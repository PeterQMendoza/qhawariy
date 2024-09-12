from sqlalchemy import desc,asc
from sqlalchemy.sql import func

from qhawariy import db
from qhawariy.models.vehiculo import Vehiculo
from qhawariy.models.propietario import Propietario

class PropietarioVehiculo(db.Model):
    __tablename__ = "propietarios_vehiculos"
    id_pv = db.Column(db.Integer,primary_key=True)
    id_vehiculo = db.Column(db.Integer,db.ForeignKey("vehiculos.id_vehiculo",ondelete="CASCADE"),nullable=False)
    id_propietario = db.Column(db.Integer,db.ForeignKey("propietarios.id_propietario",ondelete="CASCADE"),nullable=False)

    def __init__(self,id_propietario,id_vehiculo):
        self.id_propietario=id_propietario
        self.id_vehiculo=id_vehiculo

    def __repr__(self):
        return f'<PropietarioVehiculo {self.id_pv}>'

    def guardar(self):
        if not self.id_pv:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_propietario_vehiculo_por_id(id):
        return PropietarioVehiculo.query.get(id)

    @staticmethod
    def obtener_pv_por_id_vehiculo(id):
        return PropietarioVehiculo.query.filter_by(id_vehiculo=id).first()

    @staticmethod
    def obtener_todos_propietario_vehiculo():
        return PropietarioVehiculo.query.all()
    
    @staticmethod
    def obtener_vehiculo_join_propietario():
        resultado=PropietarioVehiculo.query.join(
            Propietario,PropietarioVehiculo.id_propietario==Propietario.id_propietario
        ).add_columns(
            PropietarioVehiculo.id_pv,
            Propietario.id_propietario,
            Propietario.nombres,
            Propietario.apellidos,
            Vehiculo.id_vehiculo,
            Vehiculo.placa,
            Vehiculo.flota
        ).filter(
            Propietario.id_propietario==PropietarioVehiculo.id_propietario
        ).filter(
            Vehiculo.id_vehiculo==PropietarioVehiculo.id_vehiculo
        ).order_by(desc(Vehiculo.flota)).all()
        return resultado

    @staticmethod
    def estadistica_pv_y_vehiculo_propietario(activo):
        resultado=PropietarioVehiculo.query.join(
            Vehiculo,PropietarioVehiculo.id_vehiculo==Vehiculo.id_vehiculo
        ).add_columns(
            Propietario.id_propietario,
            func.count(Vehiculo.id_vehiculo)
        ).filter(
            Propietario.id_propietario==PropietarioVehiculo.id_propietario
        ).where(
            Vehiculo.activo==activo
        ).group_by(
            Propietario.id_propietario
        ).all()
        return resultado
