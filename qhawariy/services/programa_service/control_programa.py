"""
Modulo Control de Programas
Este modulo que permite gestionar las programacion (horarios
de salida de vehiculos en una ruta determinada) para diferentes
rutas, mantiene actualizado una lista programaciones por ruta
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from typing import List, Dict, Any

from datetime import (
    datetime
)


class Flyweight:
    """
    Representa la salida que tendra cada
    vehiculo.

    Metodos:
        operacion(): retorna una cadena que muestra los estado
        del flyweight.
    """

    def __init__(self, shared_state: List) -> None:
        self._shared_state = shared_state

    def __repr__(self):
        return f"<Flyweight {self._shared_state}>"

    def operacion(self) -> List:
        """
        Retorna un cadena de letras serializada en formato JSON.

        Parametros:
            unique_state (str): Estado unico del Flyweigt.

        Retorna:
            str: cadena que muestra los estado del Flyweight.
        """
        resultado = self._shared_state

        return resultado


class FlyweightFactory:
    """
    Administra y comparte instancias de salidas de vehiculos
    (almacena flota y tiempo de salida)para optimizar el uso
    de la memoria.

    Atributos:
        _flyweights (dict): Almacena instancias de Flyweight.

    Metodos:
        get_flyweight(): Devuelve la instancia de Flyweight.
        get_key(): Retorna un hash de cadena de un Flyweight.
    """

    _flyweights: Dict[str, Flyweight] = {}

    def __init__(self, inicial_flyweights: Dict = None) -> None:
        if inicial_flyweights is not None:
            for state in inicial_flyweights:
                self._flyweights[self.get_key(state)] = Flyweight(state)

    def get_key(self, state: Dict) -> str:
        """
        Retorna un hash de cadena de un Flyweight para un
        estado dado.

        Parametros:
            state (Dict): Un estado para el Flyweight.
        Retorna:
            str: Hash de cadena de un Flyweight.

        """
        return "_".join(sorted(state))

    def get_flyweight(self, shared_state: Dict) -> Flyweight:
        """
        Retorna una instancia de Flyweight existente con un
        estado dado o crea uno nuevo.

        Parametros:
            shared_state (Dict): Diccionario de un estado.

        Retorna:
            Flyweight: instancia del objeto Flyweight.
        """

        key = self.get_key(shared_state)

        if not self._flyweights.get(key):
            # Si no encuentra un flyweight, crea uno nuevo.
            self._flyweights[key] = Flyweight(shared_state)
        else:
            # Reutilizando el flyweight existente
            pass

        return self._flyweights[key]

    def list_flyweight(self) -> str:
        # count = len(self._flyweights)
        resultado = "\n".join(map(str, self._flyweights.keys()))
        return resultado


class ProgramaIterator(Iterator):
    """
    Permite recorrer los elementos de una
    coleccion de manera eficiente

    Atributos:
        _position (int): Indica la posicion.
        _reverse (bool): Indica la direccion transversal.

    Metodos:
        __next__(): Retorna el proximo item en la secuencia.

    Ejemplo:
    >>> lista=[a,b,c,d]
    >>> iterator=Iterator(lista)
    >>> while iterator.has_next():
    >>>     programa=iterator.next()
    >>>     programa.display()
    """

    _position: int = None
    _reverse: bool = False

    def __init__(self, collection: List, reverse: bool = False):
        self._collection = collection
        self._reverse = reverse
        self._position = -1 if reverse else 0

    def __next__(self) -> Any:
        """
        Retorna el siguiente item en la secuencia. Busca el
        el final y en subsecuencia llamadas.

        Retorna:
            Any: Algun item de la coleccion.
        """
        try:
            value = self._collection[self._position]
            self._position += -1 if self._reverse else 1
        except IndexError:
            raise StopIteration()

        return value


class ProgramaCollection(ABC, Iterable):
    """
    Define la interfaz utilizada para implementar el
    patron iterator
    """
    @abstractmethod
    def __getitem__(self, index: int) -> Any:
        pass

    @abstractmethod
    def __iter__(self) -> ProgramaIterator:
        pass

    @abstractmethod
    def get_reverse_iterator(self) -> ProgramaIterator:
        pass

    @abstractmethod
    def add_item(self, item: Any) -> None:
        pass


class ProgramaComponent(ABC):
    """
    Define la interfaz comun para
    los componentes de los iterarios
    """
    @property
    def parent(self) -> ProgramaComponent:
        return self._parent

    @parent.setter
    def parent(self, parent: ProgramaComponent) -> None:
        self._parent = parent

    # def add(self,item:ProgramaComponent):
    #     pass

    def remove(self, componente: ProgramaComponent):
        pass

    def is_composite(self) -> bool:
        return False

    @abstractmethod
    def display(self) -> Any:
        pass


class CompositePrograma(ProgramaComponent, ProgramaCollection):
    """
    Implementa la estructura compuesta para manejar una
    coleccion de programas (puede contener programa
    y/o programas)
    """
    _children: List[ProgramaComponent]

    def __init__(self, ruta: str):
        self.ruta = ruta
        self._children = []

    def __repr__(self) -> str:
        return f"<CompositePrograma {self.ruta}>"

    # Implementacion de ProgramaCollection
    def __getitem__(self, index: int) -> Any:
        return self._children[index]

    def __iter__(self) -> ProgramaIterator:
        return ProgramaIterator(self._children)

    def get_reverse_iterator(self) -> ProgramaIterator:
        return ProgramaIterator(self._children, True)

    def add_item(self, item: ProgramaComponent):
        self._children.append(item)
        item.parent = self

    # Implementacion de ProgramaComponent
    def remove(self, componente: ProgramaComponent):
        if componente in self._children:
            self._children.remove(componente)
            componente.parent = None

    def is_composite(self):
        return True

    def display(self) -> Any:
        resultado = []
        for child in self._children:
            resultado.append(child.display())

        data = {
            f"{self.ruta}": resultado
        }

        return data


class LeafPrograma(ProgramaComponent):
    """
    Representa la salida especifica en una programa,
    utilizando Flyweight para compartir informacion
    comun.
    """
    flyweight: Flyweight

    def __init__(
        self,
        factory: FlyweightFactory,
        flota: str,
        tiempo: datetime,
        controles: List,
        llegada_programada: datetime,
        llegada: datetime,
        siguiente_ruta: str
    ):
        dif_prog = llegada_programada-tiempo
        diferencia_programada = dif_prog.total_seconds()/60
        dif = llegada-tiempo
        diferencia = dif.total_seconds()/60
        frecuencia = 60*10

        self.flyweight = factory.get_flyweight([
            flota,
            tiempo,
            controles,
            llegada_programada,
            llegada,
            diferencia_programada,
            diferencia,
            frecuencia,
            siguiente_ruta
        ])

    def __repr__(self):
        return f"<LeafPrograma {self.flyweight._shared_state}>"

    def display(self) -> Any:
        return self.flyweight.operacion()


# if __name__=="__main__":
#     datetime_a=datetime(year=2025,month=2,day=15,hour=16,minute=0,second=0)
#     factory=FlyweightFactory()

#     day=CompositePrograma("15/02/2025")

#     tc_34=CompositePrograma("TC-34")
#     tc_34a=CompositePrograma("TC-34A")
#     tc_34b=CompositePrograma("TC-34B")

#     datetime_1=datetime(year=2025,month=2,day=15,hour=7,minute=15,second=0)
#     datetime_2=datetime(year=2025,month=2,day=15,hour=14,minute=10,second=0)
#     datetime_3=datetime(year=2025,month=2,day=15,hour=12,minute=52,second=0)
#     datetime_4=datetime(year=2025,month=2,day=15,hour=12,minute=52,second=0)
#     datetime_5=datetime(year=2025,month=2,day=15,hour=5,minute=26,second=0)

#     simple_program=LeafPrograma(factory,"2",datetime_1.strftime("%H:%M:%S"),"TC-34A")
#     simple_program_2=LeafPrograma(factory,"3",datetime_2.strftime("%H:%M:%S"),"TC-34A")
#     simple_program_3=LeafPrograma(factory,"3",datetime_3.strftime("%H:%M:%S"),"TC-34B")
#     simple_program_4=LeafPrograma(factory,"3",datetime_4.strftime("%H:%M:%S"),"TC-34B")
#     simple_program_5=LeafPrograma(factory,"3",datetime_5.strftime("%H:%M:%S"),"TC-34B")


#     tc_34.add_item(simple_program)
#     tc_34.add_item(simple_program_2)
#     tc_34.add_item(simple_program_5)

#     tc_34a.add_item(simple_program_3)

#     tc_34b.add_item(simple_program_4)

#     #eliminar
#     tc_34.remove(simple_program_5)

#     day.add_item(tc_34)
#     day.add_item(tc_34a)
#     day.add_item(tc_34b)

#     print(day.display())

#     reverse_tc34=tc_34.get_reverse_iterator()
#     for s in reverse_tc34:
#         print(s.display())
