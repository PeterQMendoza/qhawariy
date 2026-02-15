from typing import List, Optional
import uuid
from sqlalchemy import desc

from qhawariy import db
from qhawariy.utilities.uuid_endpoints import ShortUUID


class SecuenciaControlRuta(db.Model):
    """ Modelo SecuenciaControlRuta: Establece la secuencia de controles
    dentro de una ruta """
    __tablename__ = 'secuencias_controles_rutas'
    __table_args__ = {"schema": "app"}

    id_scr: str = db.Column(
        ShortUUID(),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    secuencia: int = db.Column(db.Integer, nullable=False)
    id_ruta: int = db.Column(
        ShortUUID(),
        db.ForeignKey('app.rutas.id_ruta'),
        nullable=False
    )
    id_control: int = db.Column(
        ShortUUID(),
        db.ForeignKey('app.controles.id_control'),
        nullable=False
    )

    # Relacion de un a muchos
    ruta = db.relationship(
        "Ruta",
        back_populates="rutas_controles",
        uselist=False,
        single_parent=True,
        lazy=True
    )
    control = db.relationship(
        "Control",
        back_populates="controles_rutas",
        uselist=False,
        single_parent=True,
        lazy=True
    )

    def __init__(self, secuencia: int, id_ruta: int, id_control: int):
        self.secuencia = secuencia
        self.id_ruta = id_ruta
        self.id_control = id_control

    def __repr__(self):
        return f'<SecuenciaControlRuta {self.id_scr}>'

    def guardar(self):
        if not self.id_scr:
            db.session.add(self)
        db.session.commit()

    def eliminar(self) -> None:
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_por_id(scr_id: int) -> Optional["SecuenciaControlRuta"]:
        resultado = SecuenciaControlRuta.query.get(scr_id)
        return resultado

    @staticmethod
    def obtener_todos() -> List["SecuenciaControlRuta"]:
        return SecuenciaControlRuta.query.all()  # type: ignore

    @staticmethod
    def obtener_secuencia_por_ruta(ruta_id: int) -> Optional["SecuenciaControlRuta"]:
        return (
            SecuenciaControlRuta.query.filter_by(
                id_ruta=ruta_id
            )
            .order_by(desc(SecuenciaControlRuta.secuencia))  # type: ignore
            .first()
        )  # type: ignore

    @staticmethod
    def obtener_todos_secuencia_por_ruta(ruta_id: int) -> List["SecuenciaControlRuta"]:
        return (
            SecuenciaControlRuta.query.filter_by(
                id_ruta=ruta_id
            ).order_by(
                desc(SecuenciaControlRuta.secuencia)  # type: ignore
            ).all()
        )  # type: ignore
