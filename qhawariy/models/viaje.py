import datetime
# import pytz

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
    id_viaje = db.Column(db.Integer, primary_key=True)
    # Columna de la tabla que indica el numero de vueltas realizadas por un vehiculo
    orden = db.Column(db.Integer, nullable=False)
    id_vehiculo = db.Column(
        db.Integer,
        db.ForeignKey("vehiculos.id_vehiculo"),
        nullable=False
    )
    id_ruta = db.Column(
        db.Integer,
        db.ForeignKey("rutas.id_ruta"),
        nullable=False
    )
    id_fecha = db.Column(
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

    def __init__(self, id_ruta, id_vehiculo, orden, id_fecha):
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
    def obtener_viaje_por_id(id):
        return Viaje.query.get(id)

    @staticmethod
    def obtener_viaje_por_id_vehiculo(id):
        return Viaje.query.filter_by(id_vehiculo=id).first()

    @staticmethod
    def obtener_todos_viajes():
        return Viaje.query.all()

    @staticmethod
    def obtener_conteo_viajes_por_vehiculo(id_vehiculo):
        resultado = Viaje.query.filter_by(
            id_vehiculo=id_vehiculo
        ).add_columns(
            func.count(Viaje.id_viaje)
        ).first()
        # scalar convierte listas tuples por join en listas de objetos de clase
        return resultado

    @staticmethod
    def obtener_viaje_join_vehiculo():
        resultado = Viaje.query.join(
            Vehiculo, Viaje.id_vehiculo == Vehiculo.id_vehiculo
        ).join(
            Fecha, Viaje.id_fecha == Fecha.id_fecha
        ).join(
            Ruta, Ruta.id_ruta == Viaje.id_ruta
        ).add_columns(
            Viaje.id_viaje,
            Fecha.fecha,
            Vehiculo.flota,
            Ruta.codigo,
            Viaje.orden
        ).order_by(
            Fecha.fecha
        ).paginate()
        return resultado

    @staticmethod
    def obtener_por_fecha(idfecha):
        resultado = Viaje.query.join(
            Vehiculo, Viaje.id_vehiculo == Vehiculo.id_vehiculo
        ).join(
            Fecha, Viaje.id_fecha == Fecha.id_fecha
        ).join(
            Ruta, Ruta.id_ruta == Viaje.id_ruta
        ).add_columns(
            Viaje.id_viaje,
            Fecha.fecha,
            Vehiculo.flota,
            Ruta.codigo,
            Viaje.orden
        ).filter(
            Fecha.id_fecha == idfecha
        ).all()
        return resultado

    @staticmethod
    def obtener_orden_ruta(orden: int, vehiculo_id: int, ruta_id: int):
        resultado = Viaje.query.filter_by(
            orden=orden,
            id_ruta=ruta_id,
            id_vehiculo=vehiculo_id
        ).first()
        return resultado

    # Para el analisis de datos
    @staticmethod
    def vista_diaria(fecha: datetime.datetime, ruta_id: int):
        from qhawariy.models.control_tiempo import ControlTiempo
        resultado = Viaje.query.join(
            Ruta, Ruta.id_ruta == Viaje.id_ruta
        ).join(
            Fecha, Fecha.id_fecha == Viaje.id_fecha
        ).join(
            Vehiculo, Vehiculo.id_vehiculo == Viaje.id_vehiculo
        ).join(
            ControlTiempo, ControlTiempo.id_viaje == Viaje.id_viaje
        ).join(
            Control, Control.id_control == ControlTiempo.id_control
        ).where(
            Fecha.fecha == fecha,
            Ruta.id_ruta == ruta_id
        ).all()

        return resultado

    # Estadisticas
    @staticmethod
    def estadistica_viajes_por_vehiculo():
        resultado = Viaje.query.join(
            Vehiculo, Vehiculo.id_vehiculo == Viaje.id_vehiculo
        ).add_columns(
            Vehiculo.flota,
            func.count(Viaje.id_viaje)
        ).group_by(
            Vehiculo.id_vehiculo
        ).all()
        return resultado

    @staticmethod
    def estadistica_viajes_por_fecha_ruta(id_ruta):
        """
        metodo estatico que retorna el total de viajes realizados por fecha dentro
        de un ruta
        """
        resultado = Viaje.query.join(
            Fecha, Fecha.id_fecha == Viaje.id_fecha
        ).join(
            Ruta, Ruta.id_ruta == Viaje.id_ruta
        ).add_columns(
            Fecha.fecha,
            func.count(Viaje.id_viaje),
        ).where(
            Ruta.id_ruta == id_ruta
        ).order_by(
            asc(Fecha.fecha)
        ).group_by(
            Fecha.id_fecha
        ).all()
        return resultado

    @staticmethod
    def estadistica_viajes_por_fecha():
        """
        Funcion que retorna el total de viajes realizados por fecha
        """
        resultado = Viaje.query.join(
            Fecha, Fecha.id_fecha == Viaje.id_fecha
        ).join(
            Ruta, Ruta.id_ruta == Viaje.id_ruta
        ).add_columns(
            Fecha.fecha,
            func.count(Viaje.id_viaje)
        ).order_by(
            asc(Fecha.fecha)
        ).group_by(
            Fecha.id_fecha
        ).all()
        return resultado
