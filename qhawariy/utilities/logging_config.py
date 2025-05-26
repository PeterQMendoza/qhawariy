"""
logging_config.py
Configuracion de logging, permite registrar los eventos de la aplicacio
"""


import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
import os

from qhawariy.utilities.filters import RequestCorrelationFilter


def configure_logging(app):
    """
        Configura el modulo de logs. Establece los manejadores para cada logger

        - Muestra registros en la terminal.
        - Envia errores criticos por correo.
        - Almacena eventos en un archivo de log rotativo

        :param app: Instancia de la aplicacion Flask
    """
    # Configuracion inicial
    log_dir = app.config.get("LOGS_FOLDER", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "transacciones.log")

    # Configura logging en archivo con rotacion
    file_handler = RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=5)
    file_handler.setFormatter(logging.Formatter(
        """%(asctime)s [%(levelname)s] [%(name)s:%(funcName)s:%(lineno)d] %(message)s"""
    ))
    file_handler.setLevel(logging.INFO)
    file_handler.addFilter(RequestCorrelationFilter())

    # Configura logging en consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
    # Agregar el filtro
    console_handler.addFilter(RequestCorrelationFilter())

    if app.config.get("APP_ENV") in {"local", "testing", "development"}:
        console_handler.setLevel(logging.DEBUG)
    else:
        console_handler.setLevel(logging.INFO)

    # Configuracion logging por correo si esta en modo produccion
    mail_handler = None
    if (
        app.config.get('APP_ENV') == "PRODUCTION" and
        app.config.get('MAIL_SERVER')
    ):
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr=app.config['ADMINS'],
            subject=f"[ERROR][{app.config['APP_ENV']}] la aplicacion fallo",
            credentials=(app.config['MAIL_USERNAME'], app.config['PASSWORD']),
            secure=()
        )
        mail_handler.setLevel(logging.ERROR)
        mail_handler.setFormatter(logging.Formatter(
            "[%(levelname)s] %(message)s"
        ))

    # Aplicar manejadores al logger principal de Flask
    app.logger.handlers = []
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)

    if mail_handler:
        app.logger.addHandler(mail_handler)

    app.logger.setLevel(
        logging.DEBUG if console_handler.level == logging.DEBUG else logging.INFO
    )

    app.logger.info("Logging configurado correctamente.")

    # Elimina los manejadores por defecto
    # del app.logger.handlers[:]

    # loggers = [app.logger,]
    # handlers = []

    # console_handler = logging.StreamHandler()
    # console_handler.setFormatter(verbose_formatter())

    # if (app.config['APP_ENV'] == app.config['APP_ENV_LOCAL']) or (
    #         app.config['APP_ENV'] == app.config['APP_ENV_TESTING']) or (
    #         app.config['APP_ENV'] == app.config['APP_ENV_DEVELOPMENT']):
    #     console_handler.setLevel(logging.DEBUG)
    #     handlers.append(console_handler)
    # elif app.config['APP_ENV'] == app.config['APP_ENV_PRODUCTION']:
    #     console_handler.setLevel(logging.INFO)
    #     handlers.append(console_handler)

    #     mail_handler = SMTPHandler(
    #         (
    #             app.config['MAIL_SERVER'],
    #             app.config['MAIL_PORT']
    #         ),
    #         app.config['DONT_REPLY_FROM_EMAIL'],
    #         app.config['ADMINS'],
    #         '[Error][{}] La aplicación falló'.format(app.config['APP_ENV']),
    #         (
    #             app.config['MAIL_USERNAME'],
    #             app.config['MAIL_PASSWORD']
    #         ),
    #         ()
    #     )
    #     mail_handler.setLevel(logging.ERROR)
    #     mail_handler.setFormatter(mail_handler_formatter())
    #     handlers.append(mail_handler)

    # for log in loggers:
    #     for handler in handlers:
    #         log.addHandler(handler)
    #     log.propagate = False
    #     log.setLevel(logging.DEBUG)


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
