from datetime import (
    datetime,
    timedelta,
)
# import json
import logging
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    url_for,
    request
)
from flask_login import login_required

# from werkzeug.urls import url_parse
from urllib.parse import urlparse

import pandas as pd

# from qhawariy import scheduler
from qhawariy.models.disponible_vehiculo import DisponibleVehiculo
from qhawariy.models.fecha import Fecha
from qhawariy.models.ruta import Ruta
# from qhawariy.models.secuencia_control_ruta import SecuenciaControlRuta
from qhawariy.services.auth_service.decorators import controlador_required
# from qhawariy.services.programa_service.control_programa import (
#     CompositePrograma,
#     FlyweightFactory,
#     LeafPrograma
# )
from qhawariy.models.viaje import Viaje
from qhawariy.models.control_tiempo import ControlTiempo
from qhawariy.models.vehiculo import Vehiculo
# from qhawariy.models.vehiculo_programado import VehiculoProgramado
from qhawariy.models.programacion import Programacion
# from qhawariy.models.timer.tareas import tarea1
from qhawariy.forms.viaje_form import ViajeForm
from qhawariy.services.data_service.dataframe_operacion import DataFrameBuilder
from qhawariy.utilities.helpers import Calendario
from qhawariy.utilities.builtins import LIMA_TZ
from qhawariy.utilities.helpers import convertir_DataFrame

logger = logging.getLogger(__name__)

# Blueprint
bp = Blueprint("viaje", __name__, url_prefix="/viaje")


@bp.route("/lista", methods=["GET"])
@login_required
@controlador_required
#
def listar_calendario():
    ahora = datetime.now(LIMA_TZ)
    ahora.weekday()
    desde = datetime(
        year=ahora.year,
        month=ahora.month,
        day=1,
        hour=0,
        minute=0,
        second=0
    )

    if ahora.month >= 12:
        next_month = 1
        next_year = ahora.year+1
    else:
        next_month = ahora.month+1
        next_year = ahora.year
    # Corregir para el mes de diciembre
    hasta = datetime(
        year=next_year,
        month=next_month,
        day=1,
        hour=0,
        minute=0,
        second=0
    )-timedelta(days=1)
    # Las fechas no estan relacionadas con el modelo viaje
    fecha = Fecha.obtener_rango_fecha(ini=desde, fin=hasta)
    primer_dia = 1
    if len(fecha) != 0:
        primer_dia = fecha[0].fecha.day
    pds = desde.weekday()+1
    calendario = Calendario(ahora.year, ahora.month, fecha, primer_dia, pds)
    fechas = calendario.fechas

    return render_template(
        "viaje/lista_calendario.html",
        date=fechas,
        data=ahora
    )


@bp.route("/nuevo/<int:fecha_id>", methods=["GET", "POST"])
@login_required
@controlador_required
def agregar_viaje(fecha_id):
    """
    Funcion que agrega un viaje, solo para los vehiculos que estan
    habilitados o activos. Ademas, regitra el viaje para las fechas
    que se encuentra programado. Pueden ser programados los vehiculos
    no programados anteriormente
    """
    programa = Programacion.obtener_por_fecha(fecha_id)

    fecha_programa = programa.fecha
    vehiculos_disponibles = DisponibleVehiculo.obtener_vehiculos_disponibles(
        fecha_programa.fecha
    )
    vehiculos = []
    if vehiculos_disponibles is not None:
        for v in vehiculos_disponibles:
            vehiculos.append(v.vehiculo)
    else:
        vehiculos = Vehiculo.obtener_todos_vehiculos_activos()

    rutas = Ruta.obtener_todos_rutas()
    fecha = Fecha.obtener_id(fecha_id)

    viajes = Viaje.obtener_por_fecha(fecha_id)

    form = ViajeForm()
    form.vehiculo.choices = [
        (v.id_vehiculo, str(v.flota)+": "+v.placa) for v in vehiculos
    ]
    form.ruta.choices = [(r.id_ruta, r.codigo) for r in rutas]
    if form.validate_on_submit():
        vehiculo_id = form.vehiculo.data
        ruta_f = form.ruta.data
        orden = form.orden.data

        ruta = Ruta.obtener_ruta_por_id(ruta_f)
        programa = Programacion.obtener_por_fecha_y_ruta(fecha_id, ruta.id_ruta)
        if programa is not None:
            # Manejo de la exception donde orden es unico para cada vehiculo
            order_unico = Viaje.obtener_orden_ruta(
                orden=orden,
                vehiculo_id=vehiculo_id,
                ruta_id=ruta.id_ruta
            )
            # Si orden_unico=None significa que no existe en BD y por lo tanto para
            # registrarlo se debe asignar como 1 al orden
            if order_unico is None:
                try:
                    conteo = Viaje.obtener_conteo_viajes_por_vehiculo(
                        id_vehiculo=vehiculo_id
                    )
                    viaje = Viaje(
                        id_ruta=ruta.id_ruta,
                        id_vehiculo=vehiculo_id,
                        orden=orden,
                        id_fecha=fecha_id
                    )
                    viaje.guardar()
                    v = Vehiculo.obtener_vehiculo_por_id(vehiculo_id)
                    if int(conteo[1]) < 3:
                        v.establece_programado()
                    else:
                        v.establece_espera()
                    siguiente_pagina = request.args.get("next", None)
                    if not siguiente_pagina or urlparse(siguiente_pagina).netloc != '':
                        siguiente_pagina = url_for(
                            "viaje.agregar_viaje",
                            fecha_id=fecha_id
                        )
                    return redirect(siguiente_pagina)

                except Exception as e:
                    flash(f"Error:{e}", "error")
            else:
                flash(
                    f"""Ya existe un viaje con Nº recorrido={orden}, recomiendo
                    utilizar el siguiente:{order_unico.orden+1}""",
                    "info"
                )
    return render_template(
        "viaje/lista_viaje.html",
        form=form,
        viajes=viajes,
        fecha=fecha,
        vehiculos=vehiculos
    )


@bp.route("/elimina/<int:viaje_id>.<int:fecha_id>/", methods=["GET", "POST"])
@login_required
@controlador_required
def eliminar_viaje(viaje_id, fecha_id):
    viaje = Viaje.obtener_viaje_por_id(viaje_id)
    if viaje is not None:
        viaje.eliminar()
    return redirect(url_for("viaje.agregar_viaje", fecha_id=fecha_id))


@bp.route("/controltiempo", methods=["POST", "GET"])
@login_required
@controlador_required
def mostrar_dia():
    # para mostrar en la pantalla
    # test = None

    # Establecer el tiempo de recorrido para el calculo de llegada programada
    # delta_llegada = timedelta(minutes=75)

    # obtener la programacion de vehiculos por fecha
    ahora = datetime.now(LIMA_TZ)
    ahora = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    fecha = Fecha.obtener_fecha_por_fecha(ahora)

    # rutas = Ruta.obtener_todos_rutas()

    # Creamos un objeto factory del servicio control_programa
    # factory = FlyweightFactory()
    # main = CompositePrograma(ahora.strftime("%d/%m/%Y"))

    # # Creamos un diccionario para asignarle un nombre a cada
    # # instancia de las clases de CompositePrograma, que representa
    # # la programacion de cada una de las rutas
    # programa_ruta_info = [{"ruta": ruta.codigo, "id": ruta.id_ruta} for ruta in rutas]

    # programas = {}

    # for programa in programa_ruta_info:
    #     nombre = programa["ruta"]
    #     programas[nombre] = CompositePrograma(str(nombre))

    # # agregar un programa a la ruta actual (preferencia)
    # # Secuencia de recorrido ruta:
    # #   TC-34  -> TC-34A -> TC-34
    # #   TC-34B -> TC-34A -> TC-34
    # # ruta_id = rutas[0].id_ruta
    # ruta_actual = rutas[0].codigo
    # ruta_destino = rutas[1].codigo
    # for ruta in rutas:
    #     if ruta.codigo in programas:
    #         # Agregar todos los vehiculos programado para esta ruta
    #         vp = VehiculoProgramado.vista_diaria(ahora, ruta.id_ruta)
    #         if vp and len(vp) > 0:
    #             for vehiculo_programado in vp:
    #                 # Obtener controles de acuerdo a la ruta
    #                 controles = SecuenciaControlRuta.obtener_todos_secuencia_por_ruta(
    #                     ruta.id_ruta
    #                 )
    #                 # Obtener los viajes de esta programacion
    #                 viajes = Viaje.obtener_viaje_por_fecha_id_vehiculo(
    #                     fecha.id_fecha,
    #                     vehiculo_programado.vehiculo.id_vehiculo
    #                 )
    #                 if viajes and len(viajes) > 0:
    #                     # operacion con datetime.time usando combine()
    #                     fecha_combinada = datetime.combine(
    #                         date.today(),
    #                         vehiculo_programado.tiempo
    #                     )
    #                     llegada_programada = fecha_combinada + delta_llegada
    #                     for viaje in viajes:
    #                         tiempos = [t.tiempo for t in viaje.viajes]
    #                         programa_1 = LeafPrograma(
    #                             factory,
    #                             str(vehiculo_programado.vehiculo.flota),
    #                             vehiculo_programado.tiempo,
    #                             controles,
    #                             llegada_programada,
    #                             datetime.combine(date.today(), tiempos[0]),
    #                             ruta_destino
    #                         )
    #                         llegada_programada = llegada_programada + delta_llegada

    #                         programas[ruta.codigo].add_item(programa_1)

    # # agregar al nodo principal
    # for key, programa in programas.items():
    #     main.add_item(programa)

    # # data=pd.DataFrame(programas[ruta_actual])
    # # Acceder a un metodo de la instancia del programa en particular
    # # test=pd.DataFrame(programas[ruta_actual].display()["data"])
    # # test=test.to_html()
    # col_nombre = [
    #     "flota",
    #     "salida",
    #     "control",
    #     "programada",
    #     "llegada",
    #     "proxima ruta"
    # ]
    # test = pd.DataFrame(
    #     programas[ruta_actual].display()[ruta_actual],
    #     columns=col_nombre
    # )

    # test = test.to_html()

    # --------------------------------------------------------------------------------
    # definiendo las DataFrame
    viajes = Viaje.obtener_viaje_por_fecha(fecha.id_fecha)
    vehiculos = Vehiculo.obtener_todos_vehiculos_activos()
    rutas = Ruta.obtener_todos_rutas()

    df_vehiculos = convertir_DataFrame(vehiculos)

    # Agregar los tiempos de los controles del viaje
    lista_ct: list[pd.DataFrame] = []
    for ruta in rutas:
        ct = ControlTiempo.vista_diaria(ahora, ruta.id_ruta)
        if ct and len(ct) > 0:
            df_ct = convertir_DataFrame(ct)
            lista_ct.append(df_ct)

    # Uso de servicio de data
    builder = DataFrameBuilder(df_vehiculos)
    resultado = (
        builder
        .eliminar_columna(
            [
                'marca',
                'placa',
                'modelo',
                'fecha_fabricacion',
                'numero_asientos',
                'activo',
                'estado'
            ]
        )
    )

    # Unir con viajes
    df_viajes = pd.DataFrame()
    if viajes and len(viajes) > 0:
        # Pasar datos a DataFrame
        df_viajes = convertir_DataFrame(viajes)
        resultado = (
            builder
            .unir(df_viajes, como='inner', en='id_vehiculo')
            .eliminar_columna(
                [
                    'id_vehiculo',
                    'orden'
                ]
            )
        )
    # Unir con fecha
    if fecha:
        df_fecha = convertir_DataFrame([fecha])
        resultado = (
            builder
            .unir(df_fecha, como='inner', en='id_fecha')
            .formatear_fecha(['fecha'])
            .eliminar_columna(
                [
                    'id_fecha',
                ]
            )
        )
    # Unir con rutas
    if rutas and len(rutas) > 0:
        df_rutas = convertir_DataFrame(rutas)
        resultado = (
            builder
            .unir(df_rutas, como='inner', en='id_ruta')
            .eliminar_columna(
                [
                    'id_ruta',
                    'inicio_vigencia',
                    'fin_vigencia',
                    'documento'
                ]
            )
        )

    # Unir con los controles tiempo
    resultado = None
    agregar_controles = None
    if lista_ct and len(lista_ct) > 0 and not df_viajes.empty:
        builder_controles = DataFrameBuilder(df_viajes)
        agregar_controles = (
            builder_controles
            .unir(lista_ct, como='inner', en='id_viaje')
            .eliminar_columna(
                [
                    'orden',
                    'id_vehiculo',
                    'id_ct',
                    'id_control',
                    'id_fecha',
                    'id_ruta'
                ]
            )
            .agrupar_por(['id_viaje'], {'tiempo': lambda x: x})
            .expandir_lista_a_columnas(columna='tiempo', prefijo='ctrl')
            .construir()
        )

        # Agregar columna de llegada_programada, llegada entre otros
        resultado = (
            builder
            .unir(agregar_controles, como='inner', en='id_viaje')
            .agregar_columnas({'programado': lambda x: x['ctrl_0']})
            .agregar_tiempo('programado', horas=1, minutos=15, segundos=0)
            .diferencia_tiempo('programado', 'ctrl_5', 'diferencia', formato='hh:mm')
            .eliminar_columna(
                [
                    'id_viaje'
                ]
            )
        )

    # Resultado final convierte la DF en html para ser mostrada
    resultado = (
        builder
        .formatear_html(classes="table")
        .construir()
    )

    return render_template(
        "viaje/muestra_dia.html",
        test=resultado,
        test1=agregar_controles
    )
