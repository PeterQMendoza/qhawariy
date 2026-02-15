from typing import Optional
import uuid
from geoalchemy2 import Geometry, WKTElement
from qhawariy import db
from qhawariy.utilities.uuid_endpoints import ShortUUID


class PuntoSalida(db.Model):
    """
    PuntoSalida: Representa los puntos de salida de cada ruta, la programacion de
    horario de salida debe ser considerads desde punto de salida
    """
    __tablename__ = "puntos_salida"
    __table_args__ = {"schema": "app"}

    id_ps: str = db.Column(
        ShortUUID(),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    id_ruta: int = db.Column(
        ShortUUID(),
        db.ForeignKey("app.rutas.id_ruta"),
        nullable=False
    )

    ubicacion = db.Column(
        Geometry(geometry_type="POINT", srid=4326),
        nullable=False
    )

    def __init__(
        self,
        id_ruta: int,
        longitud: float,
        latitud: float
    ) -> None:
        self.id_ruta = id_ruta
        self.ubicacion = WKTElement(f"POINT({longitud} {latitud})", srid=4326)

    def guardar(self) -> None:
        if not self.id_ps:
            db.session.add(self)
        db.session.commit()

    def __repr__(self) -> str:
        return f"<PuntoSalida {self.id_ps}>"

    def eliminar(self) -> None:
        db.session.delete(self)
        db.session.commit()

    def obtener_por_id(self, id: int) -> Optional["PuntoSalida"]:
        return PuntoSalida.query.get(id)
