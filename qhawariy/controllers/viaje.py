import datetime
import pandas as pd
import logging
from flask import (Blueprint, flash, redirect,render_template, url_for,request)
from flask_login import login_required

# from werkzeug.urls import url_parse
from urllib.parse import urlparse

from qhawariy import scheduler
from qhawariy.controllers.datasets.dataset_factory import DatasetControlFactory, DatasetFactory, DatasetRoute, DatasetViajeFactory
from qhawariy.controllers.decorators.auth import controlador_required
from qhawariy.models.control_tiempo import ControlTiempo
from qhawariy.models.disponible_vehiculo import DisponibleVehiculo
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

    if(ahora.month>=12):
        next_month=1
        next_year=ahora.year+1
    else:
        next_month=ahora.month+1
        next_year=ahora.year
    hasta=datetime.datetime(year=next_year,month=next_month,day=1,hour=0,minute=0,second=0)-datetime.timedelta(days=1)#Corregir para el mes de diciembre
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

    fecha=programa.fecha
    dv=DisponibleVehiculo.obtener_vehiculos_disponibles(fecha.fecha)
    vehiculos=[]
    if dv!=None:
        for v in dv:
            vehiculos.append(v.vehiculo)
    else:
        vehiculos=Vehiculo.obtener_todos_vehiculos_activos()

    rutas=Ruta.obtener_todos_rutas()
    fecha=Fecha.obtener_id(fecha_id)

    viajes=Viaje.obtener_por_fecha(fecha_id)#

    form=ViajeForm()
    form.vehiculo.choices=[(v.id_vehiculo,str(v.flota)+": "+v.placa) for v in vehiculos]
    form.ruta.choices=[(r.id_ruta,r.codigo) for r in rutas]
    if form.validate_on_submit():
        vehiculo_id=form.vehiculo.data
        ruta_f=form.ruta.data
        orden=form.orden.data
        
        ruta=Ruta.obtener_ruta_por_id(ruta_f)
        programa=Programacion.obtener_por_fecha_y_ruta(fecha_id,ruta.id_ruta)
        if programa is not None:
            # Manejo de la exception donde orden es unico para cada vehiculo
            order_unico=Viaje.obtener_orden_ruta(orden=orden,vehiculo_id=vehiculo_id,ruta_id=ruta.id_ruta)
            # Si orden_unico=None significa que no existe en BD y por lo tanto para
            # registrarlo se debe asignar como 1 al orden
            if order_unico is None:
                try:
                    conteo=Viaje.obtener_conteo_viajes_por_vehiculo(id_vehiculo=vehiculo_id)
                    viaje=Viaje(id_ruta=ruta.id_ruta,id_vehiculo=vehiculo_id,orden=orden,id_fecha=fecha_id)
                    viaje.guardar()
                    v=Vehiculo.obtener_vehiculo_por_id(vehiculo_id)
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
                flash(f"Ya existe un viaje con Nº recorrido={orden}, recomiendo utilizar el siguiente:{order_unico.orden+1}","info")
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
    # obtener la programacion de vehiculos por fecha
    ahora=datetime.datetime.now(LIMA_TZ)
    ahora=ahora.replace(hour=0,minute=0,second=0,microsecond=0)
    rutas=Ruta.obtener_todos_rutas()

    # programaciones
    programacion_ida=[]
    programacion_vuelta=[]
    programacion_vehiculos_ida=[]
    programacion_vehiculos_vuelta=[]
    
    # Viajes
    viaje_ida=[]
    viaje_vuelta=[]
    viaje_vehiculos_ida=[]
    viaje_vehiculos_vuelta=[]

    # Controles
    control_viaje_ida=[]
    control_viaje_vuelta=[]
    control_ida=[]
    control_vuelta=[]

    for r in rutas:
        vp=VehiculoProgramado.vista_diaria(ahora,r.id_ruta)
        viajes=Viaje.vista_diaria(ahora,r.id_ruta)
        controles=ControlTiempo.vista_diaria(ahora,r.id_ruta)

        if (vp==[] or viajes==[] or controles==[]):
            # Establecer una mejor informacion para el usuario
            flash(f"No existe programacion o registro de viajes para hoy {ahora}.\nTe sugiero comunicarte con el responsable de las programaciones","info")
            return render_template("viaje/muestra_dia.html",dataida='',datavuelta='')


        if r.id_ruta==1 or r.id_ruta==3:
            programacion_ida.extend(vp)
            programacion_vehiculos_ida.extend([ v.vehiculo for v in vp])

            viaje_ida.extend(viajes)
            viaje_vehiculos_ida.extend([ v.vehiculo for v in viajes])

            control_viaje_ida.extend(controles)
            control_ida.extend([c.control for c in controles])

        if r.id_ruta==2:
            programacion_vuelta.extend(vp)
            programacion_vehiculos_vuelta.extend([ v.vehiculo for v in vp])

            viaje_vuelta.extend(viajes)
            viaje_vehiculos_vuelta.extend([ v.vehiculo for v in viajes])

            control_viaje_vuelta.extend(controles)
            control_vuelta.extend([c.control for c in controles])

    # Programaciones f
    dataset=DatasetFactory()
    dts_ida=dataset.create_dataset(programacion_ida,programacion_vehiculos_ida)
    dts_ida.process_dataframe()

    dts_vuelta=dataset.create_dataset(programacion_vuelta,programacion_vehiculos_vuelta)
    dts_vuelta.process_dataframe()

    # Viajes
    dts_viaje=DatasetViajeFactory()
    dtsv_ida=dts_viaje.create_dataset(viaje_ida,viaje_vehiculos_ida)
    dtsv_ida.proccess_dataframe()

    dtsv_vuelta=dts_viaje.create_dataset(viaje_vuelta,viaje_vehiculos_vuelta)
    dtsv_vuelta.proccess_dataframe()

    # Controles
    dts_control=DatasetControlFactory()
    dtc_ida=dts_control.create_dataset(control_viaje_ida,viaje_ida,control_ida)
    dtc_ida.proccess_dataframe()

    dtc_vuelta=dts_control.create_dataset(control_viaje_vuelta,viaje_vuelta,control_vuelta)
    dtc_vuelta.proccess_dataframe()

    # fusionar odas las dataframe
    df_ida=pd.merge(dtsv_ida._dataframe,dts_ida._dataframe, on="vehiculo",how='inner')#viaje->programacion
    df_ida=pd.merge(df_ida,dtc_ida._dataframe, on="id_viaje",how='inner')#anterior->controles
    df_ida=df_ida.drop(columns=["id_viaje"])

    df_vuelta=pd.merge(dtsv_vuelta._dataframe,dts_vuelta._dataframe, on="vehiculo",how='inner')#viaje->programacion
    df_vuelta=pd.merge(df_vuelta,dtc_vuelta._dataframe, on="id_viaje",how='inner')#anterior->controles
    df_vuelta=df_vuelta.drop(columns=["id_viaje"])

    # camiar el orden de las columnas de la df de ida y de vuelta
    columnas_ida=df_ida.columns.tolist()#columnas
    icon_i=columnas_ida.index("icon")
    salida_i=columnas_ida.index("salida")
    inicio_hasta_salida_i=columnas_ida[:salida_i+1]
    salida_hasta_icon_i=columnas_ida[salida_i+1:icon_i+1]
    despues_icon_i=columnas_ida[icon_i+1:]
    df_ida=df_ida[inicio_hasta_salida_i+despues_icon_i+salida_hasta_icon_i]

    columnas_vuelta=df_vuelta.columns.tolist()#columnas
    icon_v=columnas_vuelta.index("icon")
    salida_v=columnas_vuelta.index("salida")
    inicio_hasta_salida_v=columnas_vuelta[:salida_v+1]
    salida_hasta_icon_v=columnas_vuelta[salida_v+1:icon_v]
    despues_icon_v=columnas_vuelta[icon_v+1:]
    despues_icon_v.reverse()# cambiar sentido de direccion
    df_vuelta=df_vuelta[inicio_hasta_salida_v+despues_icon_v+salida_hasta_icon_v]

    # Verificar el cumplimiento de horarios en los controles
    # conteo=0
    columnas_ida=df_ida.columns.tolist()#columnas nuevamente
    col_fr=columnas_ida.index('frecuencia')
    df_ida["diferencia"]=df_ida[columnas_ida[col_fr-1]]-df_ida[columnas_ida[col_fr-2]]
    test=columnas_ida[col_fr-2]
    
    # cambiar color del texto de diferencia
    # aux.style.apply(DatasetRoute.color_negative_red,subset=['segundos'])
    # df_ida=df_ida.style.apply(DatasetRoute.color_negative_red,color='red',subset=['diferencia'])


    df_ida_html=df_ida.to_html(classes='table text-h6',index=True,escape=False)
    df_vuelta_html=df_vuelta.to_html(classes='table text-h6',index=True,escape=False)

    return render_template("viaje/muestra_dia.html",dataida=df_ida_html,datavuelta=df_vuelta_html,test=test)
