import datetime
from typing import List, Optional
# import pytz

from flask_sqlalchemy.pagination import Pagination

from sqlalchemy import asc
from sqlalchemy.sql import func

from qhawariy import db
from qhawariy.models.fecha import Fecha
from qhawariy.models.ruta import Ruta
from qhawariy.models.vehiculo import Vehiculo
from qhawariy.models.control import Control


class Viaje(db.Model):
    """" Modelo Viaje
    """
    __tablename__ = "viajes"
    id_viaje: int = db.Column(db.Integer, primary_key=True)
    # Columna de la tabla que indica el numero de vueltas realizadas por un vehiculo
    orden: int = db.Column(db.Integer, nullable=False)
    id_vehiculo: int = db.Column(
        db.Integer,
        db.ForeignKey("vehiculos.id_vehiculo"),
        nullable=False
    )
    id_ruta: int = db.Column(
        db.Integer,
        db.ForeignKey("rutas.id_ruta"),
        nullable=False
    )
    id_fecha: int = db.Column(
        db.Integer,
        db.ForeignKey("fechas.id_fecha"),
        nullable=False
    )

    # Relaciones
    ruta = db.relationship(
        "Ruta",
        back_populates="rutas_viajes",
        uselist=False,
        single_parent=True
    )
    fecha = db.relationship(
        "Fecha",
        back_populates="fechas_viajes",
        uselist=False,
        single_parent=True
    )
    vehiculo = db.relationship(
        "Vehiculo",
        back_populates="vehiculos_viajes",
        uselist=False,
        single_parent=True
    )

    # Relaciones
    viajes = db.relationship(
        "ControlTiempo",
        back_populates="viaje",
        cascade="all,delete-orphan"
    )

    def __init__(
        self,
        id_ruta: int,
        id_vehiculo: int,
        orden: int,
        id_fecha: int
    ):
        self.orden = orden
        self.id_vehiculo = id_vehiculo
        self.id_ruta = id_ruta
        self.id_fecha = id_fecha

    def __repr__(self):
        return f'<Viaje {self.id_viaje}>'

    def guardar(self):
        if not self.id_viaje:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_viaje_por_id(id: int):
        return Viaje.query.get(id)

    @staticmethod
    def obtener_viaje_por_id_vehiculo(id: int) -> Optional["Viaje"]:
        """
        Obtiene todos los vehiculos por el id_vehiculo
        """
        return Viaje.query.filter_by(id_vehiculo=id).first()  # type: ignore

    @staticmethod
    def obtener_viaje_por_fecha_id_vehiculo(
        fecha_id: int,
        vehiculo_id: int
    ) -> List["Viaje"]:
        # Sin importaciones cruzadas
        from qhawariy.models.control_tiempo import ControlTiempo
        return (
            Viaje.query.join(
                ControlTiempo,
                ControlTiempo.id_viaje == Viaje.id_viaje  # type: ignore
            ).where(
                Viaje.id_fecha == fecha_id,  # type: ignore
                Viaje.id_vehiculo == vehiculo_id  # type: ignore
            ).order_by(
                asc(ControlTiempo.tiempo)  # type: ignore
            ).all()
        )  # type: ignore

    @staticmethod
    def obtener_todos_viajes() -> List["Viaje"]:
        return Viaje.query.all()  # type: ignore

    @staticmethod
    def obtener_conteo_viajes_por_vehiculo(id_vehiculo: int):
        resultado = Viaje.query.filter_by(
            id_vehiculo=id_vehiculo
        ).add_columns(
            func.count(Viaje.id_viaje)  # type: ignore
        ).first()
        # scalar convierte listas tuples por join en listas de objetos de clase
        return resultado

    @staticmethod
    def obtener_viaje_join_vehiculo() -> Pagination:
        return (
            Viaje.query.join(
                Vehiculo, Viaje.id_vehiculo == Vehiculo.id_vehiculo  # type: ignore
            ).join(
                Fecha, Viaje.id_fecha == Fecha.id_fecha  # type: ignore
            ).join(
                Ruta, Ruta.id_ruta == Viaje.id_ruta  # type: ignore
            ).add_columns(
                Viaje.id_viaje,  # type: ignore
                Fecha.fecha,  # type: ignore
                Vehiculo.flota,  # type: ignore
                Ruta.codigo,  # type: ignore
                Viaje.orden  # type: ignore
            ).order_by(
                Fecha.fecha  # type: ignore
            ).paginate(page=1, per_page=10)  # type: ignore
        )  # type: ignore

    @staticmethod
    def obtener_viaje_por_fecha(fecha_id: int) -> List["Viaje"]:
        return (
            Viaje.query.join(
                Fecha, Fecha.id_fecha == Viaje.id_fecha  # type: ignore
            ).filter(
                Fecha.id_fecha == fecha_id  # type: ignore
            ).all()
        )  # type: ignore

    @staticmethod
    def obtener_por_fecha(idfecha: int) -> List["Viaje"]:
        resultado = Viaje.query.join(
            Vehiculo, Viaje.id_vehiculo == Vehiculo.id_vehiculo  # type: ignore
        ).join(
            Fecha, Viaje.id_fecha == Fecha.id_fecha  # type: ignore
        ).join(
            Ruta, Ruta.id_ruta == Viaje.id_ruta  # type: ignore
        ).add_columns(
            Viaje.id_viaje,  # type: ignore
            Fecha.fecha,  # type: ignore
            Vehiculo.flota,  # type: ignore
            Ruta.codigo,  # type: ignore
            Viaje.orden  # type: ignore
        ).filter(
            Fecha.id_fecha == idfecha  # type: ignore
        ).all()
        return resultado

    @staticmethod
    def obtener_orden_ruta(
        orden: int,
        vehiculo_id: int,
        ruta_id: int
    ) -> Optional["Viaje"]:
        return (
            Viaje.query.filter_by(
                orden=orden,
                id_ruta=ruta_id,
                id_vehiculo=vehiculo_id
            ).first()
        )  # type: ignore

    # Para el analisis de datos
    @staticmethod
    def vista_diaria(
        fecha: datetime.datetime,
        ruta_id: int
    ) -> List["Viaje"]:
        from qhawariy.models.control_tiempo import ControlTiempo
        return (
            Viaje.query.join(
                Ruta,
                Ruta.id_ruta == Viaje.id_ruta  # type: ignore
            ).join(
                Fecha,
                Fecha.id_fecha == Viaje.id_fecha  # type: ignore
            ).join(
                Vehiculo,
                Vehiculo.id_vehiculo == Viaje.id_vehiculo  # type: ignore
            ).join(
                ControlTiempo,
                ControlTiempo.id_viaje == Viaje.id_viaje  # type: ignore
            ).join(
                Control,
                Control.id_control == ControlTiempo.id_control
            ).where(
                Fecha.fecha == fecha,  # type: ignore
                Ruta.id_ruta == ruta_id  # type: ignore
            ).all()
        )  # type: ignore

    # Para mostrar estadisticas
    @staticmethod
    def estadistica_viajes_por_vehiculo():
        resultado = Viaje.query.join(
            Vehiculo, Vehiculo.id_vehiculo == Viaje.id_vehiculo  # type: ignore
        ).add_columns(
            Vehiculo.flota,  # type: ignore
            func.count(Viaje.id_viaje)  # type: ignore
        ).group_by(
            Vehiculo.id_vehiculo  # type: ignore
        ).all()
        return resultado

    @staticmethod
    def estadistica_viajes_por_fecha_ruta(id_ruta: int):
        """
        metodo estatico que retorna el total de viajes realizados por fecha dentro
        de un ruta
        """
        resultado = Viaje.query.join(
            Fecha, Fecha.id_fecha == Viaje.id_fecha  # type: ignore
        ).join(
            Ruta, Ruta.id_ruta == Viaje.id_ruta  # type: ignore
        ).add_columns(
            Fecha.fecha,  # type: ignore
            func.count(Viaje.id_viaje),  # type: ignore
        ).where(
            Ruta.id_ruta == id_ruta  # type: ignore
        ).order_by(
            asc(Fecha.fecha)  # type: ignore
        ).group_by(
            Fecha.id_fecha  # type: ignore
        ).all()
        return resultado

    @staticmethod
    def estadistica_viajes_por_fecha():
        """
        Funcion que retorna el total de viajes realizados por fecha
        """
        resultado = Viaje.query.join(
            Fecha, Fecha.id_fecha == Viaje.id_fecha  # type: ignore
        ).join(
            Ruta, Ruta.id_ruta == Viaje.id_ruta  # type: ignore
        ).add_columns(
            Fecha.fecha,  # type: ignore
            func.count(Viaje.id_viaje)  # type: ignore
        ).order_by(
            asc(Fecha.fecha)  # type: ignore
        ).group_by(
            Fecha.id_fecha  # type: ignore
        ).all()
        return resultado
