from qhawariy import db

class Terminal(db.Model):
    """Modelo Terminal:
    """
    __tablename__ = "terminales"
    id_terminal = db.Column(db.Integer,primary_key=True)
    direccion=db.Column(db.String(50),nullable=False)
    ubicacion_gps=db.Column(db.String(50),nullable=False)
    id_departamento = db.Column(db.Integer,db.ForeignKey("departamentos.id_departamento"),nullable=False)
    id_provincia = db.Column(db.Integer,db.ForeignKey("provincias.id_provincia"),nullable=False)
    id_distrito = db.Column(db.Integer,db.ForeignKey("distritos.id_distrito"),nullable=False)
    # Relaciones
    departamento = db.relationship("Departamento",back_populates="departamentos",uselist=False,single_parent=True)
    provincia = db.relationship("Provincia",back_populates="provincias",uselist=False,single_parent=True)
    distrito = db.relationship("Distrito",back_populates="distritos",uselist=False,single_parent=True)

    # terminales = db.relationship("RutaTerminal",back_populates="terminal",cascade="all,delete-orphan")
    # terminales2 = db.relationship("RutaTerminal",back_populates="terminal2",cascade="all,delete-orphan")

    def __init__(self, direccion,ubicacion_gps,id_departamento,id_provincia,id_distrito):
        self.direccion=direccion
        self.ubicacion_gps=ubicacion_gps
        self.id_departamento=id_departamento
        self.id_provincia=id_provincia
        self.id_distrito=id_distrito

    def __repr__(self):
        return f'<Terminal {self.id_terminal}>'

    def guardar(self):
        if not self.id_terminal:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_terminal_por_id(id):
        return Terminal.query.get(id)

    @staticmethod
    def obtener_todos_terminales():
        return Terminal.query.all()