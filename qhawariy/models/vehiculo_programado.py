
from datetime import datetime
from typing import List, Optional
# from typing import List
# import pytz

from sqlalchemy import (asc, desc)
from sqlalchemy.sql import func

from qhawariy import db
from qhawariy.models.ruta_terminal import RutaTerminal
from qhawariy.models.vehiculo import Vehiculo
from qhawariy.models.ruta import Ruta
from qhawariy.models.programacion import Programacion
from qhawariy.models.fecha import Fecha
# from qhawariy.utilities.builtins import LIMA_TZ


class VehiculoProgramado(db.Model):
    """Modelo VehiculoProgramado
    """
    __tablename__ = "vehiculos_programados"
    id_vp: int = db.Column(db.Integer, primary_key=True)
    tiempo: Optional[datetime] = db.Column(db.Time, default=None)
    # La propiedad de vehiculo_en_espera se utiliza para informar que el vehiculo puede
    # iniciar el viaje en cualquier momento
    # Por ejemplo: a consecuencia de un desperfecto, o algun evento un vehiculo deja su
    # programacion, y para solucionarlo
    # se reemplaza el vehiculo por otro para cubrir su puesto
    vehiculo_en_espera: bool = db.Column(db.Boolean, default=False)
    id_vehiculo: int = db.Column(
        db.Integer,
        db.ForeignKey("vehiculos.id_vehiculo"),
        nullable=False
    )
    id_programacion: int = db.Column(
        db.Integer,
        db.ForeignKey("programaciones.id_programacion"),
        nullable=False
    )

    # Establecer relaciones {Table1}*1-->1{Table2}
    vehiculo = db.relationship(
        "Vehiculo",
        back_populates="vehiculos",
        uselist=False,
        single_parent=True
    )
    programa = db.relationship(
        "Programacion",
        back_populates="programas_vehiculos",
        uselist=False,
        single_parent=True
    )

    def __init__(
        self,
        tiempo: Optional[datetime],
        vehiculo_en_espera: bool,
        id_vehiculo: int,
        id_programacion: int
    ):
        if vehiculo_en_espera is True:
            self.tiempo = None
        else:
            self.tiempo = tiempo
        self.vehiculo_en_espera = vehiculo_en_espera
        self.id_vehiculo = id_vehiculo
        self.id_programacion = id_programacion

    def __repr__(self):
        return f'<VehiculoProgramado {self.id_vp}>'

    def guardar(self):
        if not self.id_vp:
            db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def obtener_vp_por_id(id: int):
        return VehiculoProgramado.query.get(id)

    @staticmethod
    def obtener_vp_por_id_vehiculo(id_vehiculo: int) -> Optional["VehiculoProgramado"]:
        return (
            VehiculoProgramado.query
            .filter_by(id_vehiculo=id_vehiculo)
            .first()
        )  # type: ignore

    @staticmethod
    def obtener_vp_por_programacion_y_id_vehiculo(
        programacion_id: int,
        vehiculo_id: int
    ) -> Optional["VehiculoProgramado"]:
        return (
            VehiculoProgramado.query.filter_by(
                id_programacion=programacion_id,
                id_vehiculo=vehiculo_id
            ).first()
        )  # type: ignore

    @staticmethod
    def obtener_vp_por_programacion_y_tiempo(
        tiempo: datetime,
        programacion_id: int
    ) -> Optional["VehiculoProgramado"]:
        return (
            VehiculoProgramado.query.filter_by(
                tiempo=tiempo,
                id_programacion=programacion_id
            ).first()
        )  # type: ignore

    @staticmethod
    def obtener_todos_vp() -> List["VehiculoProgramado"]:
        return VehiculoProgramado.query.all()  # type: ignore

    @staticmethod
    def obtener_todos_vp_por_programa(id_programa: int) -> List["VehiculoProgramado"]:
        return (
            VehiculoProgramado.query.filter_by(
                id_programacion=id_programa
            ).all()
        )  # type: ignore

    @staticmethod
    def obtener_todos_vp_fecha(
        desde: datetime,
        hasta: datetime
    ) -> List["VehiculoProgramado"]:
        return (
            VehiculoProgramado.query.join(
                Programacion,
                Programacion.id_programacion == VehiculoProgramado.id_programacion
            ).join(
                Fecha, Fecha.id_fecha == Programacion.id_fecha  # type: ignore
            ).where(
                # Uso de .is_(False) que es interpretado como consulta SQL que
                # compara expresiones booleanas
                VehiculoProgramado.vehiculo_en_espera.is_(False)  # type: ignore
            ).filter(
                # desde.date() <= Fecha.fecha, hasta.date() >= Fecha.fecha
                # Cambio aqui, son las mismas consultas SQL
                Fecha.fecha.between(desde.date(), hasta.date())  # type: ignore
            ).order_by(
                desc(Fecha.fecha)  # type: ignore
            ).all()
        )  # type: ignore

    @staticmethod
    def obtener_todos_vp_en_espera_fecha(
        desde: datetime,
        hasta: datetime
    ) -> List["VehiculoProgramado"]:
        return (
            VehiculoProgramado.query.join(
                Programacion,
                Programacion.id_programacion == VehiculoProgramado.id_programacion
            ).join(
                Fecha, Fecha.id_fecha == Programacion.id_fecha  # type: ignore
            ).where(
                VehiculoProgramado.vehiculo_en_espera.is_(True)  # type: ignore
            ).filter(
                Fecha.fecha.between(desde.date(), hasta.date())  # type: ignore
            ).order_by(
                desc(Fecha.fecha)  # type: ignore
            ).all()
        )  # type: ignore

    @staticmethod
    def obtener_vp_ultimo() -> List["VehiculoProgramado"]:
        return (
            VehiculoProgramado.query.join(
                Programacion,
                Programacion.id_programacion == VehiculoProgramado.id_programacion
            ).join(
                Fecha, Fecha.id_fecha == Programacion.id_fecha  # type: ignore
            ).where(
                # Condicion para que discrimine a vehiculos en espera
                VehiculoProgramado.vehiculo_en_espera.is_(False)  # type: ignore
            ).order_by(
                desc(Fecha.fecha),  # type: ignore
                # Cambio aqui
                desc(VehiculoProgramado.id_vp)  # type: ignore
            ).first()
        )  # type: ignore

    @staticmethod
    def obtener_vp_ultimo_espera() -> List["VehiculoProgramado"]:
        return (
            VehiculoProgramado.query.join(
                Programacion,
                Programacion.id_programacion == VehiculoProgramado.id_programacion
            ).join(
                Fecha,
                Fecha.id_fecha == Programacion.id_fecha  # type: ignore
            ).where(
                VehiculoProgramado.vehiculo_en_espera.is_(True)  # type: ignore
            ).order_by(
                desc(Fecha.fecha)  # type: ignore
            ).first()
        )  # type: ignore

    @staticmethod
    def obtener_fecha_tiempo_flota_placa() -> List["VehiculoProgramado"]:
        return (
            VehiculoProgramado.query.join(
                Programacion,
                VehiculoProgramado.id_programacion == Programacion.id_programacion
            ).add_columns(
                Programacion.fecha_programa,  # type: ignore
                Vehiculo.flota,  # type: ignore
                Vehiculo.placa  # type: ignore
            ).filter(
                VehiculoProgramado.id_vehiculo == Vehiculo.id_vehiculo  # type: ignore
            ).all()
        )

    @staticmethod
    def obtener_vp_y_vehiculo(id: int):
        return (
            VehiculoProgramado.query.filter_by(
                id_programacion=id
            ).join(
                Vehiculo,
                VehiculoProgramado.id_vehiculo == Vehiculo.id_vehiculo  # type: ignore
            ).add_columns(
                VehiculoProgramado.tiempo,  # type: ignore
                Vehiculo.flota  # type: ignore
            ).order_by(asc(VehiculoProgramado.tiempo))  # type: ignore
            .all()
        )

    @staticmethod
    def obtener_vp_join_vehiculo(id: int):
        resultado = VehiculoProgramado.query.filter_by(
            id_programacion=id
        ).join(
            Vehiculo,
            VehiculoProgramado.id_vehiculo == Vehiculo.id_vehiculo  # type: ignore
        ).add_columns(
            VehiculoProgramado.id_vp,  # type: ignore
            VehiculoProgramado.id_programacion,  # type: ignore
            VehiculoProgramado.tiempo,  # type: ignore
            VehiculoProgramado.vehiculo_en_espera,  # type: ignore
            Vehiculo.id_vehiculo,  # type: ignore
            Vehiculo.flota,  # type: ignore
            Vehiculo.placa  # type: ignore
        ).filter(
            VehiculoProgramado.id_vehiculo == Vehiculo.id_vehiculo  # type: ignore
        ).filter(
            VehiculoProgramado.id_programacion == Programacion.id_programacion
        ).order_by(asc(VehiculoProgramado.tiempo)).all()  # type: ignore
        return resultado

    @staticmethod
    def buscar_vehiculo_por_programacion(id_vehiculo: int):
        resultado = VehiculoProgramado.query.add_columns(
            Programacion.fecha_programa,  # type: ignore
            VehiculoProgramado.tiempo,  # type: ignore
            Ruta.codigo,  # type: ignore
            func.count(VehiculoProgramado.id_vp)  # type: ignore
        ).filter(
            VehiculoProgramado.id_programacion == Programacion.id_programacion
        ).filter(
            VehiculoProgramado.id_vehiculo == Vehiculo.id_vehiculo  # type: ignore
        ).filter(
            Ruta.id_ruta == Programacion.id_ruta  # type: ignore
        ).where(
            Vehiculo.id_vehiculo == id_vehiculo  # type: ignore
        ).group_by(
            Programacion.fecha_programa  # type: ignore
        )

        return resultado

    @staticmethod
    def vista_diaria(fecha: datetime, ruta_id: int) -> List["VehiculoProgramado"]:
        return (
            VehiculoProgramado.query.join(
                Programacion,
                Programacion.id_programacion == VehiculoProgramado.id_programacion
            ).join(
                Ruta, Ruta.id_ruta == Programacion.id_ruta  # type: ignore
            ).join(
                Fecha, Fecha.id_fecha == Programacion.id_fecha  # type: ignore
            ).where(
                Fecha.fecha == fecha,  # type: ignore
                Ruta.id_ruta == ruta_id,  # type: ignore
                # Inconsistencia de tiempo de vehiculos en espera
                VehiculoProgramado.vehiculo_en_espera.is_(False)  # type: ignore
            ).all()
        )  # type: ignore

    # Para Estadisticas
    @staticmethod
    def estadistica_vp_fecha_programa():
        resultado = VehiculoProgramado.query.join(
            Programacion,
            Programacion.id_programacion == VehiculoProgramado.id_programacion
        ).join(
            Fecha, Programacion.id_fecha == Fecha.id_fecha  # type: ignore
        ).add_columns(
            Fecha.fecha,  # type: ignore
            func.count(VehiculoProgramado.id_vehiculo)  # type: ignore
        ).order_by(
            asc(Fecha.fecha)  # type: ignore
        ).group_by(Fecha.fecha).all()  # type: ignore
        return resultado

    @staticmethod
    def estadistica_vp_flota_programa():
        resultado = VehiculoProgramado.query.join(
            Vehiculo,
            VehiculoProgramado.id_vehiculo == Vehiculo.id_vehiculo  # type: ignore
        ).add_columns(
            Vehiculo.flota,  # type: ignore
            func.ifnull(func.count(Vehiculo.id_vehiculo), 0)  # type: ignore
        ).filter(
            VehiculoProgramado.id_vehiculo == Vehiculo.id_vehiculo  # type: ignore
        ).order_by(
            desc(Vehiculo.flota)  # type: ignore
        ).group_by(Vehiculo.flota).all()  # type: ignore
        return resultado

    @staticmethod
    def estadistica_vp_fecha_programado_no_programado():
        resultado = VehiculoProgramado.query.join(
            Programacion,
            VehiculoProgramado.id_programacion == Programacion.id_programacion
        ).join(
            Fecha, Fecha.id_fecha == Programacion.id_fecha  # type: ignore
        ).add_columns(
            func.max(Fecha.fecha),
            func.count(VehiculoProgramado.id_vehiculo)  # type: ignore
        ).filter(
            VehiculoProgramado.id_programacion == Programacion.id_programacion
        ).all()
        return resultado

    @staticmethod
    def estadistica_cantidad_vehiculos_por_ruta():
        resultado = VehiculoProgramado.query.join(
            Programacion,
            VehiculoProgramado.id_programacion == Programacion.id_programacion
        ).join(
            Ruta, Ruta.id_ruta == Programacion.id_ruta  # type: ignore
        ).join(
            RutaTerminal, RutaTerminal.id_ruta == Ruta.id_ruta  # type: ignore
        ).add_columns(
            Ruta.codigo,  # type: ignore
            func.count(VehiculoProgramado.id_vp)  # type: ignore
        ).group_by(
            Ruta.id_ruta  # type: ignore
        ).order_by(
            Ruta.id_ruta  # type: ignore
        ).all()
        return resultado

    @staticmethod
    def estadistica_vp_fecha_programa_y_ruta(ruta: int):
        resultado = VehiculoProgramado.query.join(
            Programacion,
            VehiculoProgramado.id_programacion == Programacion.id_programacion
        ).join(
            Ruta, Ruta.id_ruta == Programacion.id_ruta  # type: ignore
        ).join(
            Fecha, Fecha.id_fecha == Programacion.id_fecha  # type: ignore
        ).add_columns(
            Fecha.fecha,  # type: ignore
            func.count(VehiculoProgramado.id_vehiculo)  # type: ignore
        ).where(
            Ruta.id_ruta == ruta  # type: ignore
        ).order_by(
            asc(Fecha.fecha)  # type: ignore
        ).group_by(Fecha.fecha).all()  # type: ignore
        return resultado

    @staticmethod
    def estadistica_vp_tiempos():
        resultado = VehiculoProgramado.query.add_columns(
            VehiculoProgramado.tiempo,  # type: ignore
            func.count(VehiculoProgramado.tiempo)  # type: ignore
        ).order_by(
            asc(VehiculoProgramado.tiempo)  # type: ignore
        ).group_by(
            VehiculoProgramado.tiempo  # type: ignore
        ).all()
        return resultado
