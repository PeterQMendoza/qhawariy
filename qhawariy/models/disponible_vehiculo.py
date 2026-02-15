import datetime
from typing import List, Optional
import uuid

from qhawariy import db
from qhawariy.models.vehiculo import Vehiculo
from qhawariy.utilities.builtins import LIMA_TZ
from qhawariy.utilities.uuid_endpoints import ShortUUID

ahora = datetime.datetime.now(LIMA_TZ)


class DisponibleVehiculo(db.Model):
    """
    Clase DisponibleVehiculo: Establece control de la disponibilidad de vehiculos
    de acuerdo a un requerimiento de cantidad de vehiculos a programar

    La disponibilidad del vehiculo esta determinado de acuerdo al tiempo_inicio
    hasta el tiempo_final, referido al tiempo que el vehiculo esta con permiso
    y por lo cual no estara disponible por esos dias
    """

    __tablename__ = "disponibles_vehiculos"
    __table_args__ = {"schema": "app"}

    id_dv: str = db.Column(
        ShortUUID(),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    fecha_inicio = db.Column(
        db.DateTime,
        default=datetime.datetime(
            year=ahora.year,
            month=ahora.month,
            day=ahora.day,
            hour=0,
            minute=0,
            second=0
        ),
        nullable=False
    )
    # por defecto un dia
    fecha_final = db.Column(
        db.DateTime,
        default=datetime.datetime(
            year=ahora.year,
            month=ahora.month,
            day=ahora.day,
            hour=0,
            minute=0,
            second=0
        ),
        nullable=False
    )
    id_vehiculo = db.Column(
        ShortUUID(),
        db.ForeignKey('app.vehiculos.id_vehiculo', ondelete='CASCADE'),
        nullable=False
    )

    # Relaciones
    vehiculo = db.relationship(
        "Vehiculo",
        back_populates="vehiculos_disponibles",
        uselist=False,
        single_parent=True
    )

    def __init__(
        self,
        fecha_inicio: datetime.datetime,
        fecha_final: datetime.datetime,
        id_vehiculo: int
    ) -> None:
        self.fecha_inicio = fecha_inicio
        self.fecha_final = fecha_final
        self.id_vehiculo = id_vehiculo

    def __repr__(self) -> str:
        return f"<DisponibleVehiculo {self.id_dv}>"

    def guardar(self) -> None:
        if not self.id_dv:
            db.session.add(self)
        db.session.commit()

    def eliminar(self) -> None:
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_id(id: int) -> Optional["DisponibleVehiculo"]:
        resultado = DisponibleVehiculo.query.get(id)
        return resultado

    @staticmethod
    def obtener_todos() -> List["DisponibleVehiculo"]:
        return DisponibleVehiculo.query.all()  # type: ignore

    @staticmethod
    def busca_fecha(
        desde: datetime.datetime,
        hasta: datetime.datetime
    ) -> List["DisponibleVehiculo"]:
        return DisponibleVehiculo.query.filter(
            DisponibleVehiculo.fecha_inicio >= desde,  # type: ignore
            DisponibleVehiculo.fecha_final <= hasta  # type: ignore
        ).all()  # type: ignore

    @staticmethod
    def busca_vehiculo_flota(flota: int) -> List["DisponibleVehiculo"]:
        return (
            DisponibleVehiculo.query.join(
                Vehiculo,
                DisponibleVehiculo.id_vehiculo == Vehiculo.id_vehiculo  # type: ignore
            )
            .where(Vehiculo.flota == flota)  # type: ignore
            .all()
        )

    @staticmethod
    def obtener_vehiculos_disponibles(
        fecha: datetime.datetime
    ) -> List["DisponibleVehiculo"]:
        return DisponibleVehiculo.query.filter(
            DisponibleVehiculo.fecha_inicio <= fecha,  # type: ignore
            DisponibleVehiculo.fecha_final >= fecha  # type: ignore
        ).all()  # type: ignore
