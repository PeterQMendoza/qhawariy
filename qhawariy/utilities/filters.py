import datetime


def format_datetime(value,format="short"):
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
    value_str=None
    if not value:
        value_str=""
    if format=="short":
        value_str=value.strftime("%d/%m/%Y")
    elif format=="full":
        value_str=value.strftime("%d %b, %Y - %I:%M %p")
    elif format=="date":
        value_str=value.strftime("%A %d de %B de %Y")
    elif format=="year":
        value_str=value.strftime("%Y")
    elif format=="month_year":
        value_str=value.strftime("%B de %Y")
    elif format=="day":
        value_str=value.strftime("%d")#
    elif format=="dayweek":
        value_str=value.strftime("%a")
    else:
        value_str=""
    return value_str

def format_time(value,format='short'):
    value_str=None
    if not value:
        value_str=""
    if format=="short":
        value_str=value.strftime("%H:%M:%S-%p")
    if format=="HM":
        value_str=value.strftime("%H:%M %p")
    return value_str

def is_datetime(value):
    return isinstance(value,datetime.datetime)