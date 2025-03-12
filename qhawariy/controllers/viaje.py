import datetime
# import json
import pandas as pd
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

# from qhawariy import scheduler
from qhawariy.controllers.decorators.auth import controlador_required
from qhawariy.models.disponible_vehiculo import DisponibleVehiculo
from qhawariy.models.fecha import Fecha
from qhawariy.models.ruta import Ruta
from qhawariy.models.services.control_programa import (
    CompositePrograma,
    FlyweightFactory,
    LeafPrograma
)
from qhawariy.models.viaje import Viaje
from qhawariy.models.vehiculo import Vehiculo
from qhawariy.models.vehiculo_programado import VehiculoProgramado
from qhawariy.models.programacion import Programacion
# from qhawariy.models.timer.tareas import tarea1
from qhawariy.controllers.forms.viaje_form import ViajeForm
from qhawariy.utilities.helpers import Calendario
from qhawariy.utilities.builtins import LIMA_TZ

logger = logging.getLogger(__name__)

# Blueprint
bp = Blueprint("viaje", __name__, url_prefix="/viaje")


@bp.route("/lista", methods=["GET"])
@login_required
@controlador_required
def listar_calendario():
    ahora = datetime.datetime.now(LIMA_TZ)
    ahora.weekday()
    desde = datetime.datetime(
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
    hasta = datetime.datetime(
        year=next_year,
        month=next_month,
        day=1,
        hour=0,
        minute=0,
        second=0
    )-datetime.timedelta(days=1)
    # Las fechas no estan relacionadas con el modelo viaje
    f = Fecha.obtener_rango_fecha(ini=desde, fin=hasta)
    primer_dia = 1
    if len(f) != 0:
        primer_dia = f[0].fecha.day
    pds = desde.weekday()+1
    calendario = Calendario(ahora.year, ahora.month, f, primer_dia, pds)
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

    fecha = programa.fecha
    dv = DisponibleVehiculo.obtener_vehiculos_disponibles(fecha.fecha)
    vehiculos = []
    if dv is not None:
        for v in dv:
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
    test = None

    # obtener la programacion de vehiculos por fecha
    ahora = datetime.datetime.now(LIMA_TZ)
    ahora = ahora.replace(hour=0, minute=0, second=0, microsecond=0)

    rutas = Ruta.obtener_todos_rutas()

    # Creamos un objeto factory del servicio control_programa
    factory = FlyweightFactory()
    main = CompositePrograma(ahora.strftime("%d/%m/%Y"))

    # Creamos un diccionario para asignarle un nombre a cada
    # instancia de las clases de CompositePrograma, que representa
    # la programacion de cada una de las rutas
    programa_ruta_info = [{"ruta": ruta.codigo, "id": ruta.id_ruta} for ruta in rutas]

    programas = {}

    for programa in programa_ruta_info:
        nombre = programa["ruta"]
        programas[nombre] = CompositePrograma(str(nombre))

    # agregar un programa a la ruta actual (preferencia)
    # Secuencia de recorrido ruta:
    #   TC-34  -> TC-34A -> TC-34
    #   TC-34B -> TC-34A -> TC-34
    # ruta_id = rutas[0].id_ruta
    ruta_actual = rutas[0].codigo
    ruta_destino = rutas[1].codigo
    for r in rutas:
        if r.codigo in programas:
            # Agregar todos los vehiculos programado para esta ruta
            vp = VehiculoProgramado.vista_diaria(ahora, r.id_ruta)
            for v in vp:
                programa_1 = LeafPrograma(
                    factory,
                    str(v.vehiculo.flota),
                    v.tiempo.strftime("%H:%M:%S"),
                    ruta_destino
                )

                programas[r.codigo].add_item(programa_1)

    # agregar al nodo principal
    for key, programa in programas.items():
        main.add_item(programa)

    # data=pd.DataFrame(programas[ruta_actual])
    # Acceder a un metodo de la instancia del programa en particular
    # test=pd.DataFrame(programas[ruta_actual].display()["data"])
    # test=test.to_html()
    col_nombre = ["flota", "tiempo", "proxima ruta"]
    test = pd.DataFrame(
        programas[ruta_actual].display()[ruta_actual],
        columns=col_nombre
    )

    test = test.to_html()

    return render_template("viaje/muestra_dia.html", test=test)
