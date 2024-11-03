
from qhawariy import db

from qhawariy.models.usuario import Usuario
from qhawariy.models.rol import Rol

class UsuarioRol(db.Model):
    """Modelo UsuarioRol crea una relacion de tablas union entre Usuario y Rol
    """
    __tablename__ = "usuarios_roles"
    id_ur = db.Column(db.Integer,primary_key=True)
    id_usuario = db.Column(db.Integer,db.ForeignKey("usuarios.id_usuario"),nullable=False)
    id_rol = db.Column(db.Integer,db.ForeignKey("roles.id_rol"),nullable=False)
    # Establecer relaciones de uno a muchos
    usuario = db.relationship("Usuario",back_populates="uroles",uselist=False,single_parent=True)
    rol = db.relationship("Rol",back_populates="rusuarios",uselist=False,single_parent=True)

    def __init__(self, id_usuario, id_rol):
        self.id_usuario=id_usuario
        self.id_rol=id_rol

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
    def obtener_ur_por_id(id):
        return UsuarioRol.query.get(id)

    @staticmethod
    def obtener_todos_ur():
        return UsuarioRol.query.all()

    @staticmethod
    def obtener_usuarios_por_idrol(idrol):
        return UsuarioRol.query.filter_by(id_rol=idrol)

    @staticmethod
    def obtener_por_id_usuario(idusuario):
        return UsuarioRol.query.filter_by(id_usuario=idusuario).first()

    @staticmethod
    def obtener_rol_join_usuario():
        resultado=UsuarioRol.query.join(Usuario,UsuarioRol.id_usuario==Usuario.id_usuario).add_columns(Usuario.id_usuario,Usuario.nombres,Usuario.apellidos,Usuario.correo_electronico,Rol.rol).filter(Usuario.id_usuario==UsuarioRol.id_usuario).filter(Rol.id_rol==UsuarioRol.id_rol).all()
        return resultado