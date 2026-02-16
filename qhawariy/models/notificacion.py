from datetime import datetime
from typing import List, Optional
import uuid

from qhawariy import db
from qhawariy.utilities.builtins import LIMA_TZ
from qhawariy.utilities.uuid_endpoints import ShortUUID


class Notificacion(db.Model):
    """
    Modelo Notificacion
    """
    __tablename__ = "notificaciones"
    __table_args__ = {"schema": "app"}

    id_notificacion: str = db.Column(
        ShortUUID(),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    id_usuario: str = db.Column(
        ShortUUID(),
        db.ForeignKey('app.usuarios.id_usuario'),
        nullable=False
    )

    mensaje = db.Column(db.String(255), nullable=False)
    esta_leida = db.Column(db.Boolean, default=False, nullable=False)
    prioridad = db.Column(db.String(50), default="normal")
    creado_en = db.Column(db.DateTime, default=datetime.now(tz=LIMA_TZ))

    # Relacion con tablas
    usuario = db.relationship(
        "Usuario",
        back_populates="usuario_notificaciones",
        uselist=False,
        single_parent=True
    )

    def __init__(self, id_usuario: str, mensaje: str, prioridad: str):
        self.id_usuario = id_usuario
        self.mensaje = mensaje
        self.prioridad = prioridad

    def marcar_como_leida(self):
        self.esta_leida = True

    def guardar(self):
        if not self.id_notificacion:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f'<Notificacion {self.id_notificacion}>'

    @staticmethod
    def obtener_todos_por_usuario(id_usuario: str) -> List["Notificacion"]:
        return (
            Notificacion.query
            .filter_by(id_usuario=id_usuario)
            .order_by(Notificacion.creado_en.desc())
            .all()
        )  # type: ignore

    @staticmethod
    def obtener_por_id(id_notificacion: str) -> Optional["Notificacion"]:
        resultado = Notificacion.query.get(id_notificacion)
        return resultado
