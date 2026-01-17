# Decoradores usados para estblecer nivel de acceso por roles al sistema
from functools import wraps
from typing import Any, Callable, Optional, TypeVar

from flask import (
    Response,
    abort,
    current_app,
    request,
    jsonify
)
from flask_login import current_user
from flask_wtf.csrf import validate_csrf   # type: ignore
from wtforms.validators import ValidationError

F = TypeVar("F", bound=Callable[..., Response])


# Estableciendo acceso de usuario de acuerdo a roles
def admin_required(func: F) -> F:
    @wraps(func)
    def decorated_function(*args: Any, **kwargs: Any):
        from qhawariy.models.usuario_rol import UsuarioRol
        id_user = current_user.id_usuario
        ur = UsuarioRol.obtener_por_id_usuario(id_user)
        rol = ur.rol
        is_admin = getattr(rol, "rol", False)
        if is_admin != 'Administrador':
            abort(401)
        return func(*args, **kwargs)
    return decorated_function  # type: ignore


def operacion_required(func: F) -> F:
    @wraps(func)
    def decorated_function(*args: Any, **kwargs: Any):
        from qhawariy.models.usuario_rol import UsuarioRol
        id_user = current_user.id_usuario
        ur = UsuarioRol.obtener_por_id_usuario(id_user)
        rol = ur.rol
        is_operaciones = getattr(rol, "rol", False)
        if is_operaciones != 'Operacion':
            abort(401)
        return func(*args, **kwargs)
    return decorated_function  # type: ignore


def controlador_required(func: F) -> F:
    @wraps(func)
    def decorated_function(*args: Any, **kwargs: Any):
        from qhawariy.models.usuario_rol import UsuarioRol
        id_user = current_user.id_usuario
        ur = UsuarioRol.obtener_por_id_usuario(id_user)
        rol = ur.rol
        is_controlador = getattr(rol, "rol", False)
        if is_controlador != 'Controlador':
            abort(401)
        return func(*args, **kwargs)
    return decorated_function  # type: ignore


def middleware_debugger(func: F) -> F:
    """
    Decorador que registra la entrada y salida de un middleware.
    Si el middleware retorna None, se registra un error
    """
    @wraps(func)
    def wrapped(
        response: Optional[Response],
        *args: Any,
        **kwargs: Any
    ) -> Optional[Response]:
        current_app.logger.info(
            "Ejecutando middlewware '%s' con response: %s",
            func.__name__,
            response
        )
        result: Optional[Response] = func(response, *args, **kwargs)
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
    return wrapped  # type: ignore


def validar_csrf_token(header: str = "X-CSRFToken") -> Callable[[F], F]:
    """Decorador para validar token csrf"""
    def decorador(func: F) -> F:
        @wraps(func)
        def envoltura(*args: Any, **kwargs: Any) -> Response:
            token = (
                request.headers.get(header)
                or request.form.get('csrf_token')
                or request.args.get("csrf_token")
            )
            try:
                validate_csrf(token)
            except ValidationError as e:
                response = jsonify(error="Token CSRF invalido", mensaje=str(e))
                response.status_code = 400
                return response
            return func(*args, **kwargs)
        return envoltura  # type: ignore
    return decorador
