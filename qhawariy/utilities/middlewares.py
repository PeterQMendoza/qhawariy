import locale
import time
from typing import Any, Dict, Optional
import uuid
import os
import base64

from flask import (
    abort,
    current_app,
    g,
    jsonify,
    request,
    session,
    Response
)
from flask_wtf.csrf import validate_csrf, generate_csrf  # type: ignore
from wtforms.validators import ValidationError
from werkzeug.exceptions import HTTPException

# from qhawariy.utilities.decorators import middleware_debugger


# Correlation ID
def assign_correlation_id():
    g.correlation_id = request.headers.get(
        'X-Correlation-ID',
        str(uuid.uuid4())
    )


# @middleware_debugger
def add_correlation_id(response: Response) -> Response:
    # if response is None:
    #     return response
    correlation_id = getattr(g, 'correlation_id', 'unknown')
    # correlation_id = response.headers.get("X-Correlation-ID", 'unknow')
    response.headers['X-Correlation-ID'] = correlation_id

    return response


# Loggin de solicitudes
def log_request_start():
    # request.start_time = time.time()
    request.environ["start_time"] = time.time()
    current_app.logger.info(
        "Solicituda entrante: %s %s",
        request.method,
        request.path
    )


# @middleware_debugger
def log_request_end(response: Response) -> Response:
    duration = time.time() - getattr(request, "start_time", time.time())
    current_app.logger.info(
        "Solicitud %s %s completada en %.3f segundos",
        request.method,
        request.path,
        duration
    )
    return response


# Seguridad y CORS
# @middleware_debugger
def add_security_headers(response: Response) -> Response:
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    # Politicas de seguridad
    # (Genera error al definirlo aqui, se sobrescribe add_nonce)
    # response.headers['Content-Security-Policy'] = (
    #     "default-src 'self'; "
    #     "script-src 'self'; "
    #     "style-src 'self'; "
    #     "img-src 'self' data:; "
    #     "object-src 'none'; "
    #     "base-uri 'self'; "
    #     "form-action 'self';"
    # )
    return response


# @middleware_debugger
def add_isolation_headers(response: Response) -> Response:
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
    return response


def generate_nonce():
    """Proteccion de lineas de scripts agregando un valor aleatorio"""
    nonce = base64.b64encode(os.urandom(16)).decode('utf-8')
    # Guarda el nonce en el objeto global 'g' para usarlo en la plantilla y la cabecera
    g.nonce = nonce


# @middleware_debugger
def add_csp_header(response: Response) -> Response:
    """Agrega el nonce en la directiva CSP para los scripts en línea"""
    nonce = getattr(g, 'nonce', '')
    csp = f"script-src 'self' 'nonce-{nonce}'; object-src 'self';"
    response.headers['Content-Security-Policy'] = csp
    return response


# @middleware_debugger
def add_cors_headers(response: Response) -> Response:
    # Genera un error al consumir datos de la frontend
    # response.headers["Access-Control-Allow-Origin"] = "*"
    # Extrae el 'Origin' de la solicitud
    origin = request.headers.get("Origin")
    allowed_origins = ['http://localhost:4200']

    # Si el origin de la solicitud esta permitida, lo asignamos al headers
    if origin in allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
    else:
        response.headers["Access-Control-Allow-Origin"] = "*"

    response.headers["Access-Control-Allow-Headers"] = (
        "Content-Type, Authorization, X-CSRFToken"
    )

    response.headers["Access-Control-Allow-Methods"] = "GET, PUT, POST, DELETE, OPTIONS"

    # Si la API requiere credenciales, indicar aqui
    response.headers["Access-Control-Allow-Credentials"] = "true"

    return response


# Gestion global de errores
def handle_global_error(error: HTTPException) -> Response:
    response = jsonify({
        "nombre": __name__,
        "error": "Ha ocurrido un error inesperado.",
        "message": str(error)
    })
    response.status_code = 500
    return response


# Verificacion de Token
def verify_token():
    token = request.headers.get("Authorization")
    if not token:
        abort(401, description="No autorizado")


# Configurar el locale
def configurar_local():
    # Configurar locale para es_PE.UTF-8 (Perú)
    locale_str = 'es_PE.UTF-8'
    try:
        locale.setlocale(locale.LC_ALL, locale_str)
    except locale.Error:
        return "Locale 'es_PE.UTF-8' no esta disponible en este sistema", 500


# verificar
# @middleware_debugger
def add_vary_cookie(response: Response) -> Response:
    # if response is None:
    #     current_app.logger.error(
    #         "El middleware recibió una response None, creando una respuesta vacía."
    #     )
    #     response = make_response('')

    if getattr(response, 'vary', None) is not None:
        response.vary.add("Cookie")
    else:
        current_app.logger.warning("La respuesta no tiene el atributo 'vary'.")

    return response


# @middleware_debugger
def global_response_check(response: Optional[Response]) -> Optional[Response]:
    if response is None:
        current_app.logger.error("El response final es none")
        from flask import make_response
        return make_response("Error interno> respuesta nula", 500)
    return response


def csrf_protect():
    if request.method in ['GET', 'HEAD', 'OPTIONS']:
        return

    if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
        token = request.headers.get('X-CSRFToken')
        if not token and request.is_json:
            data: Any | Dict[str, str] = request.get_json(silent=True) or {}
            token = data.get('csrf_token')
        token_actual: Optional[str] = session.get('csrf_token')  # type: ignore
        current_app.logger.info(f"Token recibido: {token}")
        current_app.logger.info(f"Token actual: {token_actual}")

        if not token:
            token = request.cookies.get('csrf_token')
        if not token:
            return jsonify({"error": "CSRF token perdido"}), 400

        # Extrae el token que se guardo en sesion para compararlo
        try:
            validate_csrf(token)
        except ValidationError as e:
            current_app.logger.error(f"error CSRF token invalido: {e}")
            return jsonify({"error": "CSRF token invalido", "message": str(e)}), 400


def set_csrf_cookie(response: Response) -> Response:
    if request.method == 'OPTIONS':
        return response

    token: str = session.get('csrf_token')  # type: ignore
    if not token:
        token = generate_csrf()
        session['csrf_token'] = token
        current_app.logger.info(f"Token generado: {token}")
    else:
        current_app.logger.info(f"Token existente en session: {token}")
    response.set_cookie(
        'csrf_token',
        token,
        httponly=True,
        secure=False,
        samesite='Strict'
    )
    return response
