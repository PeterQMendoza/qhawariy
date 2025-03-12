# import datetime
# import locale
# import os
from flask import (
    Blueprint,
    render_template,
    # current_app,
    send_from_directory
)
from flask_login import current_user
# import pytz
# from qhawariy import cache
# from qhawariy.controllers.decorators.auth import admin_required

from qhawariy.models.usuario_rol import UsuarioRol

bp = Blueprint("home", __name__, url_prefix="/")


# Pantalla de inicio
@bp.route("/")
def index():
    if current_user.is_authenticated:
        id_user = current_user.id_usuario
        ur = UsuarioRol.obtener_por_id_usuario(id_user)
        rol = ur.rol
    else:
        rol = None

    return render_template("home/index.html", rol=rol)


# servir archivo de manifiesto web
@bp.route('/manifest.json')
def manifest():
    return send_from_directory('static/source/js/service/', 'manifest.json')


@bp.route('/service-worker.js')
def service_worker():
    return send_from_directory('static/source/js/service/', 'service-worker.js')
