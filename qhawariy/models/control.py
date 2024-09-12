from qhawariy import db

class Control(db.Model):
    """
    Modelo Control:
    Almacena todos los puntos de control de horarios
    de los vehiculos
    """
    __tablename__='controles'
    id_control=db.Column(db.Integer,primary_key=True)
    codigo=db.Column(db.String(8),unique=True,nullable=False)
    ubicacion=db.Column(db.String(50),nullable=True)

    controles=db.relationship("ControlTiempo",back_populates="control",cascade="all,delete-orphan")

    def __init__(self,codigo,ubicacion):
        self.codigo=codigo
        self.ubicacion=ubicacion

    def __repr__(self):
        return f"<Control {self.codigo}>"
    
    def guardar(self):
        if not self.id_control:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_id(id):
        resultado=Control.query.get(id)
        return resultado
    
    @staticmethod
    def obtener_todos():
        resultado=Control.query.all()
        return resultado
    
    @staticmethod
    def obtener_por_codigo(codigo):
        resultado=Control.query.filter_by(codigo=codigo).first()
        return resultado
    