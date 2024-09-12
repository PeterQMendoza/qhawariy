import datetime
import pytz

from sqlalchemy import desc
from sqlalchemy.sql import func

from qhawariy import db
from qhawariy.models.ruta import Ruta
from qhawariy.models.fecha import Fecha
from qhawariy.models.ruta_terminal import RutaTerminal
from qhawariy.models.terminal import Terminal

class Programacion(db.Model):
    """Modelo Programacion:
    """
    __tablename__ = "programaciones"
    id_programacion = db.Column(db.Integer,primary_key=True)
    id_fecha = db.Column(db.Integer,db.ForeignKey("fechas.id_fecha"),nullable=False)
    id_ruta = db.Column(db.Integer,db.ForeignKey("rutas.id_ruta"),nullable=False)
    # Establecer relaciones {Table1}*1-->1{Table2}
    ruta = db.relationship("Ruta",back_populates="rutas",uselist=False,single_parent=True)
    fecha = db.relationship("Fecha",back_populates="fecha_programas",uselist=False,single_parent=True)

    programas = db.relationship("VehiculoProgramado",back_populates="programa",cascade="all,delete-orphan")
    programas_viajes=db.relationship("Viaje",back_populates="programa",cascade="all,delete-orphan")

    def __init__(self, id_fecha, id_ruta):
        self.id_fecha=id_fecha
        self.id_ruta=id_ruta

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
    def obtener_programacion_por_id(id):
        return Programacion.query.get(id)

    @staticmethod
    def obtener_todos_programaciones():
        resultado=Programacion.query.all()
        return resultado

    @staticmethod
    def obtener_por_fecha_y_ruta(fecha,ruta):
        return Programacion.query.filter_by(id_fecha=fecha,id_ruta=ruta).first()
    
    @staticmethod
    def obtener_por_fecha(fecha):
        return Programacion.query.filter_by(id_fecha=fecha).first()
    
    @staticmethod
    def obtener_programa_join_ruta():
        """"""
        resultado=Programacion.query.join(
            Programacion,Ruta.id_ruta==Programacion.id_ruta
        ).join(
            RutaTerminal,RutaTerminal.id_ruta==Ruta.id_ruta
        ).join(
            Terminal,Terminal.id_terminal==RutaTerminal.id_terminal
        ).join(
            Fecha,Fecha.id_fecha==Programacion.id_fecha
        ).add_columns(
            Programacion.id_programacion,
            Fecha.fecha,
            Programacion.id_ruta,
            Terminal.direccion,
            Ruta.id_ruta,
            Ruta.codigo
        ).order_by(
            desc(Programacion.id_fecha)
        ).limit(22).all()
        return resultado
    