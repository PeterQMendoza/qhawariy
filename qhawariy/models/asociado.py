
import datetime
from typing import List
import pytz
from qhawariy import db


class Asociado(db.Model):
    __tablename__ = "asociados"
    id_asociado = db.Column(db.Integer, primary_key=True)
    id_pv = db.Column(
        db.Integer,
        db.ForeignKey("propietarios_vehiculos.id_pv", ondelete="CASCADE"),
        nullable=False
    )
    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id_usuario", ondelete="CASCADE"),
        nullable=False
    )
    lima_tz = pytz.timezone('America/Lima')
    fecha_registro = db.Column(db.DateTime, default=datetime.datetime.now(tz=lima_tz))

    def __init__(self, id_usuario: int, id_pv: int):
        self.id_usuario = id_usuario
        self.id_pv = id_pv

    def __repr__(self):
        return f'<Asociado {self.id_asociado}>'

    def guadar(self):
        if not self.id_asociado:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_asociado_por_id(id: int):
        return Asociado.query.get(id)

    @staticmethod
    def obtener_todos_asociados() -> List["Asociado"]:
        return Asociado.query.all()  # type: ignore
