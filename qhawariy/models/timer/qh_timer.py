"""
Modulo qh_timer.py
Permite cambiar el estado de un vehiculo de acuerdo a
su cronograma de salida.

Por ejemplo:
si un vehiculo fue programado a las 7:45 a.m. entonces
llegado a este tiempo (de acuerdo a la entidad VP), se
cambiara el estado de ese vehiculo en viaje, despues de
un cierto periodo de tiempo (se debe especificar) volvera
a cambiar a programado (simulacion de los viajes hechos
por los vehiculos).

Este modulo permitira mostrar en el mapa horarios reales

Uso:

reloj=Reloj()
alarma1=reloj.crear_alarma(flota=flota)
reloj.start()
alarma1.start()
alarma1.join()
alarma2=reloj.crear_alarma(flota=flota_ida)
alarma2.start()
alarma2.join()
time.sleep(20)
reloj.stop()
"""

from __future__ import annotations

import time
import pytz

from abc import ABC,abstractmethod
from threading import Thread
from typing import List

from datetime import datetime

from qhawariy.models.vehiculo import Vehiculo,EstadoViaje,EstadoProgramado,EstadoEspera
from qhawariy.utilities.builtins import LIMA_TZ

class CreadorAlarma(ABC):
    """
    Interface CreadorAlarma: Define los metodos de fabrica a implementar
     este retorna un objeto de la clase Alarma
    """
    @abstractmethod
    def crear_alarma(self,flota:Flota)->Temporizador:
        pass

class Reloj(Thread,CreadorAlarma):
    """
    Clase Reloj: Establece un reloj para ser mostrada en GUI
    la instancia del objeto puede crear alarmas
    """
    tiempo:datetime
    def __init__(self)->None:
        super().__init__()
        self.tiempo_inicial=0
        self.esta_iniciado=False
        self.tiempo_actual:datetime=None

    def play(self):
        self.tiempo_inicial=datetime.now(tz=LIMA_TZ)
        self.esta_iniciado=True

    def run(self):
        self.play()
        while self.esta_iniciado:
            self.tiempo_actual=datetime.now(tz=LIMA_TZ)
            # print(self.str_tiempo)
            time.sleep(1)# suspende en un segundo

    def stop(self)->None:
        self.esta_iniciado=False

    def crear_alarma(self,flota:Flota)->Alarma:
        alarma=Alarma(flota)
        return alarma
    
    @property
    def str_tiempo(self)->str:
        resultado=self.tiempo_actual.strftime("%#I:%M:%S %p")
        return resultado

class Temporizador(ABC):
    @abstractmethod
    def operacion(self)->None:
        pass

class Alarma(Thread,Temporizador):
    """
    Clase Alarma: Realiza el control de horarios segun intervalos de tiempo.
    la clase Alarma, ademas, esta asociado con uno de los comandos . La clase
    alarma envia una solicitud al comando

    argumentos:
    intervals: Intervalos de tiempo de cada notificacion tipo float
    """
    _en_iniciar=None
    _en_finalizar=None

    def __init__(self,flota:Flota) -> None:
        super().__init__()
        self.flota=flota
        self.intervals=flota._horarios
        self.is_playing=False
        self.count_time=sum(self.intervals)

    def play(self):
        self.start_time=time.time()
        self.is_playing=True
    
    def run(self):
        counter=len(self.intervals)-1
        aux=0
        self.play()
        cambiar_estado=CambiarEstadoVehiculo(self.flota)
        while self.is_playing:
            try:
                time.sleep(self.intervals[aux])
                cambiar_estado.vehiculo=self.flota._flota[aux]
                self.establecer_en_iniciar(cambiar_estado)
                self.controlar_horario()
                print(counter,aux)
                if counter>aux:# and len(self.flota._flota)>aux:# corregir fuera de indice
                    aux=aux+1
                else:
                    print("Termino")
                    self.is_playing=False
            except Exception as e:
                print(f'Error: {e}')
                print(counter,aux)
                break
    
    def stop(self)->None:
        self.is_playing=False

    # Metodos ue permite enviar solicitud al comando
    def establecer_en_iniciar(self,comando:Comando):
        self._en_iniciar=comando
        
    def establecer_en_finalizar(self,comando:Comando):
        self._en_finalizar=comando

    def controlar_horario(self)->None:
        if isinstance(self._en_iniciar,Comando):
            self._en_iniciar.ejecutar()
            
        if isinstance(self._en_finalizar,Comando):
            self._en_finalizar.ejecutar()

    # Metodos implementados de la clase Temporizador(pd Factory)
    def operacion(self) -> None:
        pass



class Controlador(ABC):
    @abstractmethod
    def update(self,control_horario:ControlHorario,vehiculo:Vehiculo)->None:
        pass

class ControladorEspera(Controlador):
    def update(self, control_horario: ControlHorario,vehiculo:Vehiculo) -> None:
        if vehiculo in control_horario._flota:
            global ve
            ve=control_horario._flota.index(vehiculo)
        if isinstance(control_horario._flota[ve]._estado,EstadoEspera):
            print(f"Vehiculo {control_horario._flota[ve].placa} esta en espera")

class ControladorViaje(Controlador):
    def update(self, control_horario: ControlHorario,vehiculo:Vehiculo) -> None:
        if vehiculo in control_horario._flota:
            global ve
            ve=control_horario._flota.index(vehiculo)
        if isinstance(control_horario._flota[ve]._estado,EstadoViaje):
            print(f"Vehiculo {control_horario._flota[ve].placa} esta en viaje")

class ControladorProgramado(Controlador):
    def update(self, control_horario: ControlHorario,vehiculo:Vehiculo) -> None:
        if vehiculo in control_horario._flota:
            global ve
            ve=control_horario._flota.index(vehiculo)
        if isinstance(control_horario._flota[ve]._estado,EstadoProgramado):
            print(f"Vehiculo {control_horario._flota[ve].placa} esta programado")

class ControlHorario(ABC):
    """
    Clase Horario: Implementa metodos a la clase ControlHorario
    """
    @abstractmethod
    def vincular(self,controlador:Controlador)->None:
        pass

    @abstractmethod
    def desvincular(self,controlador:Controlador)->None:
        pass

    @abstractmethod
    def notificar(self)->None:
        pass


class Comando(ABC):
    """
    Clase Comando: Declara los metodos para ejecutar un comando.
    """
    @abstractmethod
    def ejecutar(self)->None:
        pass

class CambiarEstadoVehiculo(Comando):
    """
    Clase CambiarEstadoVehiculo: Delega las operacion al objeto flota
    para cambiar el estado de los vehiculos.
    """
    def __init__(self,recividor:Flota) -> None:
        self._recividor=recividor

    @property
    def vehiculo(self)->Vehiculo:
        return self._vehiculo
    
    @vehiculo.setter
    def vehiculo(self,vehiculo:Vehiculo):
        self._vehiculo=vehiculo
    
    def ejecutar(self) -> None:
        if isinstance(self._vehiculo._estado,EstadoProgramado):
            self._recividor.establecer_vehiculos_en_viaje(self._vehiculo)
            pass
        elif isinstance(self._vehiculo._estado,EstadoViaje):
            self._recividor.establecer_vehiculos_en_programado(self._vehiculo)
        elif isinstance(self._vehiculo._estado,EstadoEspera):
            self._recividor.establecer_vehiculos_en_viaje(self._vehiculo)

class Flota(ControlHorario):
    """
    Clase Flota: Contiene una lista de vehiculos ademas gestiona
    y cambia el estado de cada vehiculo.
    La clase flota, ademas, es el recividor de las solicitadas por la clase
    comando.
    """
    

    def __init__(self,vehiculos:list[Vehiculo])->None:
        self._controladores:List[Controlador]=[]
        self._flota:list[Vehiculo]=[]
        self._horarios:list[float]=[0]# primer vehiculo inicia su recorrido con tiempo=0
        self._flota=vehiculos
        for i in range(len(vehiculos)-1):# primer vehiculo inicia su recorrido con tiempo=0
            self._horarios.append(float(5))

    # Metodo implementados de la clase Horario
    def vincular(self, controlador: Controlador) -> None:
        self._controladores.append(controlador)

    def desvincular(self, controlador: Controlador) -> None:
        self._controladores.remove(controlador)

    def notificar(self,controlador:Controlador,vehiculo:Vehiculo) -> None:

        controlador.update(self,vehiculo=vehiculo)
    
    def establecer_vehiculos_en_espera(self,vehiculo:Vehiculo)->None:
        if vehiculo in self._flota:
            controlador_espera=ControladorEspera()
            if controlador_espera not in self._controladores:
                self.vincular(controlador_espera)
            vehiculo.establece_espera()
            self.notificar(controlador_espera,vehiculo)
        else:
            print(f"El vehiculo {vehiculo} no pertenece a la flota")

    def establecer_vehiculos_en_viaje(self,vehiculo:Vehiculo)->None:
        if vehiculo in self._flota:
            controlador_viaje=ControladorViaje()
            if controlador_viaje not in self._controladores:
                self.vincular(controlador_viaje)
            vehiculo.establece_viaje()
            self.notificar(controlador_viaje,vehiculo)
        else:
            print(f"El vehiculo {vehiculo} no pertenece a la flota")

    def establecer_vehiculos_en_programado(self,vehiculo:Vehiculo)->None:
        if vehiculo in self._flota:
            controlador_programado=ControladorProgramado()
            if controlador_programado not in self._controladores:
                self.vincular(controlador_programado)
            vehiculo.establece_programado()
            self.notificar(controlador_programado,vehiculo)
        else:
            print(f"El vehiculo {vehiculo} no pertenece a la flota")
