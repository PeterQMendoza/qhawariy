from typing import Optional, cast
from flask import current_app
from qhawariy.models.rol import Rol
from qhawariy.models.usuario import Usuario
from qhawariy.models.usuario_rol import UsuarioRol


def seed() -> None:
    admin_rol: Optional["Rol"] = cast(
        Rol,
        Rol.query.filter_by(rol="Administrador").first()
    )
    if not admin_rol:
        admin_rol = Rol(rol="Administrador")
        admin_rol.guardar()

    admin_usuario: Optional["Usuario"] = cast(
        Usuario,
        Usuario.query.filter_by(nombres="admin").first()
    )
    if not admin_usuario:
        admin_usuario = Usuario(
            nombres="admin",
            apellidos="admin",
            dni="00000000",
            telefono="944074306",
            correo_electronico="admin@gmail.com"
        )
        admin_usuario.establecer_clave(
            clave=current_app.config['ADMIN_PASSWORD']  # type: ignore
        )
        admin_usuario.guardar()

    admin_rol_usuario: Optional["UsuarioRol"] = cast(
        UsuarioRol,
        UsuarioRol.query.filter_by(
            id_usuario=admin_usuario.id_usuario,
            id_rol=admin_rol.id_rol
        ).first()
    )
    if not admin_rol_usuario:
        admin_rol_usuario = UsuarioRol(
            id_usuario=admin_usuario.id_usuario,
            id_rol=admin_rol.id_rol
        )
        admin_rol_usuario.guardar()


if __name__ == "__main__":
    seed()
