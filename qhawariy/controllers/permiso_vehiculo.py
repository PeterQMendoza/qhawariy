import datetime
import logging
from urllib.parse import urlparse

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for
)
from flask_login import login_required

from qhawariy.services.auth_service.decorators import operacion_required
from qhawariy.forms.permiso_form import (
    AgregaPermisoForm,
    BuscaPermisoForm
)
from qhawariy.models.disponible_vehiculo import DisponibleVehiculo
from qhawariy.models.vehiculo import Vehiculo
from qhawariy.utilities.builtins import LIMA_TZ


logger = logging.getLogger(__name__)

# Blueprint
bp = Blueprint("cronograma_vehiculos", __name__, url_prefix="/cronograma_vehiculos")


@bp.route("/<string:busca>", methods=["GET", "POST"])
@login_required
@operacion_required
def mostrar_cronograma(busca: str):
    ahora = datetime.datetime.now(tz=LIMA_TZ)

    fecha = {'month': ahora.month, 'year': ahora.year}

    # Si el filtro es vacio entonces mostrar solo el vehiculo
    busqueda = None
    vehiculos = []

    if busca == 'todos':
        # Para mostrar todos los vehiculos activos con su cronograma
        busqueda = DisponibleVehiculo.obtener_todos()
        lista = Vehiculo.obtener_todos_vehiculos_activos()
        vehiculos = [
            {"id": v.id_vehiculo, "name": "Flota "+str(v.flota)} for v in lista
        ]
    else:
        # En la busqueda solo se debe mostrar el vehiculo con su cronograma
        if busca.isdigit():
            busqueda = DisponibleVehiculo.busca_vehiculo_flota(busca)
            lista = [Vehiculo.obtener_vehiculo_por_flota(busca)]
            vehiculos = [
                {"id": v.id_vehiculo, "name": "Flota "+str(v.flota)} for v in lista
            ]

    try:
        permisos = [
            {
                'id': p.id_dv,
                'start': p.fecha_inicio.strftime("%Y-%m-%d %H:%M:%S"),
                'end': p.fecha_final.strftime("%Y-%m-%d %H:%M:%S"),
                'task': p.id_vehiculo
            } for p in busqueda
        ]
    except Exception:
        permisos = [{}]

    form_busca = BuscaPermisoForm()
    titulo = f"Cronograma de permisos para {busca}"
    if form_busca.validate_on_submit():
        buscar = form_busca.busca.data

        siguiente_pagina = request.args.get("next", None)
        if not siguiente_pagina or urlparse(siguiente_pagina).netloc != '':
            siguiente_pagina = url_for(
                "cronograma_vehiculos.mostrar_cronograma",
                busca=buscar
            )
        return redirect(siguiente_pagina)

    return render_template(
        "/permiso/cronograma.html",
        form_busca=form_busca,
        titulo=titulo,
        permisos=permisos,
        date=fecha,
        vehiculos=vehiculos
    )


@bp.route("/agrega_actividad", methods=["GET", "POST"])
@login_required
@operacion_required
def agregar_permiso():

    vehiculos = Vehiculo.obtener_todos_vehiculos_activos()

    form_agrega = AgregaPermisoForm()
    form_agrega.id_vehiculo.choices = [
        (v.id_vehiculo, str(v.flota)+": "+str(v.placa)) for v in vehiculos
    ]

    if form_agrega.validate_on_submit():
        id_ve = form_agrega.id_vehiculo.data
        fecha_inicio = form_agrega.fecha_inicio.data
        fecha_final = form_agrega.fecha_final.data

        try:
            form_agrega.validate_fecha_menor(form_agrega.fecha_final)
            newDiponibleVehiculo = DisponibleVehiculo(
                fecha_inicio,
                fecha_final,
                id_ve
            )
            newDiponibleVehiculo.guardar()
            # Para un mejor redireccionamiento
            siguiente_pagina = request.args.get("next", None)
        except Exception as e:
            flash(f"Error:{e}", "error")
            siguiente_pagina = url_for("cronograma_vehiculos.agregar_permiso")

        if not siguiente_pagina or urlparse(siguiente_pagina).netloc != '':
            siguiente_pagina = url_for(
                "cronograma_vehiculos.mostrar_cronograma",
                busca='todos'
            )
        return redirect(siguiente_pagina)
    return render_template("permiso/agrega_permiso.html", form_agrega=form_agrega)


#
@bp.route("/eliminar/<int:permiso_id>", methods=["GET"])
@login_required
@operacion_required
def eliminar_permiso(permiso_id):
    permiso = DisponibleVehiculo.obtener_id(permiso_id)
    if permiso is not None:
        permiso.eliminar()
        siguiente_pagina = request.args.get("next", None)
        if not siguiente_pagina or urlparse(siguiente_pagina).netloc != '':
            siguiente_pagina = url_for(
                "cronograma_vehiculos.mostrar_cronograma",
                busca='todos'
            )
        return redirect(siguiente_pagina)

    return redirect(url_for("cronograma_vehiculos.mostrar_cronograma", busca='todos'))
