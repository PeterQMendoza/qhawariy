
import datetime
from typing import List
import uuid
import pytz
from qhawariy import db
from qhawariy.utilities.uuid_endpoints import ShortUUID


class Asociado(db.Model):
    __tablename__ = "asociados"
    __table_args__ = {"schema": "app"}

    id_asociado: str = db.Column(
        ShortUUID(),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    id_pv = db.Column(
        ShortUUID(),
        db.ForeignKey("app.propietarios_vehiculos.id_pv", ondelete="CASCADE"),
        nullable=False
    )
    id_usuario = db.Column(
        ShortUUID(),
        db.ForeignKey("app.usuarios.id_usuario", ondelete="CASCADE"),
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
    def obtener_asociado_por_id(id: str):
        return Asociado.query.get(id)

    @staticmethod
    def obtener_todos_asociados() -> List["Asociado"]:
        return Asociado.query.all()  # type: ignore
