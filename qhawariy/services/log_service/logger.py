import logging


def registrar_evento(tipo: str, mensaje: str):
    """
    Registra eventos con diferentes niveles de gravedad

    Parametros:
        tipo: nivel de gravedad
        mensaje: Informacion util para resolverlo
    """
    niveles = {
        "DEBUG": logging.debug,
        "INFO": logging.info,
        "WARNING": logging.warning,
        "ERROR": logging.error,
        "CRITAL": logging.critical
    }
    log_function = niveles.get(tipo.upper(), logging.info)
    log_function(mensaje)
