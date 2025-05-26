import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

# from werkzeug.urls import url_parse
from urllib.parse import urlparse

from qhawariy.forms.control_form import ControlForm, ControlRutaForm
from qhawariy.models.control import Control
from qhawariy.models.ruta import Ruta
from qhawariy.models.secuencia_control_ruta import SecuenciaControlRuta
from qhawariy.utilities.decorators import admin_required


logger = logging.getLogger(__name__)
bp = Blueprint("control", __name__, url_prefix="/control")


@bp.route("/lista", methods=["GET", "POST"])
@login_required
@admin_required
def listar_controles():
    controles = Control.obtener_todos()
    secuencia = SecuenciaControlRuta.obtener_todos()
    form = ControlForm()
    if form.validate_on_submit():
        codigo = form.codigo.data
        latitud = form.latitud.data
        longitud = form.longitud.data
        consulta = Control.obtener_por_codigo(codigo=codigo)
        if consulta is None:
            try:
                control = Control(codigo=codigo, latitud=latitud, longitud=longitud)
                control.guardar()
                siguiente_pagina = request.args.get("next", None)
                if not siguiente_pagina or urlparse(siguiente_pagina).netloc != '':
                    siguiente_pagina = url_for("control.listar_controles")
                return redirect(siguiente_pagina)
            except Exception as e:
                flash(f"error:{e}", "error")
        else:
            flash(
                f"Ya existe un punto de control registrado con codigo:{codigo}",
                "error"
            )
    return render_template(
        "control/lista_control.html",
        controles=controles,
        secuencia=secuencia,
        form=form
    )


@bp.route("/eliminar/<int:control_id>", methods=["GET", "POST"])
@login_required
@admin_required
def eliminar_control(control_id):
    control = Control.obtener_id(control_id)
    if control is not None:
        control.eliminar()
    return redirect(url_for("control.listar_controles"))


@bp.route("/agregar", methods=["GET", "POST"])
@login_required
@admin_required
def listar_control_ruta():
    secuencias = SecuenciaControlRuta.obtener_todos()
    form = ControlRutaForm()
    rutas = Ruta.obtener_todos_rutas()
    controles = Control.obtener_todos()
    form.ruta.choices = [(r.id_ruta, r.codigo) for r in rutas]
    form.control.choices = [(c.id_control, c.codigo) for c in controles]

    if form.validate_on_submit():
        ruta = form.ruta.data
        control = form.control.data
        ultimo = SecuenciaControlRuta.obtener_secuencia_por_ruta(ruta)
        if ultimo:
            try:
                secuencia = SecuenciaControlRuta(ultimo.secuencia+1, ruta, control)
                secuencia.guardar()
                siguiente_pagina = request.args.get("next", None)
                if not siguiente_pagina or urlparse(siguiente_pagina).netloc != '':
                    siguiente_pagina = url_for("control.listar_control_ruta")
                return redirect(siguiente_pagina)
            except Exception as e:
                flash(f"Ocurrio un error:{e}", "error")
        else:
            try:
                secuencia = SecuenciaControlRuta(1, ruta, control)
                secuencia.guardar()
                siguiente_pagina = request.args.get("next", None)
                if not siguiente_pagina or urlparse(siguiente_pagina).netloc != '':
                    siguiente_pagina = url_for("control.listar_control_ruta")
                return redirect(siguiente_pagina)
            except Exception as e:
                flash(f"Ocurrio un error:{e}", "error")
    return render_template(
        "control/lista_control_ruta.html",
        form=form,
        secuencias=secuencias,
        rutas=rutas
    )


@bp.route("/eliminar/<int:scr_id>/", methods=["GET", "POST"])
@login_required
@admin_required
def eliminar_control_ruta(scr_id: int):
    secuencia = SecuenciaControlRuta.obtener_por_id(scr_id)
    todos = SecuenciaControlRuta.obtener_todos_secuencia_por_ruta(secuencia.id_ruta)
    if secuencia is None:
        # cambiar la secuencia de los elementos mayores siguientes
        aux = int(secuencia.secuencia)
        for sec in todos:
            if aux < sec.secuencia:
                sec.secuencia = sec.secuencia-1
                sec.guardar()
        # eliminar secuencia de db
        secuencia.eliminar()

    return redirect(url_for('control.listar_control_ruta'))
