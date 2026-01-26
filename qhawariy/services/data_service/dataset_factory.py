from __future__ import annotations
from abc import ABC, abstractmethod
import datetime
from typing import Any, List

import numpy as np
import pandas as pd


class IDataset(ABC):
    @abstractmethod
    def guardar(self) -> None:
        """Guardar el dataset en el formato especifico"""
        ...

    @abstractmethod
    def proccess_dataframe(self) -> None:
        """Procesar el DataFrame interno."""
        ...


class DatasetBase(IDataset):
    _dataframe: pd.DataFrame

    def __init__(
        self,
        data: List[Any]
    ) -> None:
        datas = [
            DatasetRoute.convert_to_dict(item) for item in data
        ]
        self._dataframe = pd.DataFrame(datas)

    @property
    def dataframe(self) -> pd.DataFrame:
        return self._dataframe

    @dataframe.setter
    def dataframe(self, dataframe: pd.DataFrame) -> None:
        self._dataframe = dataframe


class DatasetControl(DatasetBase):

    _viajes: pd.DataFrame
    _controls: pd.DataFrame

    def __init__(
        self,
        data: List[Any],
        viajes: List[Any],
        controles: List[Any]
    ) -> None:
        super().__init__(data)

        list_viajes = [
            DatasetRoute.convert_to_dict(item) for item in viajes
        ]
        self._viajes = pd.DataFrame(list_viajes)

        list_controls = [
            DatasetRoute.convert_to_dict(item) for item in controles
        ]
        self._controls = pd.DataFrame(list_controls)

    def proccess_dataframe(self) -> None:
        aux = self._dataframe.copy()

        # Obtener los nombres de cada control
        ctrl = self._controls
        ctrl = self._controls.drop(columns=["id_control", "latitud", "longitud"])
        val = list(ctrl["codigo"].unique())  # type: ignore
        times = val.copy()
        val = ["id_viaje"] + val[::-1]

        # Ordenar datos
        aux = aux.groupby("id_viaje").agg(list).reset_index()  # type: ignore
        aux = aux.drop("id_ct", axis=1)
        aux = pd.concat(
            [
                aux.drop("id_control", axis=1),
                aux["id_control"].apply(pd.Series)  # type: ignore
            ],
            axis=1
        )

        # Procesar tiempos
        columns = aux.columns.to_list()
        tiempo = columns.index("tiempo")
        new_col = columns[tiempo+1:]
        aux = aux.drop(columns=new_col)
        aux = pd.concat(
            [
                aux.drop("tiempo", axis=1),
                aux["tiempo"].apply(pd.Series)  # type: ignore
            ],
            axis=1
        )
        aux.columns = val

        # Tiempo
        col_times = aux[times]
        col_t = col_times.columns.to_list()
        for col in col_times:
            col_times[col] = pd.to_datetime(col_times[col].astype(str))  # type: ignore
        aux[col_t] = col_times[col_t]

        # fusionar con viajes
        aux = pd.merge(aux, self._viajes, on="id_viaje", how="inner")  # type: ignore
        aux = aux.drop(columns=["orden"])
        # aux=pd.merge(aux,self._dataframe,on="id_viaje",how="inner")
        aux = aux.drop(columns=["id_vehiculo", "id_programacion"])

        # Eliminar los nulos
        aux = aux.dropna(how="all")  # type: ignore
        aux = aux.fillna(value="")  # type: ignore

        self._dataframe = aux

    def guardar(self):
        pass


class DatasetViaje(DatasetBase):
    _vehicles: pd.DataFrame

    def __init__(self, data: List[Any], vehicles: List[Any]) -> None:
        super().__init__(data)

        list_vehicles = [DatasetRoute.convert_to_dict(item) for item in vehicles]
        self._vehicles = pd.DataFrame(list_vehicles)

    def proccess_dataframe(self) -> None:
        # Fusionar con vehiculos
        aux = pd.merge(  # type: ignore
            self._dataframe,
            self._vehicles,
            on="id_vehiculo",
            how="inner"
        )
        aux = aux.drop(columns=[
            "id_vehiculo",
            "placa",
            "marca",
            "modelo",
            "fecha_fabricacion",
            "numero_asientos",
            "activo",
            "estado",
            "id_programacion"
        ])

        aux = aux.dropna(how="all")  # type: ignore
        aux = aux.fillna(value="")  # type: ignore

        # Cambiar nombre de las columnas
        aux = aux.rename(columns={"flota": "vehiculo", "orden": "o"})

        self._dataframe = aux

    def guardar(self):
        pass


class TimeUtils:
    @staticmethod
    def convert_timedelta_to_time(
        td: datetime.timedelta
    ) -> datetime.time:
        total_seconds = int(td.total_seconds())
        return datetime.time(
            total_seconds//3600,
            (total_seconds % 3600)//60,
            total_seconds % 60
        )

    @staticmethod
    def formating_time(time: datetime.time) -> str:
        parts: list[str] = []
        if time.hour:
            parts.append(f"{time.hour} hr")  # type: ignore
        if time.minute:
            parts.append(f"{time.minute} min")  # type: ignore
        if time.second or not parts:
            parts.append(f"{time.second} s")  # type: ignore
        return " ".join(parts)

    @staticmethod
    def time_to_seconds(time: datetime.time) -> int:
        return time.hour*3600 + time.minute*60 + time.second


class FormatUtils:
    @staticmethod
    def color_negative_red(x: int, color: str) -> np.ndarray[Any, Any]:
        return np.where(x > 300, f"color: {color};font-weight: bold", '')

    @staticmethod
    def icon_based_on_value(value: int):
        _icon_up: str = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"'\
            ' width="20px" height="20px" type="image/svg+xml"><path fill="#05be50"'\
            ' d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM385 231c9.4 9.4'\
            ' 9.4 24.6 0 33.9s-24.6 9.4-33.9 0l-71-71V376c0 13.3-10.7 24-24 24s-24'\
            '-10.7-24-24V193.9l-71 71c-9.4 9.4-24.6 9.4-33.9 0s-9.4-24.6 0-33.9L23'\
            '9 119c9.4-9.4 24.6-9.4 33.9 0L385 231z"/></svg>'
        _icon_down: str = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 '\
            '512" width="20px" height="20px"  type="image/svg+xml"><path fill="#EB00'\
            '46D9" d="M256 0a256 256 0 1 0 0 512A256 256 0 1 0 256 0zM127 281c-9.4-9'\
            '.4-9.4-24.6 0-33.9s24.6-9.4 33.9 0l71 71L232 136c0-13.3 10.7-24 24-24s2'\
            '4 10.7 24 24l0 182.1 71-71c9.4-9.4 24.6-9.4 33.9 0s9.4 24.6 0 33.9L273 '\
            '393c-9.4 9.4-24.6 9.4-33.9 0L127 281z"/></svg>'

        if value > 0:
            return _icon_up
        elif value < 0:
            return _icon_down

    @staticmethod
    def state_based_on_value(value: int):
        _to_time: str = """<div class="flex items-center justify-center">
            <span class="a_tiempo cuadro">
            <div class="mark">A tiempo</div></span></div>"""
        _time_less: str = """<div class="flex items-center justify-center">
            <span class="retrasado cuadro"><div class="mark">retrasado</div>
            </span></div>"""

        if value > 0:
            return _to_time
        elif value < 0:
            return _time_less


class DatasetRoute(DatasetBase):
    _vehicles: pd.DataFrame
    _controles: pd.DataFrame

    def __init__(self, data: List[Any], vehicles: List[Any]) -> None:
        # Convertir lista a dataframe
        super().__init__(data)

        list_vehicles = [DatasetRoute.convert_to_dict(item) for item in vehicles]
        self._vehicles = pd.DataFrame(list_vehicles)

    def guardar(self):
        pass

    @staticmethod
    def convert_to_dict(row: Any) -> dict[Any, Any]:
        if row is None:
            return {}

        # return_dict = dict()
        # keys = row.__table__.columns.keys()
        # for key in keys:
        #     return_dict[key] = getattr(row, key)
        # return return_dict
        return (
            {col: getattr(row, col) for col in row.__table__.columns.keys()}
        )  # type: ignore

    def proccess_dataframe(self) -> None:
        aux = self._dataframe.copy()

        # Ordenar la dataframe por el tiempo
        aux = aux.sort_values(by="tiempo")  # type: ignore
        aux["tiempo"] = pd.to_datetime(aux["tiempo"].astype(str))  # type: ignore
        # Eliminar primera columna
        aux = aux.drop(columns=['id_vp'])

        # Fusionar con vehiculos
        aux = pd.merge(  # type: ignore
            aux,
            self._vehicles,
            on="id_vehiculo",
            how="inner"
        )
        aux = aux.drop(columns=[
            "id_vehiculo",
            "placa",
            "marca",
            "modelo",
            "fecha_fabricacion",
            "numero_asientos",
            "activo",
            "estado",
            "id_programacion"
            ])

        # Reorden columnas
        aux = aux.reindex(columns=["flota", "tiempo"])  # type: ignore

        # Calcular llegada programada aproximado#
        demora = datetime.timedelta(minutes=75)
        aux["llegada"] = pd.to_datetime(aux.tiempo.astype(str))  # type: ignore
        aux["llegada"] = aux.llegada+demora

        # Calcular la frecuencia entre llegadas
        aux["frecuencia"] = pd.to_datetime(aux.llegada.astype(str))  # type: ignore
        aux.frecuencia = aux.frecuencia-aux.frecuencia.shift(1)  # type: ignore
        aux = aux.dropna(how="all")  # type: ignore
        aux = aux.fillna(value=datetime.timedelta(seconds=0))  # type: ignore

        aux.frecuencia = aux.frecuencia.apply(  # type: ignore
            TimeUtils.convert_timedelta_to_time  # type: ignore
        )  # type: ignore
        aux["segundos"] = aux.frecuencia.apply(  # type: ignore
            TimeUtils.time_to_seconds
        )
        aux["icon"] = aux.segundos.apply(  # type: ignore
            FormatUtils.icon_based_on_value
        )
        aux.frecuencia = aux.frecuencia.apply(TimeUtils.formating_time)  # type: ignore

        # Cambiar nombre de las columnas
        aux = aux.rename(columns={"flota": "vehiculo"})
        aux = aux.rename(columns={"tiempo": "salida"})
        aux = aux.rename(columns={"llegada": "programada"})

        aux = aux.dropna(how="all")  # type: ignore
        aux = aux.fillna(value="")  # type: ignore

        # Restablecer los index
        aux = aux.reset_index(drop=True)

        self._dataframe = aux


# Clases creadoras
class Factory(ABC):
    def __init__(self) -> None:
        pass

    def create_dataset(self, *args: Any, **kwargs: Any) -> DatasetBase:
        ...


class DatasetFactory(Factory):
    def create_dataset(
        self,
        data: List[Any],
        vehicles: List[Any]
    ) -> DatasetBase:
        dataset = DatasetRoute(data, vehicles)
        return dataset


class DatasetViajeFactory(Factory):
    def create_dataset(
        self,
        data: List[Any],
        vehicles: List[Any]
    ) -> DatasetBase:
        dataset = DatasetViaje(data, vehicles)
        return dataset


class DatasetControlFactory(Factory):
    def create_dataset(
        self,
        data: List[Any],
        viajes: List[Any],
        controles: List[Any]
    ) -> DatasetBase:
        dataset = DatasetControl(data, viajes, controles)
        return dataset
