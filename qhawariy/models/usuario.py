import datetime
from flask import current_app
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
import pytz
import string
import secrets

from email.policy import default
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin

from qhawariy import db
from qhawariy.models import (asociado,plan_salida,programacion,propietario,propietario_vehiculo,
                             rol,ruta,vehiculo_programado,vehiculo,viaje,departamento,distrito,provincia,
                             fecha,ruta_terminal,terminal,control,control_tiempo,configuracion,secuencia_control_ruta)

class Usuario(db.Model, UserMixin):
    """Modelo Usuario define a todos los usuarios que pertencen e ingresan al sistema
    """
    __tablename__ = "usuarios"
    id_usuario = db.Column(db.Integer,primary_key=True)
    nombres = db.Column(db.String(50),nullable=False)
    apellidos = db.Column(db.String(50),nullable=False)
    dni = db.Column(db.String(15),unique=True,nullable=False)
    telefono = db.Column(db.String(15),nullable=False)
    correo_electronico = db.Column(db.String(50), unique=True, nullable=False)
    lima_tz=pytz.timezone('America/Lima')
    fecha_registro = db.Column(db.DateTime,default=datetime.datetime.now(tz=lima_tz))
    clave = db.Column(db.String(128), nullable=False)
    # genera un cadena 6 letras para el id altenativo
    id_alternativo = db.Column(db.String(6), nullable=False) #Utilizado para cambio de password

    # Relaciones
    uroles = db.relationship("UsuarioRol",back_populates="usuario",cascade="all,delete-orphan")

    def __init__(self, nombres, apellidos, dni, telefono, correo_electronico):
        self.nombres=nombres
        self.apellidos=apellidos
        self.dni=dni
        self.telefono=telefono
        self.correo_electronico=correo_electronico
        self.id_alternativo = ''.join((secrets.choice(string.ascii_letters) for i in range(6)))

    def __repr__(self):
        return f'<Usuario {self.correo_electronico}>'

    def establecer_clave(self, clave):
        self.clave=generate_password_hash(password=clave,method='pbkdf2',salt_length=16)

    def revisar_clave(self, clave):
        return check_password_hash(self.clave,clave)
    
    def generar_token_restablecer_password(self):
        serializer=URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        return serializer.dumps(self.correo_electronico,salt=self.clave)

    def get_id(self):
        """Para reconocer la id registrar usuario en Login_Manager Revisar la
        documentacion de Flask_login para establecer si el usuario cambia de clave
        """
        return str(self.id_alternativo)

    def guardar(self):
        if not self.id_usuario:
            if not self.id_alternativo:
                db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def validar_token_restablece_password(token: str,usuario_id: int):
        """
        Metodo estatico que valida el token obtenido de link del email enviado al usuario
        """
        usuario=Usuario.obtener_usuario_por_id(usuario_id)
        if usuario is None:
            return None
        serializer=URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        try:
            token_usuario_email=serializer.loads(
                token,
                max_age=current_app.config["RESET_PASS_TOKEN_MAX_AGE"],
                salt=usuario.clave,
            )
        except (BadSignature,SignatureExpired):
            return None
        if token_usuario_email!=usuario.correo_electronico:
            return None
        return usuario

    @staticmethod
    def obtener_usuario_por_id(id):
        return Usuario.query.get(id)

    @staticmethod
    def obtener_usuario_por_nombre(nombre):
        return Usuario.query.filter_by(nombres=nombre).first()

    @staticmethod
    def obtener_usuario_por_correo_electronico(correo_electronico):
        return Usuario.query.filter_by(correo_electronico=correo_electronico).first()

    @staticmethod
    def obtener_todos_usuarios():
        return Usuario.query.all()