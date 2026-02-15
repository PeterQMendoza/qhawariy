import datetime
from typing import List, Optional, cast
import uuid
from flask import current_app
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
import pytz
import string
import secrets

# from email.policy import default
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from qhawariy import db
from qhawariy.utilities.uuid_endpoints import ShortUUID


class Usuario(db.Model, UserMixin):
    """Modelo Usuario define a todos los usuarios que pertencen e ingresan al sistema
    """
    __tablename__ = "usuarios"
    __table_args__ = {"schema": "app"}

    id_usuario: uuid.UUID = db.Column(
        ShortUUID(),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    nombres: str = db.Column(db.String(50), nullable=False)
    apellidos: str = db.Column(db.String(50), nullable=False)
    dni: str = db.Column(db.String(15), unique=True, nullable=False)
    telefono: str = db.Column(db.String(15), nullable=False)
    correo_electronico: str = db.Column(db.String(50), unique=True, nullable=False)
    lima_tz = pytz.timezone('America/Lima')
    fecha_registro: datetime.datetime = db.Column(
        db.DateTime,
        default=datetime.datetime.now(tz=lima_tz)
    )
    clave: str = db.Column(db.String(128), nullable=False)
    # genera un cadena 6 letras para el id altenativo
    # Utilizado para cambio de password
    id_alternativo: str = db.Column(db.String(6), nullable=False)

    # Relaciones
    uroles = db.relationship(
        "UsuarioRol",
        back_populates="usuario",
        cascade="all,delete-orphan"
    )

    # Relacion inversa con la tabla
    usuario_notificaciones = db.relationship(
        "Notificacion",
        back_populates="usuario",
        cascade="all,delete-orphan"
    )

    def __init__(
        self,
        nombres: str,
        apellidos: str,
        dni: str,
        telefono: str,
        correo_electronico: str
    ):
        self.nombres = nombres
        self.apellidos = apellidos
        self.dni = dni
        self.telefono = telefono
        self.correo_electronico = correo_electronico
        self.id_alternativo = ''.join(
            (secrets.choice(string.ascii_letters) for _ in range(6))
        )
        # self.id_alternativo = generate_password_hash(
        #     password=dni,
        #     method='pbkdf2',
        #     salt_length=6
        # )

    def __repr__(self):
        return f'<Usuario {self.correo_electronico}>'

    def establecer_clave(self, clave: str) -> None:
        self.clave = generate_password_hash(
            password=clave,
            method='pbkdf2',
            salt_length=16
        )

    def revisar_clave(self, clave: str):
        return check_password_hash(self.clave, clave)

    def generar_token_restablecer_password(self):
        secret_key: str = cast(str, current_app.config["SECRET_KEY"])
        serializer = URLSafeTimedSerializer(secret_key)
        return serializer.dumps(self.correo_electronico, salt=self.clave)

    def get_id(self):
        """Para reconocer la id registrar usuario en Login_Manager Revisar la
        documentacion de Flask_login para establecer si el usuario cambia de clave
        """
        return str(self.id_alternativo)

    def guardar(self):
        if not self.id_usuario:
            db.session.add(self)
            # if not self.id_alternativo:
            #     db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def validar_token_restablece_password(
        token: str,
        usuario_id: str
    ) -> Optional["Usuario"]:
        """
        Metodo estatico que valida el token obtenido de link del email enviado al
        usuario
        """
        usuario = Usuario.obtener_usuario_por_id(usuario_id)
        if usuario is None:
            return None
        secret_key: str = cast(str, current_app.config["SECRET_KEY"])
        serializer = URLSafeTimedSerializer(secret_key)
        try:
            max_age: int = cast(int, current_app.config["RESET_PASS_TOKEN_MAX_AGE"])
            token_usuario_email = serializer.loads(
                token,
                max_age=max_age,
                salt=usuario.clave,
            )
        except (BadSignature, SignatureExpired):
            return None
        if token_usuario_email != usuario.correo_electronico:
            return None
        return usuario

    @staticmethod
    def obtener_usuario_por_id(id: str):
        return Usuario.query.get(id)

    @staticmethod
    def obtener_usuario_por_id_alternativo(id: str) -> Optional["Usuario"]:
        return Usuario.query.filter_by(id_alternativo=id).first()  # type: ignore

    @staticmethod
    def obtener_usuario_por_nombre(nombre: str) -> Optional["Usuario"]:
        return Usuario.query.filter_by(nombres=nombre).first()  # type: ignore

    @staticmethod
    def obtener_usuario_por_correo_electronico(
        correo_electronico: str
    ) -> Optional["Usuario"]:
        return (
            Usuario.query
            .filter_by(correo_electronico=correo_electronico)
            .first()
        )  # type: ignore

    @staticmethod
    def obtener_todos_usuarios() -> List["Usuario"]:
        return Usuario.query.all()  # type: ignore

    # Saber si hay solo un registro
    @staticmethod
    def existe_usuario():
        return Usuario.query.first() is not None

    # validar la no duplicidad del DNI
    @staticmethod
    def obtener_por_dni(dni: str) -> Optional["Usuario"]:
        return Usuario.query.filter_by(dni=dni).first()  # type: ignore
