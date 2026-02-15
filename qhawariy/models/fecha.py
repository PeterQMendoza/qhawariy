import datetime
from typing import List, Optional
import uuid
# import pytz
from sqlalchemy import asc

from qhawariy import db
from qhawariy.utilities.builtins import LIMA_TZ
from qhawariy.utilities.uuid_endpoints import ShortUUID

ahora = datetime.datetime.now(tz=LIMA_TZ)


class Fecha(db.Model):
    """Modelo Fecha: contiene la fecha en la cual de realizan las programaciones,
    tambien es utilzado para reportar los viejas
    """
    __tablename__ = "fechas"
    __table_args__ = {"schema": "app"}

    id_fecha: str = db.Column(
        ShortUUID(),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    fecha: datetime.datetime = db.Column(
        db.DateTime,
        default=datetime.datetime(
            year=ahora.year,
            month=ahora.month,
            day=ahora.day,
            hour=0,
            minute=0,
            second=0
        )
    )

    # Relaciones
    fechas_programas = db.relationship(
        "Programacion",
        back_populates="fecha",
        cascade="all,delete-orphan"
    )
    fechas_viajes = db.relationship(
        "Viaje",
        back_populates="fecha",
        cascade="all,delete-orphan"
    )

    def __init__(self, fecha: datetime.datetime):
        self.fecha = fecha

    def __repr__(self):
        return f'<Fecha {self.fecha}>'

    def guardar(self):
        if not self.id_fecha:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_id(id: int) -> Optional["Fecha"]:
        resultado = Fecha.query.get(id)
        return resultado

    @staticmethod
    def obtener_todas_fechas() -> List["Fecha"]:
        return Fecha.query.all()  # type: ignore

    @staticmethod
    def obtener_fecha_por_fecha(fecha: datetime.datetime) -> Optional["Fecha"]:
        return Fecha.query.filter_by(fecha=fecha).first()  # type: ignore

    @staticmethod
    def obtener_rango_fecha(
        ini: datetime.datetime,
        fin: datetime.datetime
    ) -> List["Fecha"]:
        return (
            Fecha.query
            .filter(Fecha.fecha >= ini, Fecha.fecha <= fin)  # type: ignore
            .order_by(asc(Fecha.fecha))  # type: ignore
            .all()
        )  # type: ignore
