import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
# from werkzeug.urls import url_parse
from urllib.parse import urlparse

from qhawariy.controllers.decorators.auth import controlador_required
from qhawariy.controllers.forms.control_form import ControlTiempoForm
from qhawariy.models.control import Control
from qhawariy.models.control_tiempo import ControlTiempo


logger=logging.getLogger(__name__)

bp=Blueprint("control_tiempo",__name__,url_prefix="/control_tiempo")

@bp.route("/lista/<int:viaje_id>",methods=["GET","POST"])
@login_required
@controlador_required
def listar_controles_tiempos(viaje_id):
    cts=ControlTiempo.obtener_por_viaje(viaje_id)
    controles=Control.obtener_todos()
    form=ControlTiempoForm()
    form.control.choices=[(c.id_control,str(c.codigo)) for c in controles]
    if form.validate_on_submit():
        tiempo=form.tiempo.data
        control=form.control.data
        try:
            control_tiempo=ControlTiempo(tiempo=tiempo,id_control=control,id_viaje=viaje_id)
            control_tiempo.guardar()
            siguiente_pagina=request.args.get("next",None)
            if not siguiente_pagina or urlparse(siguiente_pagina).netloc!='':
                siguiente_pagina=url_for("control_tiempo.listar_controles_tiempos", viaje_id=viaje_id)
            return redirect(siguiente_pagina)
        except Exception as e:
            flash(f"Error: {e}","error")
    return render_template("viaje/lista_controles_tiempos.html",cts=cts,form=form,viaje_id=viaje_id)

@bp.route("/elimina/<int:ct_id>.<int:viaje_id>",methods=["GET","POST"])
@login_required
@controlador_required
def eliminar_control_tiempo(ct_id,viaje_id):
    ct=ControlTiempo.obtener_por_id(ct_id)
    ct.eliminar()
    return redirect(url_for("control_tiempo.listar_controles_tiempos",viaje_id=viaje_id))