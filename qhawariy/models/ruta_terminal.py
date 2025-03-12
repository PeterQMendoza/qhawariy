from qhawariy import db


class RutaTerminal(db.Model):
    """
    Modelo: Ruta Terminal
    """
    __tablename__ = "rutas_terminales"
    id_r = db.Column(db.Integer, primary_key=True)

    id_ruta = db.Column(db.Integer, db.ForeignKey("rutas.id_ruta"), nullable=False)
    id_terminal = db.Column(
        db.Integer,
        db.ForeignKey("terminales.id_terminal"),
        nullable=False
    )
    id_terminal_2 = db.Column(
        db.Integer,
        db.ForeignKey("terminales.id_terminal"),
        nullable=False
    )

    # Relaciones
    ruta = db.relationship(
        "Ruta",
        back_populates="rutas_terminal",
        uselist=False,
        single_parent=True
    )
    terminal = db.relationship(
        "Terminal",
        foreign_keys=[id_terminal],
        uselist=False,
        single_parent=True
    )
    terminal2 = db.relationship(
        "Terminal",
        foreign_keys=[id_terminal_2],
        uselist=False,
        single_parent=True
    )

    def __init__(self, id_ruta, id_terminal, id_terminal_2):
        self.id_ruta = id_ruta
        self.id_terminal = id_terminal
        self.id_terminal_2 = id_terminal_2

    def __repr__(self):
        return f'<RutaTerminal {self.id_rt}>'

    def guardar(self):
        if not self.id_rt:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_por_terminales(id_terminal1, id_terminal2):
        resultado = RutaTerminal.query.filter_by(
            id_terminal=id_terminal1, id_terminal_2=id_terminal2
        ).first()
        return resultado

    @staticmethod
    def obtener_rt_por_ruta(id_ruta):
        resultado = RutaTerminal.query.filter_by(
            id_ruta=id_ruta
        ).first()
        return resultado

    @staticmethod
    def obtener_todas_rt():
        resultado = RutaTerminal.query.all()
        return resultado
