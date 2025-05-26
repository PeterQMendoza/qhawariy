# Decoradores usados para estblecer nivel de acceso por roles al sistema
from functools import wraps

from flask import abort, current_app
from flask_login import current_user


# Estableciendo acceso de usuario de acuerdo a roles
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from qhawariy.models.usuario_rol import UsuarioRol
        id_user = current_user.id_usuario
        ur = UsuarioRol.obtener_por_id_usuario(id_user)
        rol = ur.rol
        is_admin = getattr(rol, "rol", False)
        if is_admin != 'Administrador':
            abort(401)
        return f(*args, **kwargs)
    return decorated_function


def operacion_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from qhawariy.models.usuario_rol import UsuarioRol
        id_user = current_user.id_usuario
        ur = UsuarioRol.obtener_por_id_usuario(id_user)
        rol = ur.rol
        is_operaciones = getattr(rol, "rol", False)
        if is_operaciones != 'Operacion':
            abort(401)
        return f(*args, **kwargs)
    return decorated_function


def controlador_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from qhawariy.models.usuario_rol import UsuarioRol
        id_user = current_user.id_usuario
        ur = UsuarioRol.obtener_por_id_usuario(id_user)
        rol = ur.rol
        is_controlador = getattr(rol, "rol", False)
        if is_controlador != 'Controlador':
            abort(401)
        return f(*args, **kwargs)
    return decorated_function


def middleware_debugger(func):
    """
    Decorador que registra la entrada y salida de un middleware.
    Si el middleware retorna None, se registra un error
    """
    @wraps(func)
    def wrapped(response, *args, **kwargs):
        current_app.logger.info(
            "Ejecutando middlewware '%s' con response: %s",
            func.__name__,
            response
        )
        result = func(response, *args, **kwargs)
        if result is None:
            current_app.logger.error(
                "El middleware '%s' retorno None. Verifica su implementacion",
                func.__name__
            )
        else:
            current_app.logger.info(
                "El middleware '%s' retorno response: %s",
                func.__name__,
                result
            )
        return result
    return wrapped
