# import datetime
# import pytz

from typing import List, Optional
from sqlalchemy import desc
# from sqlalchemy.sql import func

from qhawariy import db
from qhawariy.models.ruta import Ruta
from qhawariy.models.fecha import Fecha
from qhawariy.models.ruta_terminal import RutaTerminal
from qhawariy.models.terminal import Terminal


class Programacion(db.Model):
    """Modelo Programacion:
    """
    __tablename__ = "programaciones"
    id_programacion = db.Column(db.Integer, primary_key=True)
    id_fecha = db.Column(db.Integer, db.ForeignKey("fechas.id_fecha"), nullable=False)
    id_ruta = db.Column(db.Integer, db.ForeignKey("rutas.id_ruta"), nullable=False)
    # Establecer relaciones {Table1}*1-->1{Table2}
    ruta = db.relationship(
        "Ruta",
        back_populates="rutas_programas",
        uselist=False,
        single_parent=True
    )
    fecha = db.relationship(
        "Fecha",
        back_populates="fechas_programas",
        uselist=False,
        single_parent=True
    )
    programas_vehiculos = db.relationship(
        "VehiculoProgramado",
        back_populates="programa",
        cascade="all,delete-orphan"
    )

    def __init__(self, id_fecha: int, id_ruta: int):
        self.id_fecha = id_fecha
        self.id_ruta = id_ruta

    def __repr__(self):
        return f'<Programacion {self.id_programacion}>'

    def guardar(self):
        if not self.id_programacion:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_programacion_por_id(id: int):
        return Programacion.query.get(id)

    @staticmethod
    def obtener_todos_programaciones() -> List["Programacion"]:
        return Programacion.query.all()  # type: ignore

    @staticmethod
    def obtener_por_fecha_y_ruta(
        fecha: int,
        ruta: int
    ) -> Optional["Programacion"]:
        return (
            Programacion.query.
            filter_by(id_fecha=fecha, id_ruta=ruta)
            .first()
        )  # type: ignore

    @staticmethod
    def obtener_por_fecha(fecha_id: int) -> Optional["Programacion"]:
        return (
            Programacion.query
            .filter_by(id_fecha=fecha_id)
            .first()
        )  # type: ignore

    @staticmethod
    def obtener_programa_join_ruta() -> List["Programacion"]:
        """"""
        return (
            Programacion.query
            .join(Ruta, Ruta.id_ruta == Programacion.id_ruta)
            .join(RutaTerminal, RutaTerminal.id_ruta == Ruta.id_ruta)  # type: ignore
            .join(
                Terminal,
                Terminal.id_terminal == RutaTerminal.id_terminal  # type: ignore
            )
            .join(Fecha, Fecha.id_fecha == Programacion.id_fecha)  # type: ignore
            .add_columns(
                Programacion.id_programacion,
                Fecha.fecha,  # type: ignore
                Programacion.id_ruta,  # type: ignore
                Terminal.direccion,  # type: ignore
                Ruta.id_ruta,
                Ruta.codigo  # type: ignore
            )
            .order_by(desc(Programacion.id_fecha))  # type: ignore
            .limit(22)
            .all()
        )  # type: ignore

    @staticmethod
    def obtener_programas() -> List["Programacion"]:
        return (
            Programacion.query
            .order_by(desc(Programacion.id_fecha))  # type: ignore
            .limit(22)
            .all()
        )  # type: ignore
