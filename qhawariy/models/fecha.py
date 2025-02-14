import datetime
import pytz
from sqlalchemy import asc

from qhawariy import db
from qhawariy.utilities.builtins import LIMA_TZ

ahora=datetime.datetime.now(tz=LIMA_TZ)
class Fecha(db.Model):
    """Modelo Fecha: contiene la fecha en la cual de realizan las programaciones, tambien es utilzado para reportar
    los viejas
    """
    __tablename__ = "fechas"
    id_fecha = db.Column(db.Integer,primary_key=True)
    fecha = db.Column(db.DateTime,default=datetime.datetime(year=ahora.year,month=ahora.month,day=ahora.day,hour=0,minute=0,second=0))

    # Relaciones
    fechas_programas = db.relationship("Programacion",back_populates="fecha",cascade="all,delete-orphan")
    fechas_viajes = db.relationship("Viaje",back_populates="fecha",cascade="all,delete-orphan")

    def __init__(self, fecha):
        self.fecha=fecha

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
    def obtener_id(id):
        resultado=Fecha.query.get(id)
        return resultado
    
    @staticmethod
    def obtener_todas_fechas():
        resultado=Fecha.query.all()
        return resultado

    @staticmethod
    def obtener_fecha_por_fecha(fecha):
        resultado=Fecha.query.filter_by(fecha=fecha).first()
        return resultado

    @staticmethod
    def obtener_rango_fecha(ini,fin):
        resultado=Fecha.query.filter(
            Fecha.fecha>=ini
        ).filter(
            Fecha.fecha<=fin
        ).order_by(
            asc(Fecha.fecha)
        ).all()
        return resultado