
import datetime
import pytz

from sqlalchemy import (asc,desc)
from sqlalchemy.sql import func

from qhawariy import db
from qhawariy.models.ruta_terminal import RutaTerminal
from qhawariy.models.terminal import Terminal
from qhawariy.models.vehiculo import Vehiculo
from qhawariy.models.ruta import Ruta
from qhawariy.models.programacion import Programacion
from qhawariy.models.fecha import Fecha
from qhawariy.utilities.builtins import LIMA_TZ

class VehiculoProgramado(db.Model):
    """Modelo VehiculoProgramado
    """
    __tablename__ = "vehiculos_programados"
    id_vp = db.Column(db.Integer,primary_key=True)
    tiempo=db.Column(db.Time,default=datetime.datetime.now(tz=LIMA_TZ).time())
    id_vehiculo = db.Column(db.Integer,db.ForeignKey("vehiculos.id_vehiculo"),nullable=False)
    id_programacion = db.Column(db.Integer,db.ForeignKey("programaciones.id_programacion"),nullable=False)

    # Establecer relaciones {Table1}*1-->1{Table2}
    vehiculo = db.relationship("Vehiculo",back_populates="vehiculos",uselist=False,single_parent=True)
    programa = db.relationship("Programacion",back_populates="programas",uselist=False,single_parent=True)

    #Establecer relacion inversa {Tabla2}*1-->1{Tabla1}

    def __init__(self,tiempo, id_vehiculo, id_programacion):
        self.tiempo=tiempo
        self.id_vehiculo=id_vehiculo
        self.id_programacion=id_programacion


    def __repr__(self):
        return f'<VehiculoProgramado {self.id_vp}>'

    def guardar(self):
        if not self.id_vp:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_vp_por_id(id):
        return VehiculoProgramado.query.get(id)

    @staticmethod
    def obtener_vp_por_id_vehiculo(id_vehiculo):
        return VehiculoProgramado.query.filter_by(id_vehiculo=id_vehiculo).first()

    @staticmethod
    def obtener_vp_por_programacion_y_id_vehiculo(programacion_id,vehiculo_id):
        return VehiculoProgramado.query.filter_by(id_programacion=programacion_id,id_vehiculo=vehiculo_id).first()
    
    @staticmethod
    def obtener_vp_por_programacion_y_tiempo(tiempo,programacion_id):
        return VehiculoProgramado.query.filter_by(tiempo=tiempo,id_programacion=programacion_id).first()

    @staticmethod
    def obtener_todos_vp():
        return VehiculoProgramado.query.all()

    @staticmethod
    def obtener_todos_vp_por_programa(id_programa):
        resultado=VehiculoProgramado.query.filter_by(id_programacion=id_programa).all()
        return resultado

    @staticmethod
    def obtener_todos_vp_fecha(desde,hasta):
        resultado=VehiculoProgramado.query.join(
            Programacion,Programacion.id_programacion==VehiculoProgramado.id_programacion
        ).join(
            Fecha,Fecha.id_fecha==Programacion.id_fecha
        ).filter(
            desde<=Fecha.fecha,hasta>=Fecha.fecha
        ).order_by(
            desc(Fecha.fecha)
        ).all()
        return resultado

    @staticmethod
    def obtener_vp_ultimo():
        resultado=VehiculoProgramado.query.join(
            Programacion,Programacion.id_programacion==VehiculoProgramado.id_programacion
        ).join(
            Fecha,Fecha.id_fecha==Programacion.id_fecha
        ).order_by(
            desc(Fecha.fecha)
        ).first()
        return resultado

        
    @staticmethod
    def obtener_fecha_tiempo_flota_placa():
        resultado=VehiculoProgramado.query.join(
            Programacion,VehiculoProgramado.id_programacion==Programacion.id_programacion
        ).add_columns(
            Programacion.fecha_programa,
            Vehiculo.flota,
            Vehiculo.placa
        ).filter(
            VehiculoProgramado.id_vehiculo==Vehiculo.id_vehiculo
        ).all()
        return resultado
        
    @staticmethod
    def obtener_vp_y_vehiculo(id):
        resultado=VehiculoProgramado.query.filter_by(
            id_programacion=id
        ).join(
            Vehiculo,VehiculoProgramado.id_vehiculo==Vehiculo.id_vehiculo
        ).add_columns(
            VehiculoProgramado.tiempo,
            Vehiculo.flota
        ).order_by(asc(VehiculoProgramado.tiempo)).all()
        return resultado
    
    @staticmethod
    def obtener_vp_join_vehiculo(id):
        resultado=VehiculoProgramado.query.filter_by(
            id_programacion=id
        ).join(
            Vehiculo,VehiculoProgramado.id_vehiculo==Vehiculo.id_vehiculo
        ).add_columns(
            VehiculoProgramado.id_vp,
            VehiculoProgramado.id_programacion,
            VehiculoProgramado.tiempo,
            Vehiculo.id_vehiculo,
            Vehiculo.flota,
            Vehiculo.placa
        ).filter(
            VehiculoProgramado.id_vehiculo==Vehiculo.id_vehiculo
        ).filter(
            VehiculoProgramado.id_programacion==Programacion.id_programacion
        ).order_by(asc(VehiculoProgramado.tiempo)).all()
        return resultado
        
    @staticmethod
    def buscar_vehiculo_por_programacion(id_vehiculo):
        resultado=VehiculoProgramado.query.add_columns(
            Programacion.fecha_programa,
            VehiculoProgramado.tiempo,
            Ruta.codigo,
            func.count(VehiculoProgramado.id_vp)
        ).filter(
            VehiculoProgramado.id_programacion==Programacion.id_programacion
        ).filter(
            VehiculoProgramado.id_vehiculo==Vehiculo.id_vehiculo
        ).filter(
            Ruta.id_ruta==Programacion.id_ruta
        ).where(
            Vehiculo.id_vehiculo==id_vehiculo
        ).group_by(
            Programacion.fecha_programa
        )

        return resultado

    # Para Estadisticas
    @staticmethod
    def estadistica_vp_fecha_programa():
        resultado=VehiculoProgramado.query.join(
            Programacion,Programacion.id_programacion==VehiculoProgramado.id_programacion
        ).join(
            Fecha,Programacion.id_fecha==Fecha.id_fecha
        ).add_columns(
            Fecha.fecha,
            func.count(VehiculoProgramado.id_vehiculo)
        ).order_by(
            asc(Fecha.fecha)
        ).group_by(Fecha.fecha).all()
        return resultado
        
    @staticmethod
    def estadistica_vp_flota_programa():
        resultado=VehiculoProgramado.query.join(
            Vehiculo,VehiculoProgramado.id_vehiculo==Vehiculo.id_vehiculo
        ).add_columns(
            Vehiculo.flota,
            func.ifnull(func.count(Vehiculo.id_vehiculo),0)
        ).filter(
            VehiculoProgramado.id_vehiculo==Vehiculo.id_vehiculo
        ).order_by(
            desc(Vehiculo.flota)
        ).group_by(Vehiculo.flota).all()
        return resultado
    
    
    @staticmethod
    def estadistica_vp_fecha_programado_no_programado():
        resultado=VehiculoProgramado.query.join(
            Programacion,VehiculoProgramado.id_programacion==Programacion.id_programacion
        ).join(
            Fecha,Fecha.id_fecha==Programacion.id_fecha
        ).add_columns(
            func.max(Fecha.fecha),
            func.count(VehiculoProgramado.id_vehiculo)
        ).filter(
            VehiculoProgramado.id_programacion==Programacion.id_programacion
        ).all()
        return resultado

#
    @staticmethod
    def estadistica_cantidad_vehiculos_por_ruta():
        resultado=VehiculoProgramado.query.join(
            Programacion,VehiculoProgramado.id_programacion==Programacion.id_programacion
        ).join(
            Ruta,Ruta.id_ruta==Programacion.id_ruta
        ).join(
            RutaTerminal,RutaTerminal.id_ruta==Ruta.id_ruta
        ).add_columns(
            Ruta.codigo,
            func.count(VehiculoProgramado.id_vp)
        ).group_by(
            Ruta.id_ruta
        ).order_by(
            Ruta.id_ruta
        ).all()
        return resultado
    
       
    @staticmethod
    def estadistica_vp_fecha_programa_y_ruta(ruta):
        resultado=VehiculoProgramado.query.join(
            Programacion,VehiculoProgramado.id_programacion==Programacion.id_programacion
        ).join(
            Ruta,Ruta.id_ruta==Programacion.id_ruta
        ).join(
            Fecha,Fecha.id_fecha==Programacion.id_fecha
        ).add_columns(
            Fecha.fecha,
            func.count(VehiculoProgramado.id_vehiculo)
        ).where(
            Ruta.id_ruta==ruta
        ).order_by(
            asc(Fecha.fecha)
        ).group_by(Fecha.fecha).all()
        return resultado

    @staticmethod
    def estadistica_vp_tiempos():
        resultado=VehiculoProgramado.query.add_columns(
            VehiculoProgramado.tiempo,
            func.count(VehiculoProgramado.tiempo)
        ).order_by(
            asc(VehiculoProgramado.tiempo)
        ).group_by(
            VehiculoProgramado.tiempo
        ).all()
        return resultado

