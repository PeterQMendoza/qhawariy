import json
import csv
import logging

from flask import Blueprint, current_app, flash,request,jsonify,g,session
from itsdangerous import URLSafeSerializer, URLSafeTimedSerializer

from flask_wtf.csrf import generate_csrf,validate_csrf
from wtforms import ValidationError

from qhawariy import csrf,cache

logger=logging.getLogger(__name__)

# Blueprint
bp=Blueprint("coordenadas",__name__,url_prefix="/coordenadas")


@bp.route("/api/<int:fleet>",methods=["POST"])
@csrf.exempt
def recibir_coordenadas(fleet):
    token = request.headers.get('X-CSRFToken')
    stored_token=cache.get("csrf_token")
    if not stored_token or token!=stored_token:
        return jsonify({"error":"Token invalido o expirado"})


    try:
        data = request.get_json()
        lat = data.get('latitud')
        lon = data.get('longitud')
        filename=str(fleet)+"coord.csv"
        path=current_app.config["COORD_DATA_FOLDER"]+"\\"+filename
        with open(path, 'a',newline='') as file:
            writer=csv.writer(file)
            writer.writerow([lat,lon])
    except json.JSONDecodeError as e:
        return jsonify({"Error":e})
    except FileNotFoundError:
        with open(path,'w',newline='') as file:
            writer=csv.writer(file)
            writer.writerow(data)

    return jsonify({"mensaje": "Guardado con exito"})

@bp.route("unsign",methods=["GET"])
def unsign():
    # Para decodificar firma
    serializer=URLSafeSerializer(current_app.secret_key)
    signed_data=request.args
    if not signed_data:
        return jsonify({"error":"No ha proporcionado dato firmado"}),400
    try:
        unsigned_data={key:serializer.loads(value) for key,value in signed_data.items()}
        return jsonify(unsigned_data)
    except Exception as e:
        return jsonify({"error":str(e)}),400
    
@bp.route("get_csrfToken",methods=["GET"])
def get_csrf():
    token=generate_csrf()
    cache.set("csrf_token",token)
    return jsonify({"CSRF-TOKEN":token})

@bp.route("/sign",methods=["POST"])
def sign():
    #Para firmar datos
    data=request.json
    serializer=URLSafeSerializer(current_app.secret_key)
    if not data:
        return jsonify({"error":"Dato no porporcionado"}),400
    signed_data={key:serializer.dumps(value) for key, value in data.items()}
    return jsonify(signed_data)