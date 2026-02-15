from typing import List, Optional
import uuid

from geoalchemy2 import Geometry, WKTElement
from qhawariy import db
from qhawariy.utilities.gps import GPSMixin
from qhawariy.utilities.uuid_endpoints import ShortUUID


class Terminal(db.Model, GPSMixin):
    """Modelo Terminal:
    """
    __tablename__ = "terminales"
    __table_args__ = {"schema": "app"}

    id_terminal: str = db.Column(
        ShortUUID(),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    direccion: str = db.Column(db.String(50), nullable=False)
    ubicacion = db.Column(
        Geometry(geometry_type="POINT", srid=4326),
        nullable=False
    )
    id_departamento: str = db.Column(
        ShortUUID(),
        db.ForeignKey("app.departamentos.id_departamento"),
        nullable=False
    )
    id_provincia: str = db.Column(
        ShortUUID(),
        db.ForeignKey("app.provincias.id_provincia"),
        nullable=False
    )
    id_distrito: str = db.Column(
        ShortUUID(),
        db.ForeignKey("app.distritos.id_distrito"),
        nullable=False
    )

    # Relaciones
    departamento = db.relationship(
        "Departamento",
        back_populates="departamentos",
        uselist=False,
        single_parent=True
    )
    provincia = db.relationship(
        "Provincia",
        back_populates="provincias",
        uselist=False,
        single_parent=True
    )
    distrito = db.relationship(
        "Distrito",
        back_populates="distritos",
        uselist=False,
        single_parent=True
    )

    def __init__(
        self,
        direccion: str,
        latitud: float,
        longitud: float,
        id_departamento: str,
        id_provincia: str,
        id_distrito: str
    ):
        self.direccion = direccion
        self.ubicacion = WKTElement(f"POINT({longitud} {latitud})", srid=4326)
        self.id_departamento = id_departamento
        self.id_provincia = id_provincia
        self.id_distrito = id_distrito

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
    def obtener_terminal_por_id(id: int) -> Optional["Terminal"]:
        return Terminal.query.get(id)

    @staticmethod
    def obtener_todos_terminales() -> List["Terminal"]:
        return Terminal.query.all()  # type: ignore
