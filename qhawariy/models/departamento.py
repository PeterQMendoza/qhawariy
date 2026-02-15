from typing import List
import uuid
from qhawariy import db
from qhawariy.utilities.uuid_endpoints import ShortUUID


class Departamento(db.Model):
    """
    Modelo: Departamento
    """
    __tablename__ = "departamentos"
    __table_args__ = {"schema": "app"}

    id_departamento: str = db.Column(
        ShortUUID(),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    nombre = db.Column(db.String(50), nullable=False)

    # Relaciones
    departamentos = db.relationship(
        "Terminal",
        back_populates="departamento",
        cascade="all,delete-orphan"
    )

    def __init__(self, nombre: str):
        self.nombre = nombre

    def __repr__(self):
        return f'<Departamento {self.id_departamento}>'

    def guardar(self):
        if not self.id_departamento:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_todos_departamentos() -> List["Departamento"]:
        return Departamento.query.all()  # type: ignore
