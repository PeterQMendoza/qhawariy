import datetime
from qhawariy import db
from qhawariy.models.control import Control
from qhawariy.models.fecha import Fecha
from qhawariy.models.ruta import Ruta
from qhawariy.models.vehiculo import Vehiculo
from qhawariy.models.viaje import Viaje

class ControlTiempo(db.Model):
    """
    Modelo ControlTiempo: Contiene los tiempos de los vehiculos a pasar por los puntos de control

    """
    __tablename__='controles_tiempos'
    id_ct=db.Column(db.Integer,primary_key=True)
    tiempo=db.Column(db.Time,nullable=False)
    id_control=db.Column(db.Integer,db.ForeignKey('controles.id_control'),nullable=False)
    id_viaje=db.Column(db.Integer,db.ForeignKey('viajes.id_viaje'),nullable=False)

    control=db.relationship("Control",back_populates="controles",uselist=False,single_parent=True)
    viaje=db.relationship("Viaje",back_populates="viajes",uselist=False,single_parent=True,lazy=True)

    def __init__(self,tiempo,id_control,id_viaje):
        self.tiempo=tiempo
        self.id_control=id_control
        self.id_viaje=id_viaje

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
    def obtener_por_id(id):
        resultado=ControlTiempo.query.get(id)
        return resultado
    
    @staticmethod
    def obtener_todos():
        resultado=ControlTiempo.query.all()
        return resultado
    
    @staticmethod
    def obtener_por_cantidad_registros(cantidad):
        resultado=ControlTiempo.query.limit(cantidad).all()
        return resultado
    
    @staticmethod
    def obtener_por_viaje(id_viaje):
        resultado=ControlTiempo.query.filter_by(id_viaje=id_viaje).all()
        return resultado
    
    @staticmethod
    def vista_diaria(date:datetime.datetime,ruta_id:int):
        resultado=ControlTiempo.query.join(
            Viaje,Viaje.id_viaje==ControlTiempo.id_viaje
        ).join(
            Control,Control.id_control==ControlTiempo.id_control
        ).join(
            Fecha,Fecha.id_fecha==Viaje.id_fecha
        ).join(
            Ruta,Ruta.id_ruta==Viaje.id_ruta
        ).join(
            Vehiculo,Vehiculo.id_vehiculo==Viaje.id_vehiculo
        ).where(
            Ruta.id_ruta==ruta_id,
            Fecha.fecha==date
        ).all()

        return resultado