from qhawariy import db

class Distrito(db.Model):
    """Modelo Distrito:
    """
    __tablename__ = "distritos"
    id_distrito=db.Column(db.Integer,primary_key=True)
    nombre=db.Column(db.String(50),nullable=False)

    # Relaciones
    distritos=db.relationship("Terminal",back_populates="distrito",cascade="all,delete-orphan")

    def __init__(self,nombre):
        self.nombre=nombre

    def __repr__(self):
        return f'<Distrito {self.id_distrito}>'

    def guardar(self):
        if not self.id_distrito:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_todos_distritos():
        return Distrito.query.all()