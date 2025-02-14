from typing import List
import numpy as np

from qhawariy import db

class Control(db.Model):
    """
    Modelo Control:
    Almacena todos los puntos de control de horarios
    de los vehiculos
    """
    __tablename__='controles'
    id_control=db.Column(db.Integer,primary_key=True)
    codigo=db.Column(db.String(8),unique=True,nullable=False)
    latitud=db.Column(db.String(25),nullable=True)
    longitud=db.Column(db.String(25),nullable=True)

    # Relacion de muchos a uno
    controles=db.relationship("ControlTiempo",back_populates="control",cascade="all,delete-orphan")
    controles_rutas=db.relationship("SecuenciaControlRuta",back_populates="control",cascade="all,delete-orphan")

    def __init__(self,codigo,latitud,longitud):
        self.codigo=codigo
        self.latitud=latitud
        self.longitud=longitud

    def __repr__(self):
        return f"<Control {self.codigo}>"
    
    def guardar(self):
        if not self.id_control:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_id(id):
        resultado=Control.query.get(id)
        return resultado
    
    @staticmethod
    def obtener_todos():
        resultado=Control.query.all()
        return resultado
    
    @staticmethod
    def obtener_por_codigo(codigo):
        resultado=Control.query.filter_by(codigo=codigo).first()
        return resultado
    
class Tramo:
    _nodo_inicial:Control
    _nodo_final:Control
    _tiempo_recorrido:float
    _distancia:float

    def __init__(self)->None:
        self._tiempo_recorrido=0

    def __repr__(self) -> str:
        return f"<Tramo <{self._nodo_inicial}-{self._nodo_final}>>"
    
    @property
    def distancia(self)->float:
        return self._distancia
    
    @distancia.setter
    def distancia(self,distancia:float)->None:
        self._distancia=distancia

    @property
    def tiempo_recorrido(self)->float:
        return self._tiempo_recorrido
    
    @tiempo_recorrido.setter
    def tiempo_recorrido(self,tiempo:float)->None:
        self._tiempo_recorrido=tiempo

    def calcula_distancia_lineal(self)->float:
        """Calcula la distancia lineal de los dos puntos de control de acuerdo a long y latitud establecida"""
        lon1=np.radians(self._nodo_inicial.longitud(float))
        lat1=np.radians(self._nodo_inicial.latitud(float))
        lon2=np.radians(self._nodo_final.longitud(float))
        lat2=np.radians(self._nodo_final.latitud(float))
        r=6378.1370# Radio de la tierra en Km con una diferencia de 2m en el punto mas bajo de 6371
        dlon=np.subtract(lon2,lon1)
        dlat=np.subtract(lat2,lat1)

        # Uso de la formula semiversoseno
        a=np.add(np.power(np.sin(np.divide(dlat,2)),2),
                np.multiply(np.cos(lat1),np.multiply(np.cos(lat2),np.power(np.sin(np.divide(dlon,2)),2))))

        c=np.multiply(2,np.arcsin(np.sqrt(a)))
        distancia=c*r# en Km
        return distancia
    
class Seccion:
    _tramos:List[Tramo]=[]

    def __init__(self,tramos:List[Tramo]|Tramo=None)->None:
        if tramos:
            if isinstance(tramos,List):
                for tramo in tramos:
                    self._tramos.append(tramo)
            else:
                self._tramos.append(tramos)
    def agregar(self,tramo:Tramo)->None:
        self._tramos.append(tramo)

    def calcular_distancia_total_lineal(self)->float:
        aux=0.0
        for tramo in self._tramos:
            aux=aux+tramo.calcula_distancia_lineal()
        return aux
    
    def longitud_total(self)->float:
        aux=0.0
        for tramo in self._tramos:
            aux=aux+tramo.distancia
        return aux
    
    def tiempo_total(self)->float:
        sum=0.0
        for tramo in self._tramos:
            sum=sum+tramo.tiempo_recorrido
        return sum