import logging
import os
import pandas as pd

from flask import (Blueprint,current_app, flash, redirect,render_template, send_from_directory,stream_template,abort, url_for,request)
from flask_login import current_user, login_required

from urllib.parse import urlparse
# from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

from qhawariy.controllers.decorators.auth import admin_required
from qhawariy.models.usuario_rol import UsuarioRol
from qhawariy.models.rol import Rol
from qhawariy.models.vehiculo import Vehiculo
from qhawariy.models.vehiculo_programado import VehiculoProgramado
from qhawariy.models.propietario_vehiculo import PropietarioVehiculo
from qhawariy.models.viaje import Viaje
from qhawariy.controllers.forms.vehiculo_form import (VehiculoForm,EditarVehiculoForm,BuscarVehiculoForm)
from qhawariy.controllers.forms.upload_file_form import UploadFileForm
from qhawariy.utilities.allowed_file import allowed_file
from qhawariy.utilities.files import FactoryExcel
from qhawariy.utilities.helpers import hacer_arbol

logger=logging.getLogger(__name__)

# Blueprint
bp=Blueprint("vehiculo",__name__,url_prefix="/vehiculo")

# Lista de vehiculos
@bp.route("/",methods=["GET","POST"])
@login_required
@admin_required
def listar_vehiculos():
    # Probar
    busqueda=Vehiculo.obtener_todos_vehiculos()
    form=BuscarVehiculoForm()
    title="Lista de todos los vehiculos registrados"
    # El filtro de busqueda
    # 0: por defecto en Placa
    # 1: por nª Flota
    # 2: Marca de vehiculo
    # 3: Modelo de vehiculo
    form.filter.choices=[(0,"Placa"),(1,"Nº flota"),(2,"Marca"),(3,"Modelo")]
    if form.validate_on_submit():
        busca=form.busca.data
        filtro=form.filter.data
        siguiente_pagina=request.args.get("next",None)
        if not siguiente_pagina or urlparse(siguiente_pagina).netloc!='':
            siguiente_pagina=url_for("vehiculo.buscar_vehiculo",buscar=busca,filtro=filtro)
        return redirect(siguiente_pagina)
    return stream_template("vehiculo/lista_vehiculo.html",vehiculos=busqueda,title=title,form=form)

@bp.route("/buscar/<string:buscar>.<int:filtro>",methods=["GET","POST"])
@login_required
@admin_required
def buscar_vehiculo(buscar,filtro):
    busqueda=None
    if filtro==0:
        busqueda=Vehiculo.busqueda_placa(buscar)
    if filtro==1:
        busqueda=Vehiculo.busqueda_flota(buscar)
    if filtro==2:
        busqueda=Vehiculo.busqueda_marca(buscar)
    if filtro==3:
        busqueda=Vehiculo.busqueda_modelo(buscar)
    
    form=BuscarVehiculoForm()
    form.filter.choices=[(0,"Placa"),(1,"Nº flota"),(2,"Marca"),(3,"Modelo")]
    title="Resultado de buscar vehiculo: {b} por {o}".format(b=buscar,o=form.filter.choices[filtro][1])
    if form.validate_on_submit():
        busca=form.busca.data
        filtro=form.filter.data
        siguiente_pagina=request.args.get("next",None)
        if not siguiente_pagina or urlparse(siguiente_pagina).netloc!='':
            siguiente_pagina=url_for("vehiculo.buscar_vehiculo",buscar=busca,filtro=filtro)
        return redirect(siguiente_pagina)
    return render_template("vehiculo/lista_vehiculo.html",vehiculos=busqueda,title=title,form=form)

@bp.route("/nuevo/",methods=["GET","POST"])
@login_required
@admin_required
def agregar_vehiculo():
    form=VehiculoForm()
    error=None
    if form.validate_on_submit():
        flota=form.flota.data
        placa=form.placa.data
        marca=form.marca.data
        modelo=form.modelo.data
        numero_asientos=form.numero_asientos.data
        fecha_fabricacion=form.fecha_fabricacion.data
        # Comprobar si el vehiculo ya se encuentra registrado
        vehiculo_placa=Vehiculo.obtener_vehiculo_por_placa(placa=placa)
        if vehiculo_placa is not None:
            error=f"El vehiculo con placa Nro {placa} ya se encuentra registrado"
        else:
            # Verficar que el propietario, conductor y ayudante esten registrados
            vehiculo=Vehiculo(flota,placa,marca,modelo,fecha_fabricacion,numero_asientos)
            vehiculo.guardar()
            siguiente_pagina=request.args.get("next",None)
            if not siguiente_pagina or urlparse(siguiente_pagina).netloc!='':
                siguiente_pagina=url_for("vehiculo.listar_vehiculos")
            return redirect(siguiente_pagina)

    #Para la seleccion en un combo box envia todos los propietarios(corregir)      
    return render_template("/vehiculo/nuevo_vehiculo.html",form=form,error=error)

@bp.route("/actualiza/<int:vehiculo_id>/",methods=["GET","POST"])
@login_required
@admin_required
def actualizar_vehiculo(vehiculo_id):
    # obtener los datos de propietarios, conductores, ayudantes de este vehiculo
    vehiculo=Vehiculo.obtener_vehiculo_por_id(vehiculo_id)

    # Actualizar vehiculo
    if vehiculo is None:
        logger.info(f"El vehiculo con id={vehiculo_id} no existe")
        abort(404)
    form=EditarVehiculoForm(obj=vehiculo)
    if form.validate_on_submit():
        vehiculo.flota=form.flota.data
        vehiculo.placa=form.placa.data
        vehiculo.marca=form.marca.data
        vehiculo.modelo=form.modelo.data
        vehiculo.numero_asientos=form.numero_asientos.data
        vehiculo.fecha_fabricacion=form.fecha_fabricacion.data
        vehiculo.activo=form.activo.data
        vehiculo.guardar()
        logger.info(f"Vehiculo actualizado {vehiculo_id} ")
        siguiente_pagina=request.args.get("next",None)
        if not siguiente_pagina or urlparse(siguiente_pagina).netloc!='':
            siguiente_pagina=url_for("vehiculo.listar_vehiculos")
        return redirect(siguiente_pagina)
    return render_template("vehiculo/edita_vehiculo.html",vehiculo=vehiculo,form=form)

@bp.route("/eliminar/<int:id_vehiculo>/",methods=["POST"])
@login_required
@admin_required
def eliminar_vehiculo(id_vehiculo):
    logger.info(f"se va ha eliminar el vehiculo {id_vehiculo}")
    vehiculo=Vehiculo.obtener_vehiculo_por_id(id_vehiculo)
    vp=VehiculoProgramado.obtener_vp_por_id_vehiculo(id_vehiculo)
    pv=PropietarioVehiculo.obtener_pv_por_id_vehiculo(id_vehiculo)
    viaje=Viaje.obtener_viaje_por_id_vehiculo(id_vehiculo)
    if vehiculo is None:
        logger.info(f"El vehiculo {id_vehiculo} no existe")
        abort(404)
    else:
        if viaje is not None:
            viaje.eliminar()
        elif pv is not None:
            pv.eliminar()
        elif vp is not None:
            vp.eliminar()
        vehiculo.eliminar()
        logger.info(f"El vehiculo {id_vehiculo} ha sido eliminado")
    return redirect(url_for("vehiculo.listar_vehiculos"))

@bp.route("/subir_archivo",methods=["GET","POST"])
@login_required
@admin_required
def cargar_archivo_vehiculos():
    form=UploadFileForm()
    path=current_app.config['UPLOAD_FOLDER']
    lista_archivos=hacer_arbol(path=path)
    if form.validate_on_submit():
        if 'file' not in request.files:
            flash('No existe el archivo')
            return redirect(request.url)
        file=request.files['file']

        if file.filename=='':
            flash('Archivo no seleccionado',"error")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename=secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'],filename))
            return redirect(url_for("vehiculo.cargar_archivo_vehiculos"))
    return render_template('vehiculo/carga_vehiculo.html',form=form,la=lista_archivos)

@bp.route("/descargar/<name>",methods=["GET","POST"])
@login_required
@admin_required
def descargar_archivo(name):
    vehiculos=Vehiculo.obtener_todos_vehiculos()
    excel=FactoryExcel()
    excel.crearArchivo(filename='lista_vehiculos',dataframe=vehiculos,tipo='lista',sheetnames=['vehiculos'],recorrido=None,date=None).guardar()
    return send_from_directory(current_app.config["DOWNLOAD_FOLDER"], name)

@bp.route("/agregar_masivo/<name>",methods=["GET","POST"])
@login_required
@admin_required
def agregar_masivo(name):
    extension = os.path.splitext(name)[1][1:]
    if extension=='xlsx':
        archivo=pd.read_excel(current_app.config["UPLOAD_FOLDER"]+"\\"+name, index_col=0)
        # vehiculo=Vehiculo()
        if 'placa' in archivo.columns and 'flota' in archivo.columns and 'marca' in archivo.columns and 'modelo' in archivo.columns and 'fecha_fabricacion' in archivo.columns and 'numero_asientos' in archivo.columns:
            for i in range(0,len(archivo)):
                    placa=Vehiculo.obtener_vehiculo_por_placa(archivo.iloc[i]['placa'])
                    fl=0
                    pl=0
                    ma=0
                    mo=0
                    ff=0
                    na=0
                    if placa is None:
                        for a in archivo.columns:
                            r=archivo.iloc[i]
                            if a=='flota':
                                flota=Vehiculo.obtener_vehiculo_por_flota(archivo.iloc[i]['flota'])
                                if flota is None:
                                    fl=r[a]
                            elif a=='placa':
                                pl=r[a]
                            elif a=='marca':
                                ma=r[a]
                            elif a=='modelo':
                                mo=r[a]
                            elif a=='fecha_fabricacion':
                                ff=r[a]
                            elif a=='numero_asientos':
                                na=r[a]

                        if fl!=0 and fl!=0 and pl!=0 and ma!=0 and mo!=0 and ff!=0 and na!=0:
                            veh=Vehiculo(fl,pl,ma,mo,ff,na)
                            veh.guardar()
        else:
            flash(f"El archivo seleccionado {name} no tiene el formato correcto",category='error')
                
    return redirect(url_for("vehiculo.listar_vehiculos"))

@bp.route("/eliminar_archivo_subido/<name>",methods=["GET","POST"])
@login_required
@admin_required
def eliminar_archivo_subido(name):
    # extension = os.path.splitext(name)[1][1:]
    filename=name
    try:
        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'],filename))
        return redirect(url_for("vehiculo.cargar_archivo_vehiculos"))
    except Exception as e:
        flash(f"Error al eliminar el archivo {e}","error")

    return redirect(url_for("vehiculo.cargar_archivo_vehiculos"))