from qhawariy import db


class Provincia(db.Model):
    """
    Modelo: Provincia
    """
    __tablename__ = "provincias"

    id_provincia = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)

    # Relaciones
    provincias = db.relationship(
        "Terminal",
        back_populates="provincia",
        cascade="all,delete-orphan"
    )

    def __init__(self, nombre):
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
    def obtener_todos_provincias():
        return Provincia.query.all()
