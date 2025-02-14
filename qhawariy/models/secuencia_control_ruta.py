from sqlalchemy import func,asc,desc

from qhawariy import db

class SecuenciaControlRuta(db.Model):
    """ Modelo SecuenciaControlRuta: Establece la secuencia de controles
    dentro de una ruta """
    __tablename__='secuencias_controles_rutas'
    id_scr=db.Column(db.Integer,primary_key=True)
    secuencia=db.Column(db.Integer,nullable=False)
    id_ruta=db.Column(db.Integer,db.ForeignKey('rutas.id_ruta'),nullable=False)
    id_control=db.Column(db.Integer,db.ForeignKey('controles.id_control'),nullable=False)

    # Relacion de un a muchos
    ruta=db.relationship("Ruta",back_populates="rutas_controles",uselist=False,single_parent=True,lazy=True)
    control=db.relationship("Control",back_populates="controles_rutas",uselist=False,single_parent=True,lazy=True)

    def __init__(self,secuencia:int,id_ruta:int,id_control:int):
        self.secuencia=secuencia
        self.id_ruta=id_ruta
        self.id_control=id_control

    def __repr__(self):
        return f'<SecuenciaControlRuta {self.id_scr}>'

    def guardar(self):
        if not self.id_scr:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_por_id(scr_id:int):
        resultado=SecuenciaControlRuta.query.get(scr_id)
        return resultado

    @staticmethod
    def obtener_todos():
        resultado=SecuenciaControlRuta.query.all()
        return resultado
    
    @staticmethod
    def obtener_secuencia_por_ruta(ruta_id:int):
        resultado=SecuenciaControlRuta.query.filter_by(
            id_ruta=ruta_id
        ).order_by(
            desc(SecuenciaControlRuta.secuencia)
        ).first()
        return resultado
    
    @staticmethod
    def obtener_todos_secuencia_por_ruta(ruta_id:int):
        resultado=SecuenciaControlRuta.query.filter_by(
            id_ruta=ruta_id
        ).order_by(
            desc(SecuenciaControlRuta.secuencia)
        ).all()
        return resultado
