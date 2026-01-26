import datetime
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for
)
from flask_login import login_required  # type: ignore

from qhawariy.forms.permiso_form import (
    AgregaPermisoForm,
    BuscaPermisoForm
)
from qhawariy.models.disponible_vehiculo import DisponibleVehiculo
from qhawariy.models.vehiculo import Vehiculo
from qhawariy.utilities.builtins import LIMA_TZ
from qhawariy.utilities.decorators import operacion_required


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
    busqueda: Optional[List["DisponibleVehiculo"]] = None
    vehiculos: List[Dict[str, Any]] = []

    if busca == 'todos':
        # Para mostrar todos los vehiculos activos con su cronograma
        busqueda = DisponibleVehiculo.obtener_todos()
        lista = Vehiculo.obtener_todos_vehiculos_activos()
        vehiculos = [
            {"id": v.id_vehiculo, "name": f"Flota {v.flota}"} for v in lista
        ]
    elif busca.isdigit():
        # Solo un vehiculo por flota
        flota_id = int(busca)
        busqueda = DisponibleVehiculo.busca_vehiculo_flota(flota_id)
        v = Vehiculo.obtener_vehiculo_por_flota(flota_id)
        if v:
            vehiculos = [
                {"id": v.id_vehiculo, "name": "Flota "+str(v)}
            ]

    # Construccion de permisos
    permisos: List[Dict[str, Any]]
    if busqueda:
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
    else:
        permisos = [{}]

    form_busca = BuscaPermisoForm()
    titulo = f"Cronograma de permisos para {busca}"
    if form_busca.validate_on_submit():  # type: ignore
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
    # Obtener vehiculos activos
    vehiculos = Vehiculo.obtener_todos_vehiculos_activos()

    form_agrega = AgregaPermisoForm()
    form_agrega.id_vehiculo.choices = [
        (v.id_vehiculo, f"{v.flota}: {v.placa}") for v in vehiculos
    ]

    if form_agrega.validate_on_submit():  # type: ignore
        id_ve = form_agrega.id_vehiculo.data
        fecha_inicio = datetime.datetime.combine(
            form_agrega.fecha_inicio.data,  # type: ignore
            datetime.time.min
        )
        fecha_final = datetime.datetime.combine(
            form_agrega.fecha_final.data,  # type: ignore
            datetime.time.min
        )

        try:
            # Validacion personalizada
            form_agrega.validate_fecha_menor(form_agrega.fecha_final)
            nuevo_disponible = DisponibleVehiculo(
                fecha_inicio,
                fecha_final,
                id_ve
            )
            nuevo_disponible.guardar()
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
def eliminar_permiso(permiso_id: int):
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
