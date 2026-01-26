import json
import csv
import logging
import os
from typing import Optional, cast

from flask import (
    Blueprint,
    current_app,
    request,
    jsonify,
    session
)
from flask_cors import cross_origin
from flask_wtf.csrf import generate_csrf, validate_csrf, ValidationError  # type: ignore

from itsdangerous import URLSafeSerializer

from qhawariy import csrf

logger = logging.getLogger(__name__)

# Blueprint
bp = Blueprint("coordenadas", __name__, url_prefix="/coordenadas")


@bp.route("/api/<int:fleet>", methods=["POST"])
@csrf.exempt  # type: ignore
@cross_origin(origins="http://localhost:4200", supports_credentials=True)
def recibir_coordenadas(fleet: int):
    # token = request.headers.get('X-CSRFToken')
    # stored_token = cache.get("csrf_token")

    # if not stored_token or token != stored_token:
    #     logger.error("Token invalido o expirado")
    #     return jsonify({"error": "Token invalido o expirado"}), 500
    token = request.headers.get('X-CSRFToken')
    if not token:
        token = cast(Optional[str], session.get('csrf_token'))  # type: ignore
    if token is None:
        current_app.logger.error("CSRF token ausente")
        return jsonify({"error": "CSRF token ausente"}), 400

    try:
        validate_csrf(token)
    except ValidationError as e:
        current_app.logger.error(f"{__name__} error CSRF token invalido: {e}")
        return jsonify({"error": "CSRF token invalid", "message": str(e)}), 400

    filename = f"{fleet}coord.csv"
    folder = cast(
        str,
        current_app.config.get("COORD_DATA_FOLDER", ".")  # type: ignore
    )
    path = os.path.join(folder, filename)
    data = request.get_json()
    try:
        lat = data.get('latitud')
        lon = data.get('longitud')
        with open(path, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([lat, lon])
    except json.JSONDecodeError as e:
        logger.error(f"Error: {e}")
        return jsonify({"Error": e}), 500
    except FileNotFoundError:
        with open(path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)

    return jsonify({"mensaje": "Guardado con exito"}), 200


@bp.route("unsign", methods=["GET"])
def unsign():
    # Para decodificar firma
    secret_key = current_app.secret_key
    if secret_key is None:
        return jsonify({"Error": "SECRET_KEY no esta configurado"}), 500
    serializer = URLSafeSerializer(secret_key)
    signed_data = request.args
    if not signed_data:
        return jsonify({"error": "No ha proporcionado dato firmado"}), 400
    try:
        unsigned_data = {
            key: serializer.loads(value) for key, value in signed_data.items()
        }
        return jsonify(unsigned_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@bp.route("get-csrf-token", methods=["GET"])
# @cross_origin(origins="http://localhost:4200", supports_credentials=True)
def get_csrf():
    # token = generate_csrf()
    # response = jsonify({"csrf_token": token})
    # response.set_cookie(
    # 'crsf_token',
    # token,
    # httponly=False,
    # secure=True,
    # samesite='Strict'
    # )
    # return response
    token = cast(Optional[str], session.get('csrf_token'))  # type: ignore
    if not token:
        token = generate_csrf()
        session['csrf_token'] = token
    response = jsonify({"csrf_token": token})
    response.set_cookie(
        'csrf_token',
        token,
        httponly=False,
        secure=True,
        samesite='Strict'
    )
    current_app.logger.info(f"Token generado: {token}")
    return response


@bp.route("/sign", methods=["POST"])
def sign():
    # Para firmar datos
    data = request.json
    secret_key = current_app.secret_key
    if secret_key is None:
        return jsonify({"Error": "SECRET_KEY no esta configurado"}), 500
    serializer = URLSafeSerializer(secret_key)
    if not data:
        return jsonify({"error": "Dato no porporcionado"}), 400
    signed_data = {
        key: serializer.dumps(value) for key, value in data.items()
    }
    return jsonify(signed_data)


@bp.route("/verifica-origin", methods=['GET'])
@cross_origin(origins="http://localhost:4200", supports_credentials=True)
def verifica_origin():
    all_headers = dict(request.headers)
    origin = request.headers.get('Origin')
    logger.info(f"headers: {all_headers}")
    return jsonify({'origin': origin}), 200
