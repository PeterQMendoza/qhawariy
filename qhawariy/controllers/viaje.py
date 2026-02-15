from datetime import (
    datetime,
    timedelta,
)
# import json
import logging
from typing import List, Optional, cast
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    url_for
)
from flask_login import login_required  # type: ignore

import pandas as pd

# from qhawariy import scheduler
from qhawariy.models.disponible_vehiculo import DisponibleVehiculo
from qhawariy.models.fecha import Fecha
from qhawariy.models.ruta import Ruta
# from qhawariy.models.secuencia_control_ruta import SecuenciaControlRuta
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
from qhawariy.services.data_service.dataframe_operacion import (
    DataFrameBuilder,
    SalidaFilaEstrategia,
    SalidaHtmlEstrategia
)
from qhawariy.utilities.decorators import controlador_required
from qhawariy.utilities.helpers import Calendario, validar_dataframe
from qhawariy.utilities.builtins import LIMA_TZ
from qhawariy.utilities.helpers import convertir_DataFrame
from qhawariy.utilities.redirect import redireccion_seguro

logger = logging.getLogger(__name__)

# Blueprint
bp = Blueprint("viaje", __name__, url_prefix="/viaje")


@bp.route("/lista", methods=["GET"])
@login_required
@controlador_required
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
def agregar_viaje(fecha_id: int):
    """
    Agrega un viaje, solo para los vehiculos que estan
    habilitados o activos. Ademas, regitra el viaje para las fechas
    que se encuentra programado. Pueden ser programados los vehiculos
    no programados anteriormente
    """
    programa = Programacion.obtener_por_fecha(fecha_id)
    fecha_programa: Optional[Fecha] = None
    vehiculos_disponibles: List[DisponibleVehiculo] = []
    if not programa:
        flash("No existe programacion para fecha indicada", "error")
        return redireccion_seguro("viaje.lista_viaje", fecha_id=fecha_id)

    fecha_programa = cast(Fecha, programa.fecha)
    vehiculos_disponibles = DisponibleVehiculo.obtener_vehiculos_disponibles(
        fecha_programa.fecha
    )

    vehiculos: List['Vehiculo'] = (
        [v.vehiculo for v in vehiculos_disponibles]
        if vehiculos_disponibles else Vehiculo.obtener_todos_vehiculos_activos()
    )  # type: ignore

    rutas = Ruta.obtener_todos_rutas()
    fecha = Fecha.obtener_id(fecha_id)
    viajes = Viaje.obtener_por_fecha(fecha_id)

    form = ViajeForm()
    form.vehiculo.choices = [
        (v.id_vehiculo, f"{v.flota}: {v.placa}") for v in vehiculos
    ]
    form.ruta.choices = [(r.id_ruta, r.codigo) for r in rutas]

    if form.validate_on_submit():  # type: ignore
        vehiculo_id = form.vehiculo.data
        ruta_id = form.ruta.data
        orden = cast(int, form.orden.data)

        ruta = Ruta.obtener_ruta_por_id(ruta_id)
        if not ruta:
            flash("Ruta no encontrada", "error")
            return redireccion_seguro("viaje.agregar_viaje", fecha_id=fecha_id)

        programa_ruta = Programacion.obtener_por_fecha_y_ruta(
            fecha_id, ruta.id_ruta
        )
        if not programa_ruta:
            flash("No existe programacion para la ruta indicada", "error")
            return redireccion_seguro("viaje.agregar_viaje", fecha_id=fecha_id)

        # Manejo de la exception donde orden es unico para cada vehiculo
        order_unico = Viaje.obtener_orden_ruta(
            orden=orden,
            vehiculo_id=vehiculo_id,
            ruta_id=ruta.id_ruta
        )
        # Si orden_unico=None significa que no existe en BD y por lo tanto para
        # registrarlo se debe asignar como 1 al orden
        if order_unico:
            flash(
                f"""Ya existe un viaje con Nº recorrido={orden}, recomiendo
                utilizar el siguiente:{order_unico.orden+1}""",
                "info"
            )
            return redireccion_seguro("viaje.agregar_viaje", fecha_id=fecha_id)

        try:
            viaje = Viaje(
                id_ruta=ruta.id_ruta,
                id_vehiculo=vehiculo_id,
                orden=orden,
                id_fecha=fecha_id
            )
            viaje.guardar()

            conteo = Viaje.obtener_conteo_viajes_por_vehiculo(
                id_vehiculo=vehiculo_id
            )
            v = Vehiculo.obtener_vehiculo_por_id(vehiculo_id)
            if not v:
                flash(
                    f"No se encontro el vehiculo con id {vehiculo_id}",
                    "error"
                )
            elif conteo and int(conteo[1]) < 3:
                v.establece_programado()
            else:
                v.establece_espera()

            return redireccion_seguro("viaje.agregar_viaje", fecha_id=fecha_id)

        except Exception as e:
            flash(f"Error al guardar viaje: {e}", "error")

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
def eliminar_viaje(viaje_id: int, fecha_id: int):
    viaje = Viaje.obtener_viaje_por_id(viaje_id)
    if viaje is not None:
        viaje.eliminar()
    return redirect(url_for("viaje.agregar_viaje", fecha_id=fecha_id))


@bp.route("/controltiempo", methods=["POST", "GET"])
@login_required
@controlador_required
def mostrar_dia():
    # Normalizar fecha actual en la zona horaria Lima
    ahora = datetime.now(LIMA_TZ)
    # Obtiene la fecha actual
    ahora = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    fecha = Fecha.obtener_fecha_por_fecha(ahora)
    if not fecha:
        flash("No existe fecha programada", "error")
        return redireccion_seguro("viaje.mostrar_dia")

    # Datos base
    viajes = Viaje.obtener_viaje_por_fecha(fecha.id_fecha)
    vehiculos = Vehiculo.obtener_todos_vehiculos_activos()
    rutas = Ruta.obtener_todos_rutas()

    # Validacion de DataFrames
    df_vehiculos = validar_dataframe("vehiculo", vehiculos, True)
    df_fecha = validar_dataframe("fecha", [fecha], True)
    df_viajes = validar_dataframe("viajes", viajes, True)
    df_rutas = validar_dataframe("rutas", rutas, True)

    # DataFrame inicial de vehiculos
    builder = DataFrameBuilder(df_vehiculos)
    if not df_vehiculos.empty:
        builder = (
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
    if not df_viajes.empty:
        # Pasar datos a DataFrame
        builder = builder.unir(
            df_viajes,
            como='inner',
            en='id_vehiculo'
        ).eliminar_columna(
            [
                'id_vehiculo',
                'orden'
            ]
        )
    # Unir con fecha
    if not df_fecha.empty and not df_viajes.empty:
        builder = (
            builder
            .unir(
                df_fecha,
                como='inner',
                en='id_fecha'
            )
            .eliminar_columna(
                [
                    'id_fecha',
                    'fecha'
                ]
            )
        )
    # Unir con rutas
    if not df_rutas.empty and not df_viajes.empty:
        builder = (
            builder
            .unir(
                df_rutas,
                como='inner',
                en='id_ruta'
            )
            .eliminar_columna(
                [
                    'id_ruta',
                    'inicio_vigencia',
                    'fin_vigencia',
                    'documento'
                ]
            )
        )

    # Agregar los tiempos de los controles del viaje
    if not df_rutas.empty and not df_viajes.empty:
        agregar_controles = None
        lista_ct: list[pd.DataFrame] = []
        for ruta in rutas:
            ct = ControlTiempo.vista_diaria(ahora, ruta.id_ruta)
            if ct:
                df_ct = convertir_DataFrame(ct)
                lista_ct.append(df_ct)

        # Unir con los controles tiempo
        builder_controles = DataFrameBuilder(df_viajes)
        agregar_controles = pd.DataFrame()
        if lista_ct:
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
                .agrupar_por(['id_viaje'], {'tiempo': lambda x: x})  # type: ignore
                .expandir_lista_a_columnas(columna='tiempo', prefijo='control')
                .construir()
            )

            # Agregar columna de llegada_programada, llegada entre otros
            builder = (
                builder
                .unir(agregar_controles, como='inner', en='id_viaje')
                .eliminar_columna(
                    [
                        'id_viaje'
                    ]
                )
                # Agrega columna, llamado 'programado', con los datos de la
                # columna 'control 1'
                .agregar_columnas({'programado': lambda x: x['control 1']})
                # Ordener de acuerdo a la salida
                .ordenar_por("control 1", True)
                # Aumenta tiempo de 'control 1' en 1h:15m:0s<>75min (timedelta)
                .agregar_tiempo('programado', horas=1, minutos=15, segundos=52)
                # Agrega una columna 'Diferencia' y calcula la diferencia entre
                # la columna 'programado' y 'control 4'
                .diferencia_tiempo(
                    'programado',
                    'control 4',
                    'diferencia'
                )
                # Calcula el promedio entre filas, registro de viaje anterior y actual
                .promediar_diferencia(
                    "diferencia",
                    "promedio"
                )
            )

    builder.formato_tiempo(
        'programado',
        "hh:mm:ss"
    )
    builder.cambiar_color_tiempo_condicional(
        # Estalece una condicion a la columna diferencia y cambia el color de
        # texto si la cumple
        condicion=(
            lambda x: isinstance(x, pd.Timedelta)
            and x.total_seconds() < -60
        ),
        color_positivo='#05BE50DE',
        color_negativo='#EB0046',
        columnas=['diferencia', 'promedio']
    )
    # Resultado final convierte la DF en html para ser mostrada
    builder.formatear_html(
        classes="table",
        escape=False
    )
    df_operativo = builder.construir(SalidaFilaEstrategia())
    salida_html = builder.construir(
        SalidaHtmlEstrategia(builder.operaciones_formato)
    )

    return render_template(
        "viaje/muestra_dia.html",
        test=salida_html,
        test1=df_operativo[['diferencia', 'promedio']]
    )
