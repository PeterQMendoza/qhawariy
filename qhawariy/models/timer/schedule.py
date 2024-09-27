import datetime

from abc import ABC,abstractmethod
from typing import List

from qhawariy.utilities.builtins import LIMA_TZ

ahora=datetime.datetime.now(tz=LIMA_TZ)

class ActividadBase(ABC):
    """
    Clase Actividadease: Determina los horarios  para el control
    de salida y llegada de los vehiculos
    """
    tiempo_salida:datetime.time# Tiempo donde inicia su programacion un vehiculo
    tiempo_llegada:datetime.time# tiempo que tardo en completar su recorrido (desborde)
    identificador:str#

    def __init__(self)->None:
        pass

    @staticmethod
    def convertir_float_a_time(tiempo)->datetime.time:
        hora,minutos1=divmod(tiempo*60,3600)
        minuto,segundo=divmod(minutos1,60)
        resultado=datetime.time(hour=hora,minute=minuto,second=segundo)
        return resultado
    
    @staticmethod
    def suma_time(time1:datetime.time,time2:datetime.time)->datetime.time:
        tiempo=datetime.datetime(
            year=ahora.year,
            month=ahora.month,
            day=ahora.day,
            hour=time1.hour,
            minute=time1.minute,
            second=time1.second
        )+datetime.timedelta(
            hours=time2.hour,
            minutes=time2.minute,
            seconds=time2.second
        )
        resultado=datetime.time(hour=tiempo.hour,minute=tiempo.minute,second=tiempo.second)
        return resultado
    
    @staticmethod
    def resta_time(time1:datetime.time,time2:datetime.time)->datetime.time:
        tiempo=datetime.datetime(
            year=ahora.year,
            month=ahora.month,
            day=ahora.day,
            hour=time1.hour,
            minute=time1.minute,
            second=time1.second
        )-datetime.timedelta(
            hours=time2.hour,
            minutes=time2.minute,
            seconds=time2.second
        )
        resultado=datetime.time(hour=tiempo.hour,minute=tiempo.minute,second=tiempo.second)
        return resultado

class Actividad(ActividadBase):
    def __init__(self,tiempo_salida:float,tiempo_llegada:float,identificador:str) -> None:
        self.tiempo_salida=self.convertir_float_a_time(tiempo_salida)
        self.tiempo_llegada=self.convertir_float_a_time(tiempo_llegada)
        self.identificador=identificador
        super().__init__()

    def __repr__(self) -> str:
        return f"<Actividad {self.identificador}>"
    
class RoundRobin:
    """
    Clase RoundRobin: Establece el algoritmo de programacion
    """
    disponibles:List[ActividadBase]=[]#actividades disponibles
    tiempo:datetime.time#tiempo transcurrido

    def __init__(self,actividades:List[ActividadBase],quantum:datetime.time) -> None:
        self.tiempo=datetime.time(hour=0,minute=0)
        self.gantt=[]
        self.completados={}
        if actividades:
            self.lista_actividades=actividades
        self.tiempos_desbordados={}
        self.quantum=quantum

    def inicializar(self)->None:
        #ordenamiento metodo burbuja
        n=len(self.lista_actividades)
        for i in range(n):
            for j in range(0,n-i-1):
                if self.lista_actividades[j].tiempo_salida>self.lista_actividades[j+1].tiempo_salida:
                    aux=self.lista_actividades[j]
                    self.lista_actividades[j]=self.lista_actividades[j+1]
                    self.lista_actividades[j+1]=aux
        #
        for actividad in self.lista_actividades:
            aid=actividad.identificador
            tiempo_desbordado=actividad.tiempo_llegada
            self.tiempos_desbordados[aid]=tiempo_desbordado

    def programa(self)->None:
        self.inicializar()
        while self.lista_actividades != []:
            self.disponibles=[]
            for actividad in self.lista_actividades:
                if actividad.tiempo_salida<=self.tiempo:
                    self.disponibles.append(actividad)

            if self.disponibles == []:
                self.gantt.append("idle")
                tiempo=datetime.datetime(
                    year=ahora.year,
                    month=ahora.month,
                    day=ahora.day,
                    hour=self.tiempo.hour,
                    minute=self.tiempo.minute,
                    second=self.tiempo.second
                )+datetime.timedelta(seconds=1)
                self.tiempo=datetime.time(hour=tiempo.hour,minute=tiempo.minute,second=tiempo.second)
                continue
            else:
                actividad=self.disponibles[0]
                self.gantt.append(actividad.tiempo_salida)
                self.lista_actividades.remove(actividad)
                rem_desborde=actividad.tiempo_llegada
                act=ActividadBase()
                if rem_desborde<=self.quantum:
                    self.tiempo=act.suma_time(self.tiempo,rem_desborde)
                    ct=self.tiempo
                    aid=actividad.identificador
                    tiempo_salida=actividad.tiempo_salida
                    tiempo_llegada=self.tiempos_desbordados[aid]
                    tt=act.resta_time(ct,tiempo_salida)
                    wt=act.resta_time(tt,tiempo_llegada)
                    self.completados[actividad.identificador]=[ct,tt,wt]
                    continue
                else:
                    self.tiempo=act.suma_time(self.tiempo,self.quantum)
                    actividad.tiempo_llegada=act.resta_time(actividad.tiempo_llegada,self.quantum)
                    self.lista_actividades.append(actividad)
        
        print(self.gantt)
        print(self.completados)

if __name__=="__main__":
    actividades=[
        Actividad(2,6,"a1"),
        Actividad(5,2,"a2"),
        Actividad(1,6,"a3"),
        Actividad(3,3,"a4"),
        Actividad(6,2,"a5"),
        Actividad(4,8,"a6")
    ]

    quantum=datetime.time(hour=0,minute=2,second=23)

    sched=RoundRobin(actividades=actividades,quantum=quantum)
    print(f"Actividades:{sched.lista_actividades}")
    sched.programa()
    print(f"Actividades:{sched.lista_actividades}")