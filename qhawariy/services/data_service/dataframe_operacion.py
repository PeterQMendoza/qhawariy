import locale
import logging
from typing import List
import pandas as pd
from abc import ABC, abstractmethod

# from qhawariy.utilities.builtins import LOC, LIMA_TZ

logger = logging.getLogger(__name__)


class Operacion(ABC):
    @abstractmethod
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """ Aplica la transformacion sobre la Dataframe y retorna el resultado"""
        pass


# Operaciones concretas
class FiltraOperacion(Operacion):
    """
    FilterOPeracion: clase que permite la oeracion de filtrar filas de acuerdo a una
    condicion
    """
    def __init__(self, condicion):
        """
        Parametros:
        ----------
        condicion : Funcion que recibe un DataFrame y retorna una mascara
        """
        self.condicion = condicion

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[self.condicion(df)]


class AgregarColumnOperacion(Operacion):
    """
    AgregarColumnOperacion: clase que permite la operacion de agregar column
    """
    def __init__(self, nombre_columna, funcion):
        """
        Parametros:
        ----------
        nombre_columna : Nombre de la columna a agregar.

        funcion : Funcion que recibe el dataframe y retorna la Serie o valor
            para dicha columna.

        """
        self.nombre_columna = nombre_columna
        self.funcion = funcion

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df[self.nombre_columna] = self.funcion(df)
        return df


class EliminarColumnaOperacion(Operacion):
    def __init__(self, columna):
        self.columna = columna

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.drop(columns=self.columna, errors='ignore')


class SeleccionarColumnasOperacion(Operacion):
    def __init__(self, columnas):
        """
        columnas : Lista de columnas a seleccionar.
        """
        self.columnas = columnas

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[self.columnas]


class AgruparPorOperacion(Operacion):
    def __init__(self, columnas, funcion_ag):
        self.columnas = columnas
        self. funcion_ag = funcion_ag

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.groupby(self.columnas).agg(self.funcion_ag).reset_index()


class OrdenarPorOperacion(Operacion):
    def __init__(self, columna: str, ascendente: bool = True):
        self.columna = columna
        self.ascendente = ascendente

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        df.sort_values(by=self.columna, ascending=self.ascendente, inplace=True)
        return df


class InnerJoinOperacion(Operacion):
    def __init__(
        self,
        otros,
        como='inner',
        en_izq=None,
        en_der=None,
        en=None,
        sufijos=('_x', '_y')
    ):
        """
        Parametros:
        ----------
        otro : DataFrame (o dato convertible a DataFrame) que se unirá con el DataFrame
            original.
        como : Tipo de join a realizar ('inner', 'left', 'right', 'outer'). Por defecto,
            'inner'.
        en_izq : Columna o lista de columnas clave del DataFrame base.
        en_der : Columna o lista de columnas clave del DataFrame 'otro'.
        en : Columna o lista de columnas comunes en ambos DataFrames (si ambas tienen
            la misma columna).
        sufijos : Sufijos para diferenciar columnas con mismo nombre.
        """
        if not isinstance(otros, list):
            self.otros = [otros]
        else:
            self.otros = otros
        self.como = como
        self.en_izq = en_izq
        self.en_der = en_der
        self.en = en
        self.sufijos = sufijos

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        resultado = df.copy()
        for otro in self.otros:
            # Convertir en DataFrame si es necesario
            if not isinstance(otro, pd.DataFrame):
                otro = pd.DataFrame(otro)
            if self.en and self.en not in resultado.columns:
                raise ValueError(
                    f"La columna '{self.en}' no existe en el DataFrame base."
                )
            if self.en_izq and self.en_izq not in resultado.columns:
                raise ValueError(
                    f"La columna '{self.en_izq}' no existe en el DataFrame base."
                )
            if self.en_der and self.en_der not in otro.columns:
                raise ValueError(
                    f"La columna '{self.en_der}' no existe en el DataFrame a unir."
                )
            # Elimnar los duplicados
            otro = otro.drop_duplicates(subset=self.en_der)
            resultado = resultado.drop_duplicates(subset=self.en_izq)

            if self.en:
                interseccion = set(resultado[self.en]).intersection(set(otro[self.en]))
                if not interseccion:
                    print("Advertencia: No hay coincidencias en las claves.")

            resultado = pd.merge(
                left=resultado,
                right=otro,
                how=self.como,
                left_on=self.en_izq,
                right_on=self.en_der,
                on=self.en,
                suffixes=self.sufijos
            )
        return resultado


class AgregarTiempoOperacion(Operacion):
    def __init__(self, nombre_columna, horas=0, minutos=0, segundos=0):
        """
        Parametros:
        ----------
        nombre_columna : Nombre de la columna que contiene datos de tipo time
            o datetime.
        horas, minutos, segundos : Intervalo de tiempo a sumar.
        """
        self.nombre_columna = nombre_columna
        self.tiempo = pd.Timedelta(hours=horas, minutes=minutos, seconds=segundos)

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        # convertir la columna a datetime
        df[self.nombre_columna] = pd.to_datetime(df[self.nombre_columna])+self.tiempo
        return df


class DiferenciaTiempoOperacion(Operacion):
    def __init__(
        self,
        columna_inicio,
        columna_fin,
        columna_resultado
    ):
        """
        Parametros:
        ----------
        columna_inicio: Nombre de la columna con el tiempo de inicio.
        columna_fin: Nombre de la columna con el tiempo final.
        columna_resultado: Nombre de la columna donde se almacenará la diferencia.
        """
        self.columna_inicio = columna_inicio
        self.columna_fin = columna_fin
        self.columna_resultado = columna_resultado

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        # Verificar que ambas columnas sean datetime
        df[self.columna_inicio] = pd.to_datetime(df[self.columna_inicio])
        df[self.columna_fin] = pd.to_datetime(df[self.columna_fin])
        # Calculo de la diferencia
        df[self.columna_resultado] = df[self.columna_fin] - df[self.columna_inicio]
        return df


class PromedioDiferenciaTiempoOperacion(Operacion):
    def __init__(self, columna_resultado, nueva_columna):
        """
        Parametros:
        ----------
        columna_resultado: Nombre de la columna que almacena las diferencias de tiempo
            (Timedelta).
        nueva_columna: Nombre de la columna en la que se almacenará el valor promedio.
        """
        self.columna_resultado = columna_resultado
        self.nueva_columna = nueva_columna

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        promedio = df[self.columna_resultado].mean()
        df[self.nueva_columna] = promedio
        return df


class FormatoHTMLOperacion(Operacion):
    def __init__(
        self,
        columna_icono=None,
        icon_mapping=None,
        color_texto=None,
        **kwargs
    ):
        """
        Parametros:
        -----------
        columna_icono : Nombre de la columna a la que se le agregará un ícono.
        icon_mapping : Diccionario que mapea valores de la columna a cadenas HTML con
            íconos.
            Ejemplo :{ 'Lima': '<i class="fa fa-check" style="color:green;"></i>' }
        text_color: Si se especifica, se envuelve el HTML resultante en un div que
            aplica ese color al texto.
        kwargs : Parámetros adicionales que se pasan a df.to_html (por ejemplo, border,
            classes, etc.)

        -----------
        ### Nota : Esta operación debe ser la última en la cadena, ya que transforma el
        ### DataFrame en una cadena HTML.
        """
        self.columna_icono = columna_icono
        self.icon_mapping = icon_mapping if icon_mapping is not None else {}
        self.color_texto = color_texto
        self.kwargs = kwargs

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        # Si se ha definido una columna para iconos y existe un mapping,
        # actualizamos cada celda de esa columna anteponiendo el icono correspondiente.
        if self.columna_icono is not None and self.icon_mapping:
            df[self.columna_icono] = df[self.columna_icono].apply(
                lambda x: (
                    f"{self.icon_mapping.get(x, '')} {x}"
                    if x in self.icon_mapping
                    else x
                )
            )
        html_resultado = df.to_html(**self.kwargs)
        if self.color_texto:
            return f'<div style="color: {self.text_color};">{html_resultado}</div>'
        return html_resultado


class FormatoFechaOperacion(Operacion):
    def __init__(
        self,
        columnas,
        formato='%d de %B de %Y, %H:%M:%S',
        locale_str='es_PE.UTF-8'
    ):
        """
        Parametros:
        ----------
        columnas : Nombre o lista de nombres de columnas a formatear.
        formato : Formato de salida para las fechas, p.ej. '%d de %B de %Y, %H:%M:%S'
        locale_str : Locale para formatear (en Linux: 'es_ES.UTF-8'; en Windows puede
            ser 'Spanish_Spain' o similar).
        """
        if isinstance(columnas, str):
            self.columnas = [columnas]
        else:
            self.columnas = columnas
        self.formato = formato
        self.locale_str = locale_str

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        original_locale = locale.getlocale(locale.LC_TIME)
        try:
            locale.setlocale(locale.LC_TIME, self.locale_str)
        except locale.Error as e:
            logger.error("Error al cambiar el locale:", e)

        def formatear_valor(x):
            if pd.isna(x):
                return ""
            if isinstance(x, pd.Timestamp):
                return x.strftime(self.formato)
            # Si el objeto es timedelta
            elif isinstance(x, pd.Timedelta):
                componente = x.components  # Obtiene dias, horas, minutos  segundos
                dias = componente.days
                horas = componente.hours
                minutos = componente.minutes
                segundos = componente.seconds
                # Si hay dias se incluye en el formato
                if dias > 0 or horas > 0:
                    if dias > 0:
                        return (
                            f"""{dias} {'dias' if dias != 1 else 'día'},
                            {horas:02d}:{minutos:02d}:{segundos:02d}"""
                        )
                    else:
                        return (
                            f"{horas:02d}h {minutos:02d}m {segundos:02d}s"
                        )
                else:
                    # Si no ha horas, se muestra solo MM:SS
                    return f"{minutos:02d}m {segundos:02d}s"
            else:
                return str(x)

        for columna in self.columnas:
            if columna in df.columns:
                # convertir la columnas a datetime (si no lo es)
                if (
                    not pd.api.types.is_datetime64_any_dtype(df[columna])
                    and not pd.api.types.is_timedelta64_dtype(df[columna])
                ):
                    df[columna] = pd.to_datetime(df[columna], errors='coerce')
                # Aplicar formato si el valor es alido
                df[columna] = df[columna].apply(formatear_valor)
        # Restaurar el locale original
        try:
            locale.setlocale(locale.LC_TIME, original_locale)
        except locale.Error:
            pass
        return df


class CambiarColorTextoCondicionalOperacion(Operacion):
    def __init__(self, condicion, color: str, columnas=None):
        """
        Parametros:
        ----------
        condicion: Función que recibe el valor de una celda y retorna True si se debe
            cambiar el color.
        color: Color a aplicar (por ejemplo, 'red' o '#FF0000').
        columnas: Lista de nombres de columnas a las que se aplicará la transformación.
            Si es None, se aplicará a todas.
        """
        self.condicion = condicion
        self.color = color
        self.columnas = columnas

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        # si no se especifica, aplicar a todas las columnas
        columnas = self.columnas if self.columnas is not None else df.columns
        for columna in columnas:
            if columna in df.columns:
                df[columna] = df[columna].apply(
                    lambda x: (
                        f'<span style="color: {self.color};">{x}</span>'
                        if self.condicion(x)
                        else x
                    )
                )
        return df


# -----------------------------------------------------------------------------
# Clase DataFrameBuilder
class DataFrameBuilder:
    def __init__(self, data=None):
        """
        data : Puede ser un diccionario o una lista de diccionarios
        """
        if isinstance(data, pd.DataFrame):
            self._base_df = data.copy()
        else:
            self._base_df = pd.DataFrame(data) if data is not None else pd.DataFrame()
        self._operaciones: List[Operacion] = []

    def set_data(self, data):
        if isinstance(data, pd.DataFrame):
            self._base_df = data.copy()
        else:
            self._base_df = pd.DataFrame(data)
        return self

    def agregar_operacion(self, op: Operacion):
        self._operaciones.append(op)
        return self

    # Metodos elper para operaciones comunes
    def filtrar(self, condicion):
        return self.agregar_operacion(FiltraOperacion(condicion))

    def agregar_columna(self, nombre_columna, funcion):
        return self.agregar_operacion(AgregarColumnOperacion(nombre_columna, funcion))

    def eliminar_columna(self, columna: str):
        return self.agregar_operacion(EliminarColumnaOperacion(columna))

    def seleccionar_columna(self, columnas):
        return self.agregar_operacion(SeleccionarColumnasOperacion(columnas))

    def agrupar_por(self, columnas: list, funcion_ag: dict):
        return self.agregar_operacion(AgruparPorOperacion(columnas, funcion_ag))

    def ordenar_por(self, columna: str, ascendente: bool = True):
        return self.agregar_operacion(OrdenarPorOperacion(columna, ascendente))

    def unir(
        self,
        otros,
        como='inner',
        en_izq=None,
        en_der=None,
        en=None,
        sufijos=('_x', '_y')
    ):
        self.agregar_operacion(
            InnerJoinOperacion(otros, como, en_izq, en_der, en, sufijos)
        )
        return self

    def agregar_tiempo(
        self,
        nombre_columna: str,
        horas: int = 0,
        minutos: int = 0,
        segundos: int = 0
    ):
        self.agregar_operacion(
            AgregarTiempoOperacion(nombre_columna, horas, minutos, segundos)
        )
        return self

    def diferencia_tiempo(
        self,
        columna_inicio: str,
        columna_fin: str,
        columna_resultado: str
    ):
        self.agregar_operacion(
            DiferenciaTiempoOperacion(columna_inicio, columna_fin, columna_resultado)
        )
        return self

    def promediar_diferencia(
        self,
        columna_resultado: str,
        nueva_columna: str
    ):
        self.agregar_operacion(
            PromedioDiferenciaTiempoOperacion(columna_resultado, nueva_columna)
        )
        return self

    def cambiar_color_texto_condicional(
        self,
        condicion,
        color,
        columnas
    ):
        self.agregar_operacion(
            CambiarColorTextoCondicionalOperacion(condicion, color, columnas)
        )
        return self

    def formatear_fecha(
        self,
        columnas,
        formato='%d de %B de %Y, %H:%M:%S',
        locale_str='es_ES.UTF-8'
    ):
        self.agregar_operacion(
            FormatoFechaOperacion(columnas, formato, locale_str)
        )
        return self

    def formatear_html(
        self,
        columna_icono=None,
        icon_mapping=None,
        **kwargs
    ):
        self.agregar_operacion(
            FormatoHTMLOperacion(columna_icono, icon_mapping, **kwargs)
        )
        return self

    def construir(self) -> pd.DataFrame:
        resultado = self._base_df.copy()
        for operacion in self._operaciones:
            resultado = operacion.apply(resultado)
        return resultado


# Ejemplo de uso
# if __name__ == "__main__":
#     data = {
#         'A': [1, 2, 3, 4, 5],
#         'B': [5, 4, 3, 2, 1],
#         'C': ['apple', 'banana', 'cherry', 'date', 'elderberry']
#     }

#     data2 = {
#         'A': [1, 2, 3, 4, 5],
#         'D': ['Kg', 'Kg', 'Und', 'Date', 'Kg'],
#         'E': [
#             '2025-03-31 08:00:23',
#             '2025-03-31 09:15:00',
#             '2025-03-31 10:42:00',
#             '2025-03-31 1:30:00',
#             '2025-03-31 5:26:00'
#         ],
#         'F': [
#             '2025-03-31 10:00:23',
#             '2025-03-31 11:14:00',
#             '2025-03-31 13:04:00',
#             '2025-03-31 3:30:00',
#             '2025-03-31 7:29:00'
#         ],
#     }

#     icon_mapping = {
#         'apple': '<i class="fa fa-check" style="color:green;"></i>',
#         'banana': '<i class="fa fa-info" style="color:blue;"></i>',
#         'date': '<i class="fa fa-exclamation" style="color:red;"></i>',
#     }

#     df2 = pd.DataFrame(data2)

#     builder = DataFrameBuilder(data)
#     df_result = (
#         builder
#         .seleccionar_columna(['A', 'C'])
#         .agregar_columna('A_squared', lambda df: df['A'] ** 2)
#         .ordenar_por('A')
#         .construir()
#     )
#     resultado = (
#         builder
#         .unir(df2, en='A')
#         .agregar_tiempo('E', horas=1, minutos=24, segundos=37)
#         .agregar_columna('tiempo_resultado', lambda df: 0)
#         .diferencia_tiempo('E', 'F', 'tiempo_resultado')
#         .promediar_diferencia('tiempo_resultado', 'promedio')
#         .cambiar_color_texto_condicional(
#             lambda und: und == 'Kg',
#             color='red',
#             columnas=['D']
#         )
#         .formatear_fecha(['E', 'F', 'tiempo_resultado', 'promedio'])
#         .formatear_html(
#             columna_icono='C',
#             icon_mapping=icon_mapping,
#             border=1,
#             classes="table table-striped",
#             escape=False,
#         )
#         .construir()
#     )

#     print("\nDataFrame resultante:")
#     print(df_result)
#     print(resultado)
