import datetime
import locale
import time
import pytz
import logging
from flask import (Blueprint, app, current_app, flash, redirect,render_template,stream_template,abort, url_for,request)
from flask_login import login_required

# from werkzeug.urls import url_parse
from urllib.parse import urlparse

from qhawariy import scheduler
from qhawariy.controllers.decorators.auth import controlador_required
from qhawariy.models.fecha import Fecha
from qhawariy.models.ruta import Ruta
from qhawariy.models.viaje import Viaje
from qhawariy.models.vehiculo import Vehiculo
from qhawariy.models.vehiculo_programado import VehiculoProgramado
from qhawariy.models.programacion import Programacion
from qhawariy.models.timer.qh_timer import Flota,Reloj
# from qhawariy.models.timer.tareas import tarea1
from qhawariy.controllers.forms.viaje_form import ViajeForm
from qhawariy.utilities.helpers import Calendario
from qhawariy.utilities.builtins import LIMA_TZ

logger=logging.getLogger(__name__)

# Blueprint
bp=Blueprint("viaje",__name__,url_prefix="/viaje")

@bp.route("/lista",methods=["GET"])
@login_required
@controlador_required
def listar_calendario():
    ahora=datetime.datetime.now(LIMA_TZ)
    ahora.weekday()
    desde=datetime.datetime(year=ahora.year,month=ahora.month,day=1,hour=0,minute=0,second=0)
    hasta=datetime.datetime(year=ahora.year,month=ahora.month+1,day=1,hour=0,minute=0,second=0)-datetime.timedelta(days=1)
    f=Fecha.obtener_rango_fecha(ini=desde,fin=hasta)# las fechas no estan relacionadas con el modelo viaje
    primer_dia=1
    if len(f)!=0:
        primer_dia=f[0].fecha.day
    pds=desde.weekday()+1
    calendario=Calendario(ahora.year,ahora.month,f,primer_dia,pds)
    fechas=calendario.fechas

    return render_template("viaje/lista_calendario.html",date=fechas,data=ahora)

@bp.route("/nuevo/<int:fecha_id>",methods=["GET","POST"])
@login_required
@controlador_required
def agregar_viaje(fecha_id):
    """
    Funcion que agrega un viaje, solo para los vehiculos que estan
    habilitados o activos. Ademas, regitra el viaje para las fechas
    que se encuentra programado. Pueden ser programados los vehiculos
    no programados anteriormente
    """
    programa=Programacion.obtener_por_fecha(fecha_id)
    vp=VehiculoProgramado.obtener_todos_vp_por_programa(programa.id_programacion)
    # Establecer todos los vehiculos que tienen programacion  para hoy
    # en estado de programado
    for v in vp:
        v.vehiculo.actualizar()
    # vehiculos=Vehiculo.obtener_todos_vehiculos_programado()
    vehiculos=Vehiculo.obtener_todos_vehiculos_activos()
    rutas=Ruta.obtener_todos_rutas()
    fecha=Fecha.obtener_id(fecha_id)

    viajes=Viaje.obtener_por_fecha(fecha_id)#
    # date=datetime.datetime.now(tz=lima_tz)

    form=ViajeForm()
    # mostrar solo vehiculos activos
    form.vehiculo.choices=[(v.id_vehiculo,str(v.flota)+"-"+v.placa) for v in vehiculos]
    form.ruta.choices=[(r.id_ruta,r.codigo) for r in rutas]
    if form.validate_on_submit():
        vehiculo=form.vehiculo.data
        ruta_f=form.ruta.data
        orden=form.orden.data
        
        ruta=Ruta.obtener_ruta_por_id(ruta_f)
        programa=Programacion.obtener_por_fecha_y_ruta(fecha_id,ruta.id_ruta)
        if programa is not None:
            # Manejo de la exception donde orden=unique
            order_unico=Viaje.obtener_orden_programa(orden=orden,id_programacion=programa.id_programacion)
            if order_unico is None:
                try:
                    conteo=Viaje.obtener_conteo_viajes_por_vehiculo_programa(id_programa=programa.id_programacion,id_vehiculo=vehiculo)
                    viaje=Viaje(id_vehiculo=vehiculo,id_programacion=programa.id_programacion,orden=orden)
                    viaje.guardar()
                    v=Vehiculo.obtener_vehiculo_por_id(vehiculo)
                    if int(conteo[1])<3:
                        v.establece_programado()
                    else:
                        v.establece_espera()
                    siguiente_pagina=request.args.get("next",None)
                    if not siguiente_pagina or urlparse(siguiente_pagina).netloc!='':
                        siguiente_pagina=url_for("viaje.agregar_viaje",fecha_id=fecha_id)
                    return redirect(siguiente_pagina)

                except Exception as e:
                    flash(f"Error:{e}","error")
            else:
                flash(f"Ya existe un viaje con Nº recorrido={orden}, recomiendo utilizar el siguiente:{order_unico.orden+1}","Aviso")
    return render_template("viaje/lista_viaje.html",form=form,viajes=viajes,fecha=fecha,vehiculos=vehiculos)

@bp.route("/elimina/<int:viaje_id>.<int:fecha_id>/",methods=["GET","POST"])
@login_required
@controlador_required
def eliminar_viaje(viaje_id,fecha_id):
    viaje=Viaje.obtener_viaje_por_id(viaje_id)
    if viaje is not None:
        viaje.eliminar()
    return redirect(url_for("viaje.agregar_viaje",fecha_id=fecha_id))


@bp.route("/controltiempo",methods=["POST","GET"])
@login_required
@controlador_required
def mostrar_dia():
    time_alarma="Test"
    return render_template("viaje/muestra_dia.html",tiempo=time_alarma)

valor=0
@bp.route("/tiempo")
@login_required
@controlador_required
def intervalo_tiempo():
    global valor
    valor+=1
    return str(valor)
# @bp.route("/agrearTarea")
# @login_required
# @controlador_required
# def agregar():
#     trabajo=scheduler.add_job(
#         func=tarea1,
#         trigger="interval",
#         seconds=10,
#         id="prueba tarea1",
#         name="Trabajo de tarea1",
#         replace_existing=True
#     )
#     return "%s agregado"%trabajo.name