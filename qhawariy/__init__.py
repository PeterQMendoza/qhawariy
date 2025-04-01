"""
App Qhawariy: Sistema de administracion de flota vehicular
para las empresas de transporte publico de pasajeros

autor: Peter Pilen Quispe Mendoza
"""
import locale
import os
import logging

# from os.path import abspath,dirname,join
from logging.handlers import SMTPHandler
from logging.config import dictConfig

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
# from itsdangerous import URLSafeTimedSerializer
from sqlalchemy.orm import declarative_base
from flask_assets import Environment
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_caching import Cache

from flask_apscheduler import APScheduler

# import redis

from qhawariy.utilities.filters import (
    format_datetime,
    format_time,
    is_datetime
)
from qhawariy.utilities.assets import (
    compile_stylesheet_bundles,
    compile_js_assets
)

Base = declarative_base()

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()
csrf = CSRFProtect()
cache = Cache()
scheduler = APScheduler()


dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


def create_app(test_config=None):
    """
        Establece toda la configuracion necesaria para la aplicacion Flask.
        :param test_config: establece el mapeo de configuracion en el archivo
            config.py
    """
    app = Flask(__name__, instance_relative_config=True)

    # Configurarel locale
    @app.before_request
    def configurar_local():
        # Configurar locale para es_PE.UTF-8 (Per'u)
        locale_str = 'es_PE.UTF-8'
        try:
            locale.setlocale(locale.LC_ALL, locale_str)
        except locale.Error:
            app.logger.error("Locale 'es_PE.UTF-8' no esta disponible en este sistema")

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

    # Configuracion de logs
    configure_logging(app)

    # Configuracion de csrf
    csrf.init_app(app)

    # Inicializa scheduler
    scheduler.init_app(app)
    logging.getLogger("apscheduler").setLevel(logging.INFO)
    # Configuracion para los activos con flask_assets
    with app.app_context():
        assets = Environment()
        assets.init_app(app=app)
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
    cache.init_app(
        app,
        config={
            'CACHE_TYPE': "SimpleCache",
            'CACHE_DEFAULT_TIMEOUT': 80000,
            'CACHE_KEY_PREFIX': 'qhawariy'
        }
    )

    # Configuracion de Login
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.session_protection = "strong"
    login_manager.login_message_category = "info"
    login_manager.login_message = (
        u"No puedes realizar esta accion sin no has iniciado sesion"
    )
    login_manager.refresh_view = "auth.login"
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
    app.config.update(mail_settings)
    # chache=Cache(app)

    # Registro de filtros
    register_filters(app)

    # Seguridad y uso de cookies(Tambien declaradas en config)
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=False,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=3600  # 1 Hora<>3600s
    )

    # Reglas
    # app.add_url_rule("/vehiculo/cargar", endpoint="/uploads", build_only=True)

    # Ejecutar antes de cada solicitud

    # Registro de Blueprints
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

    # Manejador de errores #analisis
    register_error_handler(app)

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


def register_error_handler(app):
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
    def base_500_handler(e):
        """
            Mostrada en situaciones de error ajenas a la
            naturaleza del servidor web.
        """
        return render_template("500.html"), 500

    @app.errorhandler(404)
    def error_404_handler(e):
        """
            Mostrada en situaciones donde el servidor web no encuentra la pagina o
            recurso solicitado
        """
        return render_template("404.html"), 404

    @app.errorhandler(401)
    def error_401_handler(e):
        """
            Mostrada en situaciones en donde la autentificacion es posible pero ha
            fallado o aun no ha sido provista
        """
        return render_template("401.html"), 401


def register_filters(app):
    app.jinja_env.filters["date_time"] = format_datetime
    app.jinja_env.filters["time"] = format_time
    app.jinja_env.filters["is_datetime"] = is_datetime


def configure_logging(app):
    """
        Configura el modulo de logs. Establece los manejadores para cada logger
        :param app: Instancia de la aplicacion Flask
    """
    # Elimina los manejadores por defecto
    del app.logger.handlers[:]

    loggers = [app.logger,]
    handlers = []

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(verbose_formatter())

    if (app.config['APP_ENV'] == app.config['APP_ENV_LOCAL']) or (
            app.config['APP_ENV'] == app.config['APP_ENV_TESTING']) or (
            app.config['APP_ENV'] == app.config['APP_ENV_DEVELOPMENT']):
        console_handler.setLevel(logging.DEBUG)
        handlers.append(console_handler)
    elif app.config['APP_ENV'] == app.config['APP_ENV_PRODUCTION']:
        console_handler.setLevel(logging.INFO)
        handlers.append(console_handler)

        mail_handler = SMTPHandler(
            (
                app.config['MAIL_SERVER'],
                app.config['MAIL_PORT']
            ),
            app.config['DONT_REPLY_FROM_EMAIL'],
            app.config['ADMINS'],
            '[Error][{}] La aplicación falló'.format(app.config['APP_ENV']),
            (
                app.config['MAIL_USERNAME'],
                app.config['MAIL_PASSWORD']
            ),
            ()
        )
        mail_handler.setLevel(logging.ERROR)
        mail_handler.setFormatter(mail_handler_formatter())
        handlers.append(mail_handler)

    for log in loggers:
        for handler in handlers:
            log.addHandler(handler)
        log.propagate = False
        log.setLevel(logging.DEBUG)


def mail_handler_formatter():
    return logging.Formatter(
        '''
            Message type:       %(levelname)s
            Location:           %(pathname)s:%(lineno)d
            Module:             %(module)s
            Function:           %(funcName)s
            Time:               %(asctime)s.%(msecs)d

            Message:

            %(message)s
        ''',
        datefmt="%d/%m/%Y %H:%M:%S"
    )


def verbose_formatter():
    return logging.Formatter(
        """[%(asctime)s.%(msecs)d]\t %(levelname)s \t[%(name)s.%(funcName)s:%(lineno)d]
        \t %(message)s""",
        datefmt="%d/%m/%Y %H:%M:%S"
    )
