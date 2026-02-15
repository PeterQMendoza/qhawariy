# import datetime
# import pytz

from typing import List, Optional
import uuid
from qhawariy import db
from sqlalchemy.sql import asc

from qhawariy.utilities.uuid_endpoints import ShortUUID


class Propietario(db.Model):
    __tablename__ = "propietarios"
    __table_args__ = {"schema": "app"}

    id_propietario: str = db.Column(
        ShortUUID(),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    nombres: str = db.Column(db.String(50), nullable=False)
    apellidos: str = db.Column(db.String(50), nullable=False)
    telefono: str = db.Column(db.String(15), nullable=False)
    documento_identificacion: str = db.Column(db.String(15), nullable=False)

    def __init__(
        self,
        nombres: str,
        apellidos: str,
        telefono: str,
        documento_identificacion: str,
    ):
        self.nombres = nombres
        self.apellidos = apellidos
        self.telefono = telefono
        self.documento_identificacion = documento_identificacion

    def __repr__(self):
        return f'<Propietario {self.id_propietario}>'

    def guardar(self):
        if not self.id_propietario:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_propietario_por_id(id: int):
        return Propietario.query.get(id)

    @staticmethod
    def obtener_propietario_por_dni(dni: str) -> Optional["Propietario"]:
        return (
            Propietario.query
            .filter_by(documento_identificacion=dni)
            .first()
        )  # type: ignore

    @staticmethod
    def obtener_propietario_por_apellidos(apellido: str) -> Optional["Propietario"]:
        return (
            Propietario.query
            .filter_by(apellidos=apellido)
            .first()
        )  # type: ignore

    @staticmethod
    def obtener_todos_propietarios() -> List["Propietario"]:
        return (
            Propietario.query
            .order_by(asc(Propietario.apellidos))
            .all()
        )  # type: ignore

    @staticmethod
    def buscar_propietarios_dni(dni: str) -> List["Propietario"]:
        return (
            Propietario.query
            .filter_by(documento_identificacion=dni)
            .all()
        )  # type: ignore
