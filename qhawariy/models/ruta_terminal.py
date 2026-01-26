from typing import List, Optional
from qhawariy import db


class RutaTerminal(db.Model):
    """
    Modelo: Ruta Terminal
    """
    __tablename__ = "rutas_terminales"
    id_rt: int = db.Column(db.Integer, primary_key=True)

    id_ruta: int = db.Column(db.Integer, db.ForeignKey("rutas.id_ruta"), nullable=False)
    id_terminal: int = db.Column(
        db.Integer,
        db.ForeignKey("terminales.id_terminal"),
        nullable=False
    )
    id_terminal_2: int = db.Column(
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

    def __init__(
        self,
        id_ruta: int,
        id_terminal: int,
        id_terminal_2: int
    ):
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
    def obtener_por_terminales(
        id_terminal1: int,
        id_terminal2: int
    ) -> Optional["RutaTerminal"]:
        return (
            RutaTerminal.query.filter_by(
                id_terminal=id_terminal1,
                id_terminal_2=id_terminal2
            )
            .first()
        )  # type: ignore

    @staticmethod
    def obtener_rt_por_ruta(id_ruta: int) -> Optional["RutaTerminal"]:
        return RutaTerminal.query.filter_by(id_ruta=id_ruta).first()  # type: ignore

    @staticmethod
    def obtener_todas_rt() -> List["RutaTerminal"]:
        return RutaTerminal.query.all()  # type: ignore
