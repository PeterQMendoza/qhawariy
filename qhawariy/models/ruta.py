import datetime
from typing import List, Optional
import pytz
from qhawariy import db


class Ruta(db.Model):
    """Modelo Ruta:
    """
    __tablename__ = "rutas"
    id_ruta: int = db.Column(db.Integer, primary_key=True)
    codigo: str = db.Column(db.String(8), unique=True, nullable=False)
    lima_tz = pytz.timezone('America/Lima')
    inicio_vigencia: datetime.datetime = db.Column(
        db.DateTime,
        default=datetime.datetime.now(lima_tz),
        nullable=False
    )
    fin_vigencia = db.Column(
        db.DateTime,
        default=datetime.datetime.now(lima_tz),
        nullable=False
    )
    documento: str = db.Column(db.String(300), nullable=False)

    # Relaciones de muchos a uno
    rutas_programas = db.relationship(
        "Programacion",
        back_populates="ruta",
        cascade="all,delete-orphan"
    )
    rutas_viajes = db.relationship(
        "Viaje",
        back_populates="ruta",
        cascade="all,delete-orphan"
    )
    rutas_terminal = db.relationship(
        "RutaTerminal",
        back_populates="ruta",
        cascade="all,delete-orphan"
    )
    rutas_controles = db.relationship(
        "SecuenciaControlRuta",
        back_populates="ruta",
        cascade="all,delete-orphan"
    )

    def __init__(
        self,
        codigo: str,
        inicio_vigencia: datetime.datetime,
        fin_vigencia: datetime.datetime,
        documento: str
    ):
        self.codigo = codigo
        self.inicio_vigencia = inicio_vigencia
        self.fin_vigencia = fin_vigencia
        self.documento = documento

    def __repr__(self):
        return f'<Ruta {self.id_ruta}>'

    def guardar(self):
        if not self.id_ruta:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_ruta_por_id(id: int) -> Optional["Ruta"]:
        return Ruta.query.get(id)

    # @staticmethod
    # def obtener_ruta_por_direccion_destino_origen(
    #     direccion_origen,
    #     direccion_destino
    # ):
    #     return Ruta.query.filter_by(
    #         direccion_destino=direccion_destino,
    #         direccion_origen=direccion_origen
    #     ).first()

    @staticmethod
    def obtener_todos_rutas() -> List["Ruta"]:
        return Ruta.query.all()  # type: ignore
