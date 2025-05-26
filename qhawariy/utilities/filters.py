from datetime import datetime
import logging

from flask import g, has_request_context


def format_datetime(value: datetime, format="short"):
    """Filtro que transforma un datetime en str con formato.

    El filtro es para ser usado en plantillas JINJA2.
    Los formatos posibles son los siguientes:
    * short: dd/mm/aaaa
    * full: dd de mm de aaaa
    * year: aaaa

    :param datetime value: Fecha a ser transformada.
    :param format: Formato con el que mostrar la fecha. Valores posibles: short y full.
    :return: Un string con formato de la fecha.
    """
    value_str = None
    if not value:
        value_str = ""
    if format == "short":
        value_str = value.strftime("%d/%m/%Y")
    elif format == "full":
        value_str = value.strftime("%d %b, %Y - %I:%M %p")
    elif format == "full_peru":
        value_str = value.strftime("%I:%M %p, %B %d, %Y")
    elif format == "date":
        value_str = value.strftime("%A %d de %B de %Y")
    elif format == "year":
        value_str = value.strftime("%Y")
    elif format == "month_year":
        value_str = value.strftime("%B de %Y")
    elif format == "day":
        value_str = value.strftime("%d")
    elif format == "dayweek":
        value_str = value.strftime("%a")
    else:
        value_str = ""

    # Traducir el mes al español
    # meses_espanol = {
    #     "January": "Enero",
    #     "February": "Febrero",
    #     "March": "Marzo",
    #     "April": "Abril",
    #     "May": "Mayo",
    #     "June": "Junio",
    #     "July": "Julio",
    #     "August": "Agosto",
    #     "September": "Septiembre",
    #     "October": "Octubre",
    #     "November": "Noviembre",
    #     "December": "Diciembre"
    # }

    # value_str = value_str.replace(
    #     value.strftime("%B"),
    #     meses_espanol[value.strftime("%B")]
    # )

    return value_str


def format_time(value, format='short'):
    value_str = None
    if not value:
        value_str = ""
    if format == "short":
        value_str = value.strftime("%H:%M:%S-%p")
    if format == "HM":
        value_str = value.strftime("%H:%M %p")
    return value_str


def is_datetime(value):
    return isinstance(value, datetime)


class RequestCorrelationFilter(logging.Filter):
    def filter(self, record):
        if has_request_context():
            record.correlation_id = getattr(g, 'correlation_id', 'unknown')
        else:
            record.correlation_id = 'unknown'
        return True
