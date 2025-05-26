import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
# from werkzeug.urls import url_parse
from urllib.parse import urlparse

from qhawariy.forms.control_form import ControlTiempoForm
from qhawariy.models.control_tiempo import ControlTiempo
from qhawariy.models.secuencia_control_ruta import SecuenciaControlRuta
from qhawariy.models.viaje import Viaje
from qhawariy.utilities.decorators import controlador_required


logger = logging.getLogger(__name__)

bp = Blueprint("control_tiempo", __name__, url_prefix="/control_tiempo")


@bp.route("/lista/<int:viaje_id>", methods=["GET", "POST"])
@login_required
@controlador_required
def listar_controles_tiempos(viaje_id):
    # Para mostrar los controles de acuerdo a la secuencia
    cts = ControlTiempo.obtener_por_viaje(viaje_id)
    viaje = Viaje.obtener_viaje_por_id(viaje_id)
    controles_secuencia = SecuenciaControlRuta.obtener_todos_secuencia_por_ruta(
        viaje.id_ruta
    )
    form = ControlTiempoForm()
    form.control.choices = [
        (cs.id_control, str(cs.control.codigo)) for cs in controles_secuencia
    ]
    if form.validate_on_submit():
        tiempo = form.tiempo.data
        control = form.control.data
        try:
            control_tiempo = ControlTiempo(
                tiempo=tiempo,
                id_control=control,
                id_viaje=viaje_id
            )
            control_tiempo.guardar()
            siguiente_pagina = request.args.get("next", None)
            if not siguiente_pagina or urlparse(siguiente_pagina).netloc != '':
                siguiente_pagina = url_for(
                    "control_tiempo.listar_controles_tiempos",
                    viaje_id=viaje_id
                )
            return redirect(siguiente_pagina)
        except Exception as e:
            flash(f"Error: {e}", "error")
    return render_template(
        "viaje/lista_controles_tiempos.html",
        cts=cts,
        form=form,
        viaje_id=viaje_id
    )


@bp.route("/elimina/<int:ct_id>.<int:viaje_id>", methods=["GET", "POST"])
@login_required
@controlador_required
def eliminar_control_tiempo(ct_id, viaje_id):
    ct = ControlTiempo.obtener_por_id(ct_id)
    ct.eliminar()
    return redirect(
        url_for("control_tiempo.listar_controles_tiempos", viaje_id=viaje_id)
    )
