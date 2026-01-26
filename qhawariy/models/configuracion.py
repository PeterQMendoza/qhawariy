import datetime
from qhawariy import db


class Configuracion(db.Model):
    __tablename__ = 'configuraciones'
    id_config = db.Column(db.Integer, primary_key=True)
    tiempo_espera_vehiculo = db.Column(
        db.Time,
        nullable=False,
        default=datetime.time(hour=0, minute=30, second=0)
    )
    tiempo_total_en_recorrido = db.Column(
        db.Time,
        nullable=False,
        default=datetime.time(hour=1, minute=15, second=0)
    )
    horario_inicio = db.Column(
        db.Time,
        nullable=False,
        default=datetime.time(hour=5, minute=0, second=0)
    )
    horario_fin = db.Column(
        db.Time,
        nullable=False,
        default=datetime.time(hour=21, minute=59, second=0)
    )
    cantidad_vehiculos_a_programar = db.Column(db.Integer, nullable=True, default=34)

    def __init__(self):
        pass

    @property
    def cvp(self) -> int:
        return self.cantidad_vehiculos_a_programar

    def __repr__(self) -> str:
        return f"<Configuracion {self.id_config}>"

    def guardar(self) -> None:
        if not self.id_config:
            db.session.add(self)
        db.session.commit()

    def eliminar(self) -> None:
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_config(id_config: int):
        resultado = Configuracion.query.get(id_config)
        return resultado
