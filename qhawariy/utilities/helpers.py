
import datetime
import os
import random
from typing import Any, Dict, Iterable, List, Optional, cast

from flask import flash
import pandas as pd
# import geopandas as gpd

from os import walk


def convertir_DataFrame(lista: List[Any]) -> pd.DataFrame:
    data_list = [a_dict(item) for item in lista]
    df = pd.DataFrame(data_list)
    return df


def validar_dataframe(
    nombre: str,
    datos: List[Any],
    requerido: bool = True
) -> pd.DataFrame:
    if not datos:
        if requerido:
            flash(f"No existen datos de {nombre}", "error")
        return pd.DataFrame()
    return convertir_DataFrame(datos)


def a_dict(row: Optional[Any]) -> Dict[str, Any]:
    if row is None:
        return {}

    keys = cast(Iterable[str], row.__table__.columns.keys())
    return {key: getattr(row, key) for key in keys}


def archivo_existe(ruta: str) -> bool:
    return os.path.exists(ruta)


def hacer_arbol(path: str) -> List[Any]:
    fn: List[Any] = []
    # for (dirpath, dirnames, filenames) in walk(path):
    for (_, _, filenames) in walk(path):
        fn.extend(filenames)
        break

    return fn


def generar_numero(lenght: int = 8):
    """Genera numero pseudoaleatorio"""
    return ''.join([str(random.randint(0, 9)) for _ in range(lenght)])


def obtener_tiempo_actual():
    pass


class Calendario():
    """
    Clase Calendario: Devuelve una lista del modelo Fecha, para ser mostrados e una
    plantilla
    """
    def __init__(
        self,
        anio: int,
        mes: int,
        lista_fechas: List[Any],
        primer_dia_lista: int,
        primer_dia_semana: int
    ):
        self.anio = anio
        self.mes = mes
        self.actual = datetime.date(year=anio, month=mes, day=primer_dia_lista)

        self.ultimo = self._calcular_ultimo_dia_mes(anio, mes)
        self.primer_dia_semana = primer_dia_semana
        self.ultimo_dia_mes = self.ultimo.day
        self.ultima_celda = self.primer_dia_semana+self.ultimo_dia_mes

        # Lista de dias que tienen objeto Fecha asociado
        self.lista_dias = [
            getattr(a, "fecha").day for a in lista_fechas if getattr(a, "fecha", None)
        ]

        # Construir de las celdas del calendario
        self.fechas: List[Any] = self._construir_celdas(lista_fechas)

    @staticmethod
    def _calcular_ultimo_dia_mes(
        anio: int,
        mes: int
    ) -> datetime.date:
        """ Devuelve el ultimo dia del mes dado."""
        if mes == 12:
            siguiente_mes, siguiente_anio = 1, anio+1
        else:
            siguiente_mes, siguiente_anio = mes+1, anio
        return (
            datetime.date(siguiente_anio, siguiente_mes, 1) -
            datetime.timedelta(days=1)
        )

    def _construir_celdas(
        self,
        lista_fechas: List[Any]
    ) -> List[Any]:
        """ Construye 42 celdas (6 semanas x 7 dias) del calendario"""
        fechas: List[Any] = []
        dia = 0

        for i in range(1, 43):
            if i == self.primer_dia_semana:
                dia = 1

            if i < self.primer_dia_semana or i >= self.ultima_celda:
                fechas.append("")
            else:
                if dia in self.lista_dias:
                    index = self.lista_dias.index(dia)
                    fechas.append(lista_fechas[index])
                else:
                    fechas.append(str(dia))
                dia += 1

            # Si llegamos al final de una semana y ya pasamos el ultimo
            if i % 7 == 0 and dia > self.ultimo_dia_mes:
                break
        return fechas
