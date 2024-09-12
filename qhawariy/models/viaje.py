import datetime
import pytz

from sqlalchemy import (asc,desc)
from sqlalchemy.sql import func

from qhawariy import db
from qhawariy.models.fecha import Fecha
from qhawariy.models.programacion import Programacion
from qhawariy.models.ruta import Ruta
from qhawariy.models.vehiculo import Vehiculo

class Viaje(db.Model):
    """" Modelo Viaje
    """
    __tablename__ = "viajes"
    id_viaje = db.Column(db.Integer,primary_key=True)
    id_vehiculo=db.Column(db.Integer,db.ForeignKey("vehiculos.id_vehiculo"),nullable=False)
    id_programacion = db.Column(db.Integer,db.ForeignKey("programaciones.id_programacion"),nullable=False)
    orden=db.Column(db.Integer,nullable=False)

    # Relaciones 
    programa=db.relationship("Programacion",back_populates="programas_viajes",uselist=False,single_parent=True)

    # Relaciones
    viajes=db.relationship("ControlTiempo",back_populates="viaje",cascade="all,delete-orphan")

    def __init__(self,id_vehiculo,id_programacion,orden):
        self.orden=orden
        self.id_vehiculo=id_vehiculo
        self.id_programacion=id_programacion

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
    def obtener_conteo_viajes_por_vehiculo_programa(id_vehiculo,id_programa):
        resultado=Viaje.query.filter_by(
            id_vehiculo=id_vehiculo,
            id_programacion=id_programa
        ).add_columns(
            func.count(Viaje.id_viaje)
        ).first()# scalar convierte listas tuples por join en listas de objetos de clase
        return resultado
    
        
    @staticmethod
    def obtener_viaje_join_vehiculo():
        resultado=Viaje.query.join(
            Vehiculo,Viaje.id_vehiculo==Vehiculo.id_vehiculo
        ).join(
            Programacion,Viaje.id_programacion==Programacion.id_programacion
        ).join(
            Fecha,Programacion.id_fecha==Fecha.id_fecha
        ).join(
            Ruta,Ruta.id_ruta==Programacion.id_ruta
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
        resultado=Viaje.query.join(
            Vehiculo,Viaje.id_vehiculo==Vehiculo.id_vehiculo
        ).join(
            Programacion,Viaje.id_programacion==Programacion.id_programacion
        ).join(
            Fecha,Programacion.id_fecha==Fecha.id_fecha
        ).join(
            Ruta,Ruta.id_ruta==Programacion.id_ruta
        ).add_columns(
            Viaje.id_viaje,
            Fecha.fecha,
            Vehiculo.flota,
            Ruta.codigo,
            Viaje.orden
        ).filter(
            Fecha.id_fecha==idfecha
        ).all()
        return resultado
    
    @staticmethod
    def obtener_orden_programa(orden,id_programacion):
        resultado=Viaje.query.filter_by(
            orden=orden,
            id_programacion=id_programacion
        ).first()
        return resultado
    
    # Estadisticas
    @staticmethod
    def estadistica_viajes_por_vehiculo():
        resultado=Viaje.query.join(
            Programacion,Programacion.id_programacion==Viaje.id_programacion
        ).join(
            Vehiculo,Vehiculo.id_vehiculo==Viaje.id_vehiculo
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
        metodo estatico que retorna el total de viajes realizados por fecha dentro de un ruta
        """
        resultado=Viaje.query.join(
            Programacion,Programacion.id_programacion==Viaje.id_programacion
        ).join(
            Fecha,Fecha.id_fecha==Programacion.id_fecha
        ).join(
            Ruta,Ruta.id_ruta==Programacion.id_ruta
        ).add_columns(
            Fecha.fecha,
            func.count(Viaje.id_viaje),
        ).where(
            Ruta.id_ruta==id_ruta
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
        resultado=Viaje.query.join(
            Programacion,Programacion.id_programacion==Viaje.id_programacion
        ).join(
            Fecha,Fecha.id_fecha==Programacion.id_fecha
        ).join(
            Ruta,Ruta.id_ruta==Programacion.id_ruta
        ).add_columns(
            Fecha.fecha,
            func.count(Viaje.id_viaje)
        ).order_by(
            asc(Fecha.fecha)
        ).group_by(
            Fecha.id_fecha
        ).all()
        return resultado