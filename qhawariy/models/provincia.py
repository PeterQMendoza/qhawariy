from typing import List
import uuid
from qhawariy import db
from qhawariy.utilities.uuid_endpoints import ShortUUID


class Provincia(db.Model):
    """
    Modelo: Provincia
    """
    __tablename__ = "provincias"
    __table_args__ = {"schema": "app"}

    id_provincia: str = db.Column(
        ShortUUID(),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    nombre: str = db.Column(db.String(50), nullable=False)

    # Relaciones
    provincias = db.relationship(
        "Terminal",
        back_populates="provincia",
        cascade="all,delete-orphan"
    )

    def __init__(self, nombre: str):
        self.nombre = nombre

    def __repr__(self):
        return f'<Provincia {self.nombre}>'

    def guardar(self):
        if not self.id_provincia:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_todos_provincias() -> List["Provincia"]:
        return Provincia.query.all()  # type: ignore
