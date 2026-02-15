from typing import List, Optional
import uuid
from qhawariy import db
from qhawariy.utilities.uuid_endpoints import ShortUUID


class Rol(db.Model):
    """Modelo Rol describe el rol que se asignara al usuario
    """
    __tablename__ = "roles"
    __table_args__ = {"schema": "app"}

    id_rol: uuid.UUID = db.Column(
        ShortUUID(),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    rol: str = db.Column(db.String(20), unique=True, nullable=False)
    # Relaciones
    rusuarios = db.relationship(
        "UsuarioRol",
        back_populates="rol",
        cascade="all,delete-orphan"
    )

    def __init__(self, rol: str):
        self.rol = rol

    def __repr__(self):
        return f'<Rol {self.id_rol}>'

    def guardar(self):
        if not self.id_rol:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_rol_por_id(id: uuid.UUID):
        return Rol.query.get(id)

    @staticmethod
    def obtener_todos_roles() -> List["Rol"]:
        return Rol.query.all()  # type: ignore

    @staticmethod
    def obtener_por_rol(rol: str) -> Optional["Rol"]:
        return Rol.query.filter_by(rol=rol).first()  # type: ignore
