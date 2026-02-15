from typing import List, Optional, Tuple
import uuid
from sqlalchemy import desc
from sqlalchemy.sql import func

from qhawariy import db
from qhawariy.models.vehiculo import Vehiculo
from qhawariy.models.propietario import Propietario
from qhawariy.utilities.uuid_endpoints import ShortUUID


class PropietarioVehiculo(db.Model):
    __tablename__ = "propietarios_vehiculos"
    __table_args__ = {"schema": "app"}

    id_pv: str = db.Column(
        ShortUUID(),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    id_vehiculo: str = db.Column(
        ShortUUID(),
        db.ForeignKey("app.vehiculos.id_vehiculo", ondelete="CASCADE"),
        nullable=False
    )
    id_propietario: str = db.Column(
        ShortUUID(),
        db.ForeignKey("app.propietarios.id_propietario", ondelete="CASCADE"),
        nullable=False
    )

    def __init__(self, id_propietario: str, id_vehiculo: str):
        self.id_propietario = id_propietario
        self.id_vehiculo = id_vehiculo

    def __repr__(self):
        return f'<PropietarioVehiculo {self.id_pv}>'

    def guardar(self):
        if not self.id_pv:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_propietario_vehiculo_por_id(id: int):
        return PropietarioVehiculo.query.get(id)

    @staticmethod
    def obtener_pv_por_id_vehiculo(id: int) -> Optional["PropietarioVehiculo"]:
        return (
            PropietarioVehiculo.query
            .filter_by(id_vehiculo=id)
            .first()
        )  # type: ignore

    @staticmethod
    def obtener_todos_propietario_vehiculo() -> List["PropietarioVehiculo"]:
        return PropietarioVehiculo.query.all()  # type: ignore

    @staticmethod
    def obtener_vehiculo_join_propietario() -> List[Tuple[
        int,
        int,
        str,
        int,
        str,
        str
    ]]:
        return (
            db.session.query(
                PropietarioVehiculo.id_pv,  # type: ignore
                Propietario.id_propietario,   # type: ignore
                Propietario.nombres,   # type: ignore
                Propietario.apellidos,   # type: ignore
                Vehiculo.id_vehiculo,   # type: ignore
                Vehiculo.placa,   # type: ignore
                Vehiculo.flota   # type: ignore
            )
            .join(
                Propietario,
                PropietarioVehiculo.id_propietario == Propietario.id_propietario  # type: ignore
            )
            .filter(
                Vehiculo.id_vehiculo == PropietarioVehiculo.id_vehiculo  # type: ignore
            )
            .order_by(desc(Vehiculo.flota))  # type: ignore
            .all()
        )

    @staticmethod
    def estadistica_pv_y_vehiculo_propietario(
        activo: bool
    ) -> List[Tuple[str, int]]:
        return (
            db.session.query(
                Propietario.id_propietario,  # type: ignore
                func.count(Vehiculo.id_vehiculo)  # type: ignore
            )
            .select_from(PropietarioVehiculo)
            .join(
                Vehiculo,
                PropietarioVehiculo.id_vehiculo == Vehiculo.id_vehiculo  # type: ignore
            )
            .join(
                Propietario,
                PropietarioVehiculo.id_propietario == Propietario.id_propietario  # type: ignore
            )
            .filter(
                Vehiculo.activo.is_(activo)  # type: ignore
            )
            .group_by(Propietario.id_propietario)
            .all()
        )
