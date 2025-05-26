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
    # return send_from_directory('static/source/js/service/', 'manifest.json')
    import os
    from flask import (
        abort,
        current_app
    )
    static_dir = os.path.join(
        current_app.root_path,
        'static',
        'source',
        'js',
        'service'
    )
    file_path = os.path.join(static_dir, 'manifest.json')
    if not os.path.exists(file_path):
        """
        Si no se encuentra dentro del directorio del proyecto
        el archivo service-worker.js se registra una advertencia
        """
        current_app.logger.warning("Advertencia archivo no encontrado: %s", file_path)
        abort(404, description="Archivo manifest.json no encontrado.")

    response = send_from_directory(
        static_dir,
        'manifest.json',
        mimetype='application/javascript',
        cache_timeout=0
    )
    response.headers['Cache-Control'] = (
        'no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0'
    )
    return response


@bp.route('/service-worker.js')
def service_worker():
    import os
    from flask import (
        abort,
        current_app
    )
    static_dir = os.path.join(
        current_app.root_path,
        'static',
        'source',
        'js',
        'service'
    )
    file_path = os.path.join(static_dir, 'service-worker.js')

    if not os.path.exists(file_path):
        """
        Si no se encuentra dentro del directorio del proyecto
        el archivo service-worker.js se registra una advertencia
        """
        current_app.logger.warning("Archivo no encontrado: %s", file_path)
        abort(404, description="Archivo service-worker.js no encontrado.")

    response = send_from_directory(
        static_dir,
        'service-worker.js',
        mimetype='application/javascript'
    )
    response.headers['Cache-Control'] = (
        'no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0'
    )
    return response
