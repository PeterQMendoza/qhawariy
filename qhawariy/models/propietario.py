# import datetime
# import pytz

from qhawariy import db
from sqlalchemy.sql import asc


class Propietario(db.Model):
    __tablename__ = "propietarios"
    id_propietario = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(50), nullable=False)
    apellidos = db.Column(db.String(50), nullable=False)
    telefono = db.Column(db.String(15), nullable=False)
    documento_identificacion = db.Column(db.String(15), nullable=False)

    def __init__(self, nombres, apellidos, telefono, documento_identificacion):
        self.nombres = nombres
        self.apellidos = apellidos
        self.telefono = telefono
        self.documento_identificacion = documento_identificacion

    def __repr__(self):
        return f'<Propietario {self.id_propietario}>'

    def guardar(self):
        if not self.id_propietario:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_propietario_por_id(id):
        return Propietario.query.get(id)

    @staticmethod
    def obtener_propietario_por_dni(dni):
        return Propietario.query.filter_by(documento_identificacion=dni).first()

    @staticmethod
    def obtener_propietario_por_apellidos(apellido):
        return Propietario.query.filter_by(apellidos=apellido).first()

    @staticmethod
    def obtener_todos_propietarios():
        return Propietario.query.order_by(asc(Propietario.apellidos)).all()

    @staticmethod
    def buscar_propietarios_dni(dni):
        return Propietario.query.filter_by(documento_identificacion=dni).all()
