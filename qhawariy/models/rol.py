from qhawariy import db


class Rol(db.Model):
    """Modelo Rol describe el rol que se asignara al usuario
    """
    __tablename__ = "roles"
    id_rol = db.Column(db.Integer, primary_key=True)
    rol = db.Column(db.String(20), unique=True, nullable=False)
    # Relaciones
    rusuarios = db.relationship(
        "UsuarioRol",
        back_populates="rol",
        cascade="all,delete-orphan"
    )

    def __init__(self, rol):
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
    def obtener_rol_por_id(id):
        return Rol.query.get(id)

    @staticmethod
    def obtener_todos_roles():
        return Rol.query.all()

    @staticmethod
    def obtener_por_rol(rol):
        return Rol.query.filter_by(rol=rol).first()
