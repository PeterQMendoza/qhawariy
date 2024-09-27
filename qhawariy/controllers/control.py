import logging

from flask import Blueprint, flash, redirect, render_template, request, stream_template, url_for
from flask_login import login_required

# from werkzeug.urls import url_parse
from urllib.parse import urlparse

from qhawariy.controllers.decorators.auth import admin_required
from qhawariy.controllers.forms.control_form import ControlForm
from qhawariy.models.control import Control


logger=logging.getLogger(__name__)
bp=Blueprint("control",__name__,url_prefix="/control")

@bp.route("/lista",methods=["GET","POST"])
@login_required
@admin_required
def listar_controles():
    controles=Control.obtener_todos()
    form=ControlForm()
    if form.validate_on_submit():
        codigo=form.codigo.data
        latitud=form.latitud.data
        longitud=form.longitud.data
        consulta=Control.obtener_por_codigo(codigo=codigo)
        if consulta is None:
            try:
                control=Control(codigo=codigo,latitud=latitud,longitud=longitud)
                control.guardar()
                siguiente_pagina=request.args.get("next",None)
                if not siguiente_pagina or urlparse(siguiente_pagina).netloc!='':
                    siguiente_pagina=url_for("control.listar_controles")
                return redirect(siguiente_pagina)
            except Exception as e:
                flash(f"error:{e}","error")
        else:
            flash(f"Ya existe un punto de control registrado con codigo:{codigo}","error")
    return render_template("control/lista_control.html",controles=controles,form=form)


@bp.route("/eliminar/<int:control_id>",methods=["GET","POST"])
@login_required
@admin_required
def eliminar_control(control_id):
    control=Control.obtener_id(control_id)
    if control is not None:
        control.eliminar()
    return redirect(url_for("control.listar_controles"))

