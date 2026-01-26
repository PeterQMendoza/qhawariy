from __future__ import annotations

import datetime
# import pytz

from abc import ABC, abstractmethod
from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.sql import func

from qhawariy import db
from qhawariy.utilities.builtins import LIMA_TZ


class Vehiculo(db.Model):
    """" Modelo Vehiculo de administracion de vehiculos

        El estado de un vehiculo puede ser:

        0=activo: el vehiculo esta apto para ser programado
        1=inactivo: el vehiculo no puede ser programado
        2=espera: el vehiculo esta listo para realizar un viaje por algun
            improvisto (a reemplazo de otro vehiculo)
        3=programado: el vehiculo esta en espera de su turno para iniciar viaje
        4=viaje: el vehiculo esta realizando un viaje en este instante
    """

    __tablename__ = "vehiculos"
    id_vehiculo: int = db.Column(db.Integer, primary_key=True)
    flota: int = db.Column(db.Integer, nullable=False)
    placa: str = db.Column(db.String(8), unique=True, nullable=False)
    marca: str = db.Column(db.String(45), nullable=False)
    modelo: str = db.Column(db.String(45), nullable=False)
    fecha_fabricacion: datetime.datetime = db.Column(
        db.DateTime, default=datetime.datetime.now(tz=LIMA_TZ)
    )
    numero_asientos: int = db.Column(db.Integer, nullable=False)
    activo: bool = db.Column(db.Boolean, default=False)
    estado: int = db.Column(db.Integer, nullable=False)

    # Establecer relacion inversa {Tabla2}*1-->1{Tabla1}
    vehiculos = db.relationship(
        "VehiculoProgramado",
        back_populates="vehiculo",
        cascade="all,delete-orphan"
    )
    vehiculos_disponibles = db.relationship(
        "DisponibleVehiculo",
        back_populates="vehiculo",
        cascade="all,delete-orphan"
    )
    vehiculos_viajes = db.relationship(
        "Viaje",
        back_populates="vehiculo",
        cascade="all,delete-orphan"
    )

    __allow_unmapped__ = True

    _estado: Optional[Estado] = None
    _esta_viaje: Optional[bool] = None

    @property
    def esta_viaje(self) -> bool:
        return bool(self._esta_viaje)

    @esta_viaje.setter
    def esta_viaje(self, value: bool) -> None:
        self._esta_viaje = value

    def __init__(
        self,
        flota: int,
        placa: str,
        marca: str,
        modelo: str,
        fecha_fabricacion: datetime.datetime,
        numero_asientos: int
    ):
        self.flota = flota
        self.placa = placa
        self.modelo = modelo
        self.marca = marca
        self.fecha_fabricacion = fecha_fabricacion
        self.numero_asientos = numero_asientos
        self.estado = 0
        self.transicion(EstadoActivo())
        self._esta_viaje = False

    def __repr__(self):
        return f'<Vehiculo {self.flota}-{self._estado}>'

    def transicion(self, estado: Estado):
        self._estado = estado
        self._estado.vehiculo = self

    def actualizar(self):
        if self.activo:
            if self.estado == 0:
                self.transicion(EstadoActivo())
            if self.estado == 1:
                self.transicion(EstadoInactivo())
            if self.estado == 2:
                self.transicion(EstadoEspera())
            if self.estado == 3:
                self.transicion(EstadoProgramado())
            if self.estado == 4:
                self.transicion(EstadoViaje())

    def establece_espera(self):
        if self.activo and self._estado is not None:
            self._estado.espera()

    def establece_viaje(self):
        if self.activo and self._estado is not None:
            self._estado.viaje()

    def establece_programado(self):
        if self.activo and self._estado is not None:
            self._estado.programado()

    def establece_activo(self):
        if self._estado is not None:
            self._estado.activo()

    def establece_inactivo(self):
        if self._estado is not None:
            self._estado.inactivo()

    def guardar(self):
        self.actualizar()
        if not self.id_vehiculo:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_vehiculo_por_id(id: int):
        resultado = Vehiculo.query.get(id)
        return resultado

    @staticmethod
    def obtener_todos_vehiculos() -> List["Vehiculo"]:
        resultado: List[Vehiculo] = (  # type: ignore
            Vehiculo.query.order_by(desc(Vehiculo.flota)).all()  # type: ignore
        )
        for v in resultado:
            v.actualizar()
        return resultado

    @staticmethod
    def obtener_todos_vehiculos_activos() -> List["Vehiculo"]:
        resultado: List[Vehiculo] = (  # type: ignore
            Vehiculo.query.filter_by(activo=True).order_by(
                desc(Vehiculo.flota)  # type: ignore
            ).all()
        )
        for v in resultado:
            v.actualizar()
        return resultado

    @staticmethod
    def obtener_todos_vehiculos_programado() -> List["Vehiculo"]:
        resultado: List[Vehiculo] = (  # type: ignore
            Vehiculo.query.filter_by(estado=3).order_by(
                desc(Vehiculo.flota)  # type: ignore
            ).all()
        )
        for v in resultado:
            v.actualizar()
        return resultado

    @staticmethod
    def obtener_vehiculo_por_placa(placa: str) -> Optional["Vehiculo"]:
        return Vehiculo.query.filter_by(placa=placa).first()  # type: ignore

    @staticmethod
    def obtener_vehiculo_por_flota(flota: int) -> Optional["Vehiculo"]:
        return Vehiculo.query.filter_by(flota=flota).first()  # type: ignore

    @staticmethod
    def obtener_vehiculo_por_fabricacion(fecha_fabricacion: datetime.datetime):
        return Vehiculo.query.filter_by(fecha_fabricacion=fecha_fabricacion)

    @staticmethod
    def busqueda_flota(palabra: str) -> List["Vehiculo"]:
        resultado: List[Vehiculo] = (  # type: ignore
            Vehiculo.query.filter_by(flota=palabra).all()
        )
        return resultado

    @staticmethod
    def busqueda_placa(palabra: str) -> List["Vehiculo"]:
        resultado: List["Vehiculo"] = (  # type: ignore
            Vehiculo.query.filter_by(placa=palabra).all()
        )
        return resultado

    @staticmethod
    def busqueda_marca(palabra: str) -> List["Vehiculo"]:
        resultado: List["Vehiculo"] = (  # type: ignore
            Vehiculo.query.filter_by(marca=palabra).all()
        )
        return resultado

    @staticmethod
    def busqueda_modelo(palabra: str) -> List["Vehiculo"]:
        resultado: List["Vehiculo"] = (  # type: ignore
            Vehiculo.query.filter_by(modelo=palabra).all()
        )
        return resultado

    @staticmethod
    def estadistica_todos_vehiculos_activos():
        return Vehiculo.query.filter_by(activo=True).add_columns(
            func.count(Vehiculo.id_vehiculo)  # type: ignore
        ).all()


class Estado(ABC):
    @property
    def vehiculo(self) -> Vehiculo:
        return self._vehiculo

    @vehiculo.setter
    def vehiculo(self, vehiculo: Vehiculo) -> None:
        self._vehiculo = vehiculo

    @abstractmethod
    def espera(self) -> None:
        pass

    @abstractmethod
    def viaje(self) -> None:
        pass

    @abstractmethod
    def programado(self) -> None:
        pass

    @abstractmethod
    def inactivo(self) -> None:
        pass

    @abstractmethod
    def activo(self) -> None:
        pass


class EstadoViaje(Estado):
    def espera(self) -> None:
        """
        Estado que cambia cuando un vehiculo es castigado
        """
        self.vehiculo.esta_viaje = False
        self.vehiculo.estado = 2
        self.vehiculo.transicion(EstadoEspera())
        self.vehiculo.guardar()

    def viaje(self) -> None:
        pass

    def programado(self) -> None:
        """
        Estado cuando vehiculo continua con la programacion
        """
        self.vehiculo.esta_viaje = False
        self.vehiculo.estado = 3
        self.vehiculo.transicion(EstadoProgramado())
        self.vehiculo.guardar()

    def inactivo(self) -> None:
        self.vehiculo.activo = False
        self.vehiculo.estado = 1
        self.vehiculo.transicion(EstadoInactivo())
        self.vehiculo.guardar()

    def activo(self) -> None:
        pass


class EstadoEspera(Estado):
    def espera(self) -> None:
        pass

    def viaje(self) -> None:
        self.vehiculo.esta_viaje = True
        self.vehiculo.estado = 4
        self.vehiculo.transicion(EstadoViaje())
        self.vehiculo.guardar()

    def programado(self) -> None:
        self.vehiculo.estado = 3
        self.vehiculo.transicion(EstadoProgramado())
        self.vehiculo.guardar()

    def inactivo(self) -> None:
        self.vehiculo.activo = False
        self.vehiculo.estado = 1
        self.vehiculo.transicion(EstadoInactivo())
        self.vehiculo.guardar()

    def activo(self) -> None:
        pass


class EstadoProgramado(Estado):
    def espera(self) -> None:
        self.vehiculo.estado = 2
        self.vehiculo.transicion(EstadoEspera())
        self.vehiculo.guardar()

    def viaje(self) -> None:
        self.vehiculo.esta_viaje = True
        self.vehiculo.estado = 4
        self.vehiculo.transicion(EstadoViaje())
        self.vehiculo.guardar()

    def programado(self) -> None:
        pass

    def inactivo(self) -> None:
        pass

    def activo(self) -> None:
        pass


class EstadoActivo(Estado):
    def espera(self) -> None:
        self.vehiculo.estado = 2
        self.vehiculo.transicion(EstadoEspera())
        self.vehiculo.guardar()

    def viaje(self) -> None:
        pass

    def programado(self) -> None:
        pass

    def activo(self) -> None:
        pass

    def inactivo(self) -> None:
        self.vehiculo.activo = False
        self.vehiculo.estado = 1
        self.vehiculo.transicion(EstadoInactivo())
        self.vehiculo.guardar()


class EstadoInactivo(Estado):
    def espera(self) -> None:
        pass

    def viaje(self) -> None:
        pass

    def programado(self) -> None:
        pass

    def inactivo(self) -> None:
        pass

    def activo(self) -> None:
        self.vehiculo.activo = True
        self.vehiculo.estado = 0
        self.vehiculo.transicion(EstadoActivo())
        self.vehiculo.guardar()
