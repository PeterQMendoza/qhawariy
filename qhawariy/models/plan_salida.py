from qhawariy import db


class PlanSalida(db.Model):
    __tablename__ = "planes_salidas"
    id_ps = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id_usuario", ondelete="CASCADE"),
        nullable=False
    )
    id_vp = db.Column(
        db.Integer,
        db.ForeignKey("vehiculos_programados.id_vehiculo", ondelete="CASCADE"),
        nullable=False
    )

    def __init__(self, id_usuario, id_vp):
        self.id_usuario = id_usuario
        self.id_vp = id_vp

    def __repr__(self):
        return f'<PlanSalida {self.id_ps}>'

    def guadar(self):
        if not self.id_ps:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_plan_salida_por_id(id):
        return PlanSalida.query.get(id)

    @staticmethod
    def obtener_todos_plan_salida():
        return PlanSalida.query.all()
