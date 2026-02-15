from typing import List
import uuid

from qhawariy import db
from qhawariy.utilities.uuid_endpoints import ShortUUID


class PlanSalida(db.Model):
    __tablename__ = "planes_salidas"
    __table_args__ = {"schema": "app"}

    id_ps: str = db.Column(
        ShortUUID(),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    id_usuario = db.Column(
        ShortUUID(),
        db.ForeignKey("app.usuarios.id_usuario", ondelete="CASCADE"),
        nullable=False
    )
    id_vp = db.Column(
        ShortUUID(),
        db.ForeignKey("app.vehiculos_programados.id_vehiculo", ondelete="CASCADE"),
        nullable=False
    )

    def __init__(self, id_usuario: int, id_vp: int):
        self.id_usuario = id_usuario
        self.id_vp = id_vp

    def __repr__(self):
        return f'<PlanSalida {self.id_ps}>'

    def guadar(self):
        if not self.id_ps:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_plan_salida_por_id(id: int):
        return PlanSalida.query.get(id)

    @staticmethod
    def obtener_todos_plan_salida() -> List["PlanSalida"]:
        return PlanSalida.query.all()  # type: ignore
