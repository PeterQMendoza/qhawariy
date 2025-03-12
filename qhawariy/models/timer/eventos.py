from apscheduler.events import (
    EVENT_JOB_ADDED,
    EVENT_JOB_ERROR,
    EVENT_JOB_EXECUTED,
    EVENT_JOB_MISSED,
    EVENT_JOB_REMOVED,
    EVENT_JOB_SUBMITTED
)

from qhawariy import scheduler


def trabajo_perdido(event):
    with scheduler.app.app_context():
        print(event)


def trabajo_agregado(event):
    with scheduler.app.app_context():
        print(event)


def trabajo_error(event):
    with scheduler.app.app_context():
        print(event)


def trabajo_ejecutado(event):
    with scheduler.app.app_context():
        print(event)


def trabajo_eliminado(event):
    with scheduler.app.app_context():
        print(event)


def trabajo_enviado(event):
    with scheduler.app.app_context():
        print(event)


scheduler.add_listener(trabajo_agregado, EVENT_JOB_ADDED)
scheduler.add_listener(trabajo_perdido, EVENT_JOB_MISSED)
scheduler.add_listener(trabajo_error, EVENT_JOB_ERROR)
scheduler.add_listener(trabajo_ejecutado, EVENT_JOB_EXECUTED)
scheduler.add_listener(trabajo_eliminado, EVENT_JOB_REMOVED)
scheduler.add_listener(trabajo_enviado, EVENT_JOB_SUBMITTED)
