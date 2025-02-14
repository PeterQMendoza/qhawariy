import datetime

from qhawariy import db
from qhawariy.models.vehiculo import Vehiculo
from qhawariy.utilities.builtins import LIMA_TZ

ahora=datetime.datetime.now(LIMA_TZ)
class DisponibleVehiculo(db.Model):
    """
    Clase DisponibleVehiculo: Establece control de la disponibilidad de vehiculos
    de acuerdo a un requerimiento de cantidad de vehiculos a programar

    La disponibilidad del vehiculo esta determinado de acuerdo al tiempo_inicio
    hasta el tiempo_final, referido al tiempo que el vehiculo esta con permiso
    y por lo cual no estara disponible por esos dias
    """

    __tablename__="disponibles_vehiculos"
    id_dv=db.Column(db.Integer,primary_key=True)
    fecha_inicio=db.Column(db.DateTime,default=datetime.datetime(year=ahora.year,month=ahora.month,day=ahora.day,hour=0,minute=0,second=0),nullable=False)
    fecha_final=db.Column(db.DateTime,default=datetime.datetime(year=ahora.year,month=ahora.month,day=ahora.day,hour=0,minute=0,second=0),nullable=False)# por defecto un dia
    id_vehiculo=db.Column(db.Integer,db.ForeignKey('vehiculos.id_vehiculo',ondelete='CASCADE'),nullable=False)

    # Relaciones
    vehiculo=db.relationship("Vehiculo",back_populates="vehiculos_disponibles",uselist=False,single_parent=True)

    def __init__(self,fecha_inicio:datetime.datetime,fecha_final:datetime.datetime,id_vehiculo:int) -> None:
        self.fecha_inicio=fecha_inicio
        self.fecha_final=fecha_final
        self.id_vehiculo=id_vehiculo

    def __repr__(self) -> str:
        return f"<DisponibleVehiculo {self.id_dv}>"
    
    def guardar(self)->None:
        if not self.id_dv:
            db.session.add(self)
        db.session.commit()

    def eliminar(self)->None:
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_id(id):
        resultado=DisponibleVehiculo.query.get(id)
        return resultado

    @staticmethod
    def obtener_todos():
        resultado=DisponibleVehiculo.query.all()
        return resultado

    @staticmethod
    def busca_fecha(desde,hasta):
        resultado=DisponibleVehiculo.query.filter(
            desde>=DisponibleVehiculo.fecha_inicio,
            hasta<=DisponibleVehiculo.fecha_final
        ).all()
        return resultado
    
    @staticmethod
    def busca_vehiculo_flota(flota):
        resultado=DisponibleVehiculo.query.join(
            Vehiculo,DisponibleVehiculo.id_vehiculo==Vehiculo.id_vehiculo
        ).where(
            Vehiculo.flota==flota
        ).all()
        return resultado
    
    @staticmethod
    def obtener_vehiculos_disponibles(fecha:datetime.datetime):
        resultado=DisponibleVehiculo.query.filter(
            fecha>=DisponibleVehiculo.fecha_inicio,
            fecha<=DisponibleVehiculo.fecha_final
        ).all()
        return resultado

