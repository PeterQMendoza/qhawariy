from datetime import datetime
from typing import List, Optional
from qhawariy import db
from qhawariy.utilities.builtins import LIMA_TZ


class Notificacion(db.Model):
    """
    Modelo Notificacion
    """
    __tablename__ = "notificaciones"
    id_notificacion = db.Column(
        db.Integer,
        primary_key=True
    )
    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.id_usuario'),
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

    def __init__(self, id_usuario: int, mensaje: str, prioridad: str):
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
    def obtener_todos_por_usuario(id_usuario: int) -> List["Notificacion"]:
        return (
            Notificacion.query
            .filter_by(id_usuario=id_usuario)
            .order_by(Notificacion.creado_en.desc())
            .all()
        )  # type: ignore

    @staticmethod
    def obtener_por_id(id_notificacion: int) -> Optional["Notificacion"]:
        resultado = Notificacion.query.get(id_notificacion)
        return resultado
