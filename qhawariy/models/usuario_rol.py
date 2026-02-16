
from typing import List, Optional
import uuid

from qhawariy import db

from qhawariy.models.usuario import Usuario
from qhawariy.models.rol import Rol
from qhawariy.utilities.uuid_endpoints import ShortUUID


class UsuarioRol(db.Model):
    """Modelo UsuarioRol crea una relacion de tablas union entre Usuario y Rol
    """
    __tablename__ = "usuarios_roles"
    __table_args__ = {"schema": "app"}

    id_ur: str = db.Column(
        ShortUUID(),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    id_usuario: str = db.Column(
        ShortUUID(),
        db.ForeignKey("app.usuarios.id_usuario"),
        nullable=False
    )
    id_rol: str = db.Column(
        ShortUUID(),
        db.ForeignKey("app.roles.id_rol"),
        nullable=False
    )

    # Establecer relaciones de uno a muchos
    usuario = db.relationship(
        "Usuario",
        back_populates="uroles",
        uselist=False,
        single_parent=True
    )
    rol = db.relationship(
        "Rol",
        back_populates="rusuarios",
        uselist=False,
        single_parent=True
    )

    def __init__(self, id_usuario: str, id_rol: str):
        self.id_usuario = id_usuario
        self.id_rol = id_rol

    def __repr__(self):
        return f'<UsuarioRol {self.id_ur}>'

    def guardar(self):
        if not self.id_ur:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_ur_por_id(id: uuid.UUID):
        return UsuarioRol.query.get(id)

    @staticmethod
    def obtener_todos_ur() -> List["UsuarioRol"]:
        return UsuarioRol.query.all()  # type: ignore

    @staticmethod
    def obtener_usuarios_por_idrol(idrol: uuid.UUID):
        return UsuarioRol.query.filter_by(id_rol=idrol)

    @staticmethod
    def obtener_por_id_usuario(idusuario: str) -> Optional["UsuarioRol"]:
        return UsuarioRol.query.filter_by(id_usuario=idusuario).first()  # type: ignore

    @staticmethod
    def obtener_rol_join_usuario():
        return (
            UsuarioRol.query.join(
                Usuario,
                UsuarioRol.id_usuario == Usuario.id_usuario  # type: ignore
            ).add_columns(
                Usuario.id_usuario,  # type: ignore
                Usuario.nombres,  # type: ignore
                Usuario.apellidos,  # type: ignore
                Usuario.correo_electronico,  # type: ignore
                Rol.rol  # type: ignore
            ).filter(
                Usuario.id_usuario == UsuarioRol.id_usuario  # type: ignore
            ).filter(Rol.id_rol == UsuarioRol.id_rol)  # type: ignore
            .all()
        )
