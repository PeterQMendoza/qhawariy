from __future__ import annotations
from typing import Any
from qhawariy.models.notificacion import Notificacion


class SingletonMeta(type):
    """Clase SingletonMeta """

    _instancias: dict[Any, Any] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        """
        Posibles cambios al valor de los argumentos de `__init__` no
        afecta el retorno de la instancia.
        """
        if cls not in cls._instancias:
            instancia = super().__call__(*args, **kwargs)
            cls._instancias[cls] = instancia
        return cls._instancias[cls]


class NotificacionFactory(metaclass=SingletonMeta):
    @staticmethod
    def crear_notificacion(
        id_usuario: int,
        mensaje: str,
        prioridad: str = "normal"
    ) -> Notificacion:
        notificacion = Notificacion(
            id_usuario=id_usuario,
            mensaje=mensaje,
            prioridad=prioridad,
        )
        return notificacion
