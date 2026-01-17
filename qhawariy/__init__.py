"""
App Qhawariy: Sistema de administracion de flota vehicular
para las empresas de transporte publico de pasajeros

autor: Peter Pilen Quispe Mendoza
"""
import os
import logging

from typing import Optional, Callable, Any, Dict, cast

# from os.path import abspath,dirname,join

from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, CSRFError
# from itsdangerous import URLSafeTimedSerializer
from sqlalchemy.orm import declarative_base
from flask_assets import Environment
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_caching import Cache
from flask_cors import CORS

from flask.logging import create_logger

from flask_apscheduler import APScheduler

from werkzeug.exceptions import HTTPException

# import redis

from qhawariy.utilities.context_processors import inject_nonce
from qhawariy.utilities.filters import (
    format_datetime,
    format_time,
    is_datetime
)
from qhawariy.utilities.assets import (
    compile_stylesheet_bundles,
    compile_js_assets
)
from qhawariy.utilities.logging_config import configure_logging  # type: ignore
from qhawariy.utilities.middlewares import (
    add_correlation_id,
    add_csp_header,
    add_isolation_headers,
    assign_correlation_id,
    configurar_local,
    handle_global_error,
    log_request_start,
    add_cors_headers,
    add_security_headers,
    add_vary_cookie,
    log_request_end,
    generate_nonce,
    # csrf_protect,
    # set_csrf_cookie
)

Base = declarative_base()

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()
cache = Cache()
scheduler = APScheduler()
csrf = CSRFProtect()


# dictConfig({
#     'version': 1,
#     'formatters': {'default': {
#         'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
#     }},
#     'handlers': {'wsgi': {
#         'class': 'logging.StreamHandler',
#         'stream': 'ext://flask.logging.wsgi_errors_stream',
#         'formatter': 'default'
#     }},
#     'root': {
#         'level': 'INFO',
#         'handlers': ['wsgi']
#     }
# })


def create_app(test_config: Optional[str] = None) -> Flask:
    """
        Establece toda la configuracion necesaria para la aplicacion Flask.
        :param test_config: establece el mapeo de configuracion en el archivo
            config.py
    """
    app = Flask(__name__, instance_relative_config=True)

    # Crear un logger vinculado a la aplicacion
    logger = create_logger(app)
    logger.setLevel(logging.INFO)

    # Cargar la configuracion del folder  de la instancia
    if test_config is None:
        app.config.from_pyfile("config\\config.py")
    elif test_config == "TESTING":
        app.config.from_pyfile("Config\\testing.py")
    else:
        app.config.from_pyfile(test_config, silent=True)

    # En caso de que no exista el archivo de instancia
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Configuracion de csrf en la app
    csrf.init_app(app)  # type: ignore

    # Configuracion de CORS
    # Esta configuracion es para rutas especificas
    # Rutas que empiecen con /api/
    CORS(
        app=app,
        resources={r"/coordenadas/api/*": {"origins": "http://localost:4200"}},
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-CSRFToken"]
    )

    # Inicializa scheduler
    scheduler.init_app(app)  # type: ignore
    logging.getLogger("apscheduler").setLevel(logging.INFO)

    # Configuracion para los activos con flask_assets
    with app.app_context():
        assets = Environment()
        assets.init_app(app=app)  # type: ignore
        compile_stylesheet_bundles(assets)
        compile_js_assets(assets)

        if is_debug_mode() and not is_werkzeug_reloader_process():
            pass
        else:
            pass
            # from qhawariy.models.timer import tareas
            # scheduler.start()
    # configuracion para asignacion de memoria cache con
    # flask-caching y Redis
    # https://redis.io/docs/latest/develop/connect/clients/python/
    # redis_client=redis.Redis(host='localhost',port=6379, db=0)
    cache.init_app(  # type: ignore
        app,
        config={
            'CACHE_TYPE': "SimpleCache",
            'CACHE_DEFAULT_TIMEOUT': 80000,
            'CACHE_KEY_PREFIX': 'qhawariy'
        }
    )

    # Configuracion de Login
    login_manager.init_app(app)  # type: ignore
    login_manager.login_view = "auth.login"  # type: ignore
    login_manager.session_protection = "strong"
    login_manager.login_message_category = "info"
    login_manager.login_message = (
        u"No puedes realizar esta accion sin no has iniciado sesion"
    )
    login_manager.refresh_view = "auth.login"  # type: ignore
    login_manager.needs_refresh_message = (
        u"To protect your account, please reauthenticate to access this page."
    )
    login_manager.needs_refresh_message_category = "info"

    # Cargar la Base de Datos, Migrar datos, mail
    # MIGRATE.COMANDOS:
    #   flask db list-templates: muestra la lista de plantillas de repositorio.
    #   flask db init:Inicia la compatibilidad con la migracion de app.
    #   flask db revision: Crea un script de revision vacio.
    #   flask db migrate: El script de revision se rellena con los cambios detectados.
    #   flask db edit: Para editar el script de revision con $EDITOR.
    #   flask db upgrade: Actualiza la BD.
    #   flask db downgrade: Degrada la BD.
    #   flask db current: Muestra la revision actual de BD.
    #   flask db stamp: Establece la revision en BD en la dada como argumento, sin
    #                   realizar migracion.
    db.init_app(app)
    migrate.init_app(app, db)

    # Configuracion para envio de email
    mail.init_app(app)
    mail_settings = {
        "MAIL_USERNAME": os.environ['EMAIL_USER'],
        "MAIL_PASSWORD": os.environ['EMAIL_PASSWORD']
    }
    app.config.update(mail_settings)  # type: ignore
    # chache=Cache(app)

    # Seguridad y uso de cookies(Tambien declaradas en config)
    app.config.update(  # type: ignore
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=False,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=3600  # 1 Hora<>3600s
    )

    # Reglas
    # app.add_url_rule("/vehiculo/cargar", endpoint="/uploads", build_only=True)

    # Registro de filtros
    register_filters(app)

    # Registro de Blueprints
    register_blueprints(app)

    # Manejador de errores #analisis
    register_error_handler(app)

    # Configuracion de logs
    configure_logging(app)

    # Registro de Middlewares
    register_middlewares(app)

    # Registro de preprocesadores
    app.context_processor(inject_nonce)

    return app


def is_debug_mode():
    """Obtener estado debug de app"""
    debug = os.environ.get("FLASK_DEBUG")
    if not debug:
        return os.environ.get("FLASK_ENV") == "development"
    return debug.lower() not in ("0", "false", "no")


def is_werkzeug_reloader_process():
    """Obtener estado de werkzeug"""
    return os.environ.get("WERKZEUG_RUN_MAIN") == "true"


def register_error_handler(app: Flask):
    """
        Manejadores errores de codigo de respuestas HTTP, para ser nostrados en la
        interfaz grafica. De acuerdo a los codigos de estado y descritas de la
        siguiente manera:
        1xx: Respuestas informativas.
        2xx: Peticiones correctas.
        3xx: Redirecciones.
        4xx: Errores de cliente.
        5xx: Errores del servidor.
    """
    @app.errorhandler(500)
    def base_500_handler(error: HTTPException):  # type: ignore
        """
            Mostrada en situaciones de error ajenas a la
            naturaleza del servidor web.
        """
        return render_template("500.html"), 500

    @app.errorhandler(404)
    def error_404_handler(error: HTTPException):  # type: ignore
        """
            Mostrada en situaciones donde el servidor web no encuentra la pagina o
            recurso solicitado
        """
        return render_template("404.html"), 404

    @app.errorhandler(401)
    def error_401_handler(error: HTTPException):  # type: ignore
        """
            Mostrada en situaciones en donde la autentificacion es posible pero ha
            fallado o aun no ha sido provista
        """
        return render_template("401.html"), 401

    @app.errorhandler(CSRFError)
    def error_csrf_handler(error: HTTPException):  # type: ignore
        return jsonify({"error": "CSRF token error", "message": error.description}), 400


def register_filters(app: Flask):
    filters = cast(Dict[str, Callable[..., Any]], app.jinja_env.filters)  # type: ignore
    filters["date_time"] = format_datetime
    filters["time"] = format_time
    filters["is_datetime"] = is_datetime


def register_middlewares(app: Flask):
    """
    Registro de middleware en la aplicacion global
    """
    app.register_error_handler(Exception, handle_global_error)
    app.before_request(assign_correlation_id)
    app.before_request(log_request_start)
    app.before_request(configurar_local)
    app.before_request(generate_nonce)
    # app.before_request(csrf_protect)

    # app.after_request(set_csrf_cookie)
    app.after_request(add_correlation_id)
    app.after_request(add_cors_headers)
    app.after_request(add_security_headers)
    app.after_request(log_request_end)
    app.after_request(add_isolation_headers)
    app.after_request(add_csp_header)
    app.after_request(add_vary_cookie)

    # app.after_request(global_response_check)


# def register_context_processors(app):
#     """Registrar procesadores de contexto"""
#     app.context_processor(inject_nonce)


def register_blueprints(app: Flask):
    from qhawariy.controllers import (
        auth,
        home,
        admin,
        vehiculo,
        ruta,
        propietario,
        viaje,
        programacion,
        estadistica,
        control,
        control_tiempo,
        permiso_vehiculo,
        coordenadas,
        notificacion
    )
    # from qhawariy.models.timer import eventos
    app.register_blueprint(home.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(vehiculo.bp)
    app.register_blueprint(ruta.bp)
    app.register_blueprint(propietario.bp)
    app.register_blueprint(viaje.bp)
    app.register_blueprint(programacion.bp)
    app.register_blueprint(estadistica.bp)
    app.register_blueprint(control.bp)
    app.register_blueprint(control_tiempo.bp)
    app.register_blueprint(permiso_vehiculo.bp)
    app.register_blueprint(coordenadas.bp)
    app.register_blueprint(notificacion.bp)
