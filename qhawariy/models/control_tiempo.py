import datetime
from typing import List

from qhawariy import db
from qhawariy.models.control import Control
from qhawariy.models.fecha import Fecha
from qhawariy.models.ruta import Ruta
from qhawariy.models.vehiculo import Vehiculo
from qhawariy.models.viaje import Viaje


class ControlTiempo(db.Model):
    """
    Modelo ControlTiempo: Contiene los tiempos de los vehiculos a pasar por los puntos
    de control

    """
    __tablename__ = 'controles_tiempos'
    id_ct = db.Column(db.Integer, primary_key=True)
    tiempo = db.Column(db.Time, nullable=False)
    id_control = db.Column(
        db.Integer,
        db.ForeignKey('controles.id_control'),
        nullable=False
    )
    id_viaje = db.Column(
        db.Integer,
        db.ForeignKey('viajes.id_viaje'),
        nullable=False
    )

    control = db.relationship(
        "Control",
        back_populates="controles",
        uselist=False,
        single_parent=True
    )

    viaje = db.relationship(
        "Viaje",
        back_populates="viajes",
        uselist=False,
        single_parent=True,
        lazy=True
    )

    def __init__(
        self,
        tiempo: datetime.time,
        id_control: int,
        id_viaje: int
    ):
        self.tiempo = tiempo
        self.id_control = id_control
        self.id_viaje = id_viaje

    def __repr__(self):
        return f"<ControlTiempo {self.id_ct}>"

    def guardar(self):
        if not self.id_ct:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_por_id(id: int):
        resultado = ControlTiempo.query.get(id)
        return resultado

    @staticmethod
    def obtener_todos() -> List["ControlTiempo"]:
        return ControlTiempo.query.all()  # type: ignore

    @staticmethod
    def obtener_por_cantidad_registros(cantidad: int) -> List["ControlTiempo"]:
        return ControlTiempo.query.limit(cantidad).all()  # type: ignore

    @staticmethod
    def obtener_por_viaje(id_viaje: int) -> List["ControlTiempo"]:
        return ControlTiempo.query.filter_by(id_viaje=id_viaje).all()  # type: ignore

    @staticmethod
    def vista_diaria(date: datetime.datetime, ruta_id: int) -> List["ControlTiempo"]:
        resultado = ControlTiempo.query.join(  # type: ignore
            Viaje, Viaje.id_viaje == ControlTiempo.id_viaje
        ).join(
            Control, Control.id_control == ControlTiempo.id_control
        ).join(
            Fecha, Fecha.id_fecha == Viaje.id_fecha  # type: ignore
        ).join(
            Ruta, Ruta.id_ruta == Viaje.id_ruta  # type: ignore
        ).join(
            Vehiculo, Vehiculo.id_vehiculo == Viaje.id_vehiculo  # type: ignore
        ).where(
            Ruta.id_ruta == ruta_id,
            Fecha.fecha == date  # type: ignore
        ).all()

        return resultado  # type: ignore
