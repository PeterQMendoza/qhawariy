from qhawariy import db


class ProximaRuta(db.Model):
    """
    Modelo ProximaRuta
    """
    __tablename__ = "proximas_rutas"
    id_pr = db.Column(db.Integer, primary_key=True)
    id_ruta = db.Column(db.Integer, db.ForeignKey("rutas.id_ruta"), nullable=False)
    id_ruta2 = db.Column(db.Integer, db.ForeignKey("rutas.id_ruta"), nullable=True)

    # Relacion entre tablas
    actual = db.relationship(
        "Ruta",
        foreign_keys=[id_ruta],
        uselist=False,
        single_parent=True
    )
    proxima = db.relationship(
        "Ruta",
        foreign_keys=[id_ruta2],
        uselist=False,
        single_parent=True
    )

    def __init__(self, id_ruta: int, id_ruta2: int | None):
        self.id_ruta = id_ruta
        if id_ruta2 is not None:
            self.id_ruta2 = id_ruta2

    def __repr__(self):
        return f"<ProximaRuta {self.id_pr}>"

    # Getters
    @property
    def ruta_proxima(self):
        return self.id_ruta2

    # Setters
    @ruta_proxima.setter
    def ruta_proxima(self, nueva_ruta_proxima: int):
        self.id_ruta2 = nueva_ruta_proxima

    def guardar(self):
        if not self.id_pr:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_por_ruta_actual(ruta_id: int):
        resultado = ProximaRuta.query.filter_by(id_ruta=ruta_id).first()
        return resultado
