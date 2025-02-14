
import logging
from urllib.parse import urlparse
import pandas as pd
from datetime import datetime

from io import BytesIO

from flask import (Blueprint, render_template,redirect, request,url_for,abort,send_file)
from flask_login import (current_user, login_required)
from wsgiref.headers import Headers

from qhawariy.controllers.forms.admin_form import ConfiguracionForm, UserAdminForm

from qhawariy.models.configuracion import Configuracion
from qhawariy.models.control import Control
from qhawariy.models.ruta import Ruta
from qhawariy.models.usuario import Usuario
from qhawariy.models.usuario_rol import UsuarioRol
from qhawariy.models.rol import Rol

from qhawariy.controllers.decorators.auth import admin_required

logger=logging.getLogger(__name__)

# Blueprint
bp=Blueprint("admin",__name__,url_prefix="/admin")

# prueba para descargar
@bp.route("/download")
@login_required
@admin_required
def descargar_xls():
    users=Usuario.obtener_todos_usuarios()
    # result_dicts = [u for u in users]
    name=[]
    last_name=[]
    telefono=[]
    email=[]
    dni=[]
    for u in users:
        name.append(u.nombres)
        last_name.append(u.apellidos)
        email.append(u.correo_electronico)
        dni.append(u.dni)
        telefono.append(u.telefono)


    data=pd.DataFrame({'DNI':dni,'Nombres':name,'Apellidos':last_name,'email':email,'Telefono':telefono})
    output = BytesIO()
    writer=pd.ExcelWriter(output,engine='openpyxl')
    data.to_excel(writer,startrow=0,merge_cells = False,sheet_name="Usuarios")
    # workbook=writer.book
    # worksheet=writer.sheets["Usuario"]

    writer.close()
    output.seek(0)
    file_name='download_{}.xlsx'.format(datetime.now().strftime('%d%m%Y-%H%M'))
    return send_file(path_or_file=output, download_name=file_name, as_attachment=True)

@bp.route("/usuarios")
@login_required
@admin_required
def listar_usuarios():
    users=UsuarioRol.obtener_rol_join_usuario()

    # return render_template("auth/test.html", users=users)
    return render_template("admin/lista_usuario.html", users=users)

@bp.route("/usuario/<int:user_id>/",methods=["GET","POST"])
@login_required
@admin_required
def editar_usuario(user_id):
    # Para actualizar usuario existente
    roles=Rol.obtener_todos_roles()
    ur=UsuarioRol.obtener_por_id_usuario(user_id)
    user=ur.usuario
    rol=ur.rol
    
    if user is None:
        logger.info(f"El usuario {user_id} no existe")
        abort(404)
    form=UserAdminForm(obj=ur)
    form.rol.choices=[(r.id_rol,r.rol) for r in roles]
    if form.validate_on_submit():
        ur.id_rol=form.rol.data
        ur.guardar()
        logger.info(f"Guardando el usuario {user_id}")
        return redirect(url_for("admin.listar_usuarios"))

    return render_template("admin/edita_usuario.html",form=form,user=user,rol=rol.rol)

@bp.route("/usuario/eliminar/<int:user_id>/",methods=["POST"])
@login_required
@admin_required
def eliminar_usuario(user_id):
    logger.info(f"Se va ha eliminar al usuario {user_id}")
    user=Usuario.obtener_usuario_por_id(user_id)
    if user is None:
        logger.info(f"El usuario {user_id} no existe")
        abort(404)
    user.eliminar()
    logger.info(f"El usuario {user_id} ha sido eliminado")
    return redirect(url_for("admin.listar_usuarios"))

@bp.route("/configuracion/<int:config_id>",methods=["GET","POST"])
@login_required
@admin_required
def configurar(config_id):
    configuracion=Configuracion.obtener_config(config_id)
    # controles=Control.obtener_todos()
    # items=[(ctrl.id_control,ctrl.codigo)for ctrl in controles]
    # items.insert(0,(0,'Seleccione control'))

    if configuracion is None:
        form=ConfiguracionForm()        

        config=Configuracion()

        if form.validate_on_submit():
            tiempo_espera_vehiculo=form.tiempo_espera_vehiculo.data
            tiempo_en_recorrido=form.tiempo_total_en_recorrido.data
            horario_inicio=form.horario_inicio.data
            horario_final=form.horario_fin.data
            cantidad_vehiculo_a_programar=form.cantidad_vehiculos_a_programar.data

            config.tiempo_espera_vehiculo=tiempo_espera_vehiculo
            config.tiempo_total_en_recorrido=tiempo_en_recorrido
            config.horario_inicio=horario_inicio
            config.horario_fin=horario_final
            config.cantidad_vehiculos_a_programar=cantidad_vehiculo_a_programar

            config.guardar()

            siguiente_pagina=request.args.get("next",None)
            if not siguiente_pagina or urlparse(siguiente_pagina).netloc!='':
                siguiente_pagina=url_for("admin.configurar",config_id=1)
            return redirect(siguiente_pagina)
    else:
        form=ConfiguracionForm(obj=configuracion)
        # for subform in form.secuencia_control_ida:
        #     subform.control.choices=items

        # for subform in form.secuencia_control_vuelta:
        #     subform.control.choices=items

        if form.validate_on_submit():
            tiempo_espera_vehiculo=form.tiempo_espera_vehiculo.data
            tiempo_en_recorrido=form.tiempo_total_en_recorrido.data
            horario_inicio=form.horario_inicio.data
            horario_final=form.horario_fin.data
            cantidad_vehiculo_a_programar=form.cantidad_vehiculos_a_programar.data

            # lista_control_ida = [field.data['control'] for field in form.secuencia_control_ida]
            # lista_control_vuelta = [field.data['control'] for field in form.secuencia_control_vuelta]

            configuracion.tiempo_espera_vehiculo=tiempo_espera_vehiculo
            configuracion.tiempo_total_en_recorrido=tiempo_en_recorrido
            configuracion.horario_inicio=horario_inicio
            configuracion.horario_fin=horario_final
            configuracion.cantidad_vehiculos_a_programar=cantidad_vehiculo_a_programar

            configuracion.guardar()

            siguiente_pagina=request.args.get("next",None)
            if not siguiente_pagina or urlparse(siguiente_pagina).netloc!='':
                siguiente_pagina=url_for("admin.configurar",config_id=1)
            return redirect(siguiente_pagina)

    return render_template("admin/configura.html",form=form,confi=configuracion)

