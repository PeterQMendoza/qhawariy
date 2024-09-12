# @file auth.py
import logging

from smtplib import SMTPException
from threading import Thread
from functools import wraps

from flask import (current_app,abort)
from flask_login import current_user
from flask_mail import Message

from qhawariy import mail
from qhawariy.models.usuario_rol import UsuarioRol
from qhawariy.models.rol import Rol

# Configuracion para envio de email de confirmacion
logger=logging.getLogger(__name__)
def send_async_email(app,msg):
    with app.app_context():
        try:
            mail.send(msg)
        except SMTPException:
            logger.exception("Ocurrio un problema al enviar el email")
def send_email(subject,sender,recipients,text_body,cc=None,bcc=None,html_body=None):
    msg=Message(subject,sender=sender,recipients=recipients,cc=cc,bcc=bcc)
    msg.body=text_body
    if html_body:
        msg.html=html_body
    Thread(target=send_async_email,args=(current_app._get_current_object(),msg)).start()

# Decoradores usados para estblecer nivel de acceso por roles al sistema
def admin_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        id_user=current_user.id_usuario
        ur=UsuarioRol.obtener_por_id_usuario(id_user)
        rol=ur.rol
        is_admin=getattr(rol,"rol",False)
        if is_admin!='Administrador':
            abort(401)
        return f(*args,**kwargs)
    return decorated_function

def operacion_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        id_user=current_user.id_usuario
        ur=UsuarioRol.obtener_por_id_usuario(id_user)
        rol=ur.rol
        is_operaciones=getattr(rol,"rol",False)
        if is_operaciones!='Operacion':
            abort(401)
        return f(*args,**kwargs)
    return decorated_function

def controlador_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        id_user=current_user.id_usuario
        ur=UsuarioRol.obtener_por_id_usuario(id_user)
        rol=ur.rol
        is_controlador=getattr(rol,"rol",False)
        if is_controlador!='Controlador':
            abort(401)
        return f(*args,**kwargs)
    return decorated_function
