import logging
from typing import cast

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required  # type: ignore

from qhawariy.forms.control_form import ControlForm, ControlRutaForm
from qhawariy.models.control import Control
from qhawariy.models.ruta import Ruta
from qhawariy.models.secuencia_control_ruta import SecuenciaControlRuta
from qhawariy.utilities.decorators import admin_required
from qhawariy.utilities.redirect import redireccion_seguro


logger = logging.getLogger(__name__)
bp = Blueprint("control", __name__, url_prefix="/control")


@bp.route("/lista", methods=["GET", "POST"])
@login_required
@admin_required
def listar_controles():
    controles = Control.obtener_todos()
    secuencia = SecuenciaControlRuta.obtener_todos()
    form = ControlForm()
    if form.validate_on_submit():  # type: ignore
        codigo = cast(str, form.codigo.data)
        latitud = cast(float, form.latitud.data)
        longitud = cast(float, form.longitud.data)
        consulta = Control.obtener_por_codigo(codigo=codigo)
        if consulta:
            flash(
                f"Ya existe un punto de control registrado con codigo:{codigo}",
                "error"
            )
            redireccion_seguro("control.listar_controles")
        else:
            try:
                nuevo_control = Control(
                    codigo=codigo,
                    latitud=latitud,
                    longitud=longitud
                )
                nuevo_control.guardar()
            except Exception as e:
                flash(f"error:{e}", "error")
                redireccion_seguro("control.listar_controles")
    return render_template(
        "control/lista_control.html",
        controles=controles,
        secuencia=secuencia,
        form=form
    )


@bp.route("/eliminar/<int:control_id>", methods=["GET", "POST"])
@login_required
@admin_required
def eliminar_control(control_id: int):
    control = Control.obtener_id(control_id)
    if control:
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

    if form.validate_on_submit():  # type: ignore
        ruta_id = form.ruta.data
        control_id = form.control.data
        try:
            ultimo = SecuenciaControlRuta.obtener_secuencia_por_ruta(ruta_id)
            nueva_secuencia = (ultimo.secuencia + 1) if ultimo else 1

            secuencia = SecuenciaControlRuta(nueva_secuencia, ruta_id, control_id)
            secuencia.guardar()

        except Exception as e:
            flash(f"Ocurrio un error:{e}", "error")
            redireccion_seguro("control.listar_control_ruta")

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
    try:
        secuencia = SecuenciaControlRuta.obtener_por_id(scr_id)
        if not secuencia:
            flash("La secuencia no existe", "error")
            return redireccion_seguro("control.listar_control_ruta")

        # Obtener todas las secuencias de la misma ruta
        todos = SecuenciaControlRuta.obtener_todos_secuencia_por_ruta(secuencia.id_ruta)

        # Ajustar a las secuencias posteriores
        for sec in todos:
            if sec.secuencia > secuencia.secuencia:
                sec.secuencia -= 1
                sec.guardar()

        # eliminar secuencia de db
        secuencia.eliminar()
        flash("Secuencia eliminada correctamente", "success")
    except Exception as e:
        logger.error(f"Error al eliminar secuencia{scr_id}: {e}")
        flash("Ocurrio un error inesperado al eliminar la secuencia", "error")

    return redirect(url_for('control.listar_control_ruta'))
