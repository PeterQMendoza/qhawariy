
import logging
import pandas as pd
from datetime import datetime

from io import BytesIO

from flask import (Blueprint, render_template,redirect,url_for,abort,send_file)
from flask_login import (current_user, login_required)
from wsgiref.headers import Headers

from qhawariy.controllers.forms.admin_form import UserAdminForm

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
    form=UserAdminForm(obj=user)
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

@bp.route("/configuracion",methods=["GET","POST"])
@login_required
@admin_required
def configurar():
    return render_template("admin/configura.html")

