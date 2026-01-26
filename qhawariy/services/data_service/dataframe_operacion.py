import locale
import logging
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Union, cast
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from datetime import datetime, date, time

# from qhawariy.utilities.builtins import LOC, LIMA_TZ

logger = logging.getLogger(__name__)


class Operacion(ABC):
    @abstractmethod
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """ Aplica la transformacion sobre la Dataframe y retorna el resultado"""
        pass


class OperacionFormato(ABC):
    @abstractmethod
    def apply(self, df: pd.DataFrame) -> Optional[str]:
        """
        Retorna el str de la HTML de la DataFrame, esta operacion debe
        realizar al final de todas las operaciones
        """
        pass


# Operaciones concretas
class FiltraOperacion(Operacion):
    """
    FilterOPeracion: clase que permite la oeracion de filtrar filas de acuerdo a una
    condicion
    """
    def __init__(self, condicion: Callable[[pd.DataFrame], pd.Series]):
        """
        Parametros:
        ----------
        condicion : Funcion que recibe un DataFrame y retorna una mascara
        """
        self.condicion = condicion

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[self.condicion(df)]


class ExpandirListaColumnasOperacion(Operacion):
    def __init__(
        self, columna: str,
        prefijo: Optional[str] = None,
        drop_original: bool = True
    ):
        """
            Parámetros:
            columna :   str
                        Nombre de la columna cuyo contenido es una lista.
            prefijo :   str
                        Prefijo para nombrar las nuevas columnas. Si no se especifica,
                        se usa el nombre de la columna.
            drop_original   :   bool
                                Si es True, se elimina la columna original luego de
                                crear las nuevas. Por defecto es True.
        """
        self.columna = columna
        self.prefijo = prefijo if prefijo is not None else columna
        self.drop_original = drop_original

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.columna not in df.columns:
            return df
        # Crear una DataFrame a partir de la lista de cada celda;
        # pd.DataFrame(...).tolist() manejara diferentes longitudes
        nuevo_df = pd.DataFrame(df[self.columna].to_list(), index=df.index)

        # Renombre las columnas
        nuevo_df = nuevo_df.rename(columns=lambda x: f"{self.prefijo} {x+1}")

        # Eliminar la columna original
        if self.drop_original:
            df = df.drop(columns=[self.columna])

        # Combinar el DataFrame original (a sin la columna expandida, si drop_original)
        # con el DataFrame generado a partir de la lista.
        df = df.join(nuevo_df)
        return df


class CambiarNombreColumnasOperacion(Operacion):
    def __init__(self, mapeado: dict[str, str]):
        """
        Parametros:
        ----------
        mapeado: Diccionario con el mapeo de nombres antiguos a nuevos.
            Ejemplo: {'viejo_nombre': 'nuevo_nombre'}
        """
        self.mapeado = mapeado

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.rename(columns=self.mapeado)


class AgregarColumnasOperacion(Operacion):
    """
    AgregarColumnOperacion: clase que permite la operacion de agregar columna
    """
    def __init__(self, mapeado: dict[str, Callable[[pd.DataFrame], pd.Series]]):
        """
        Parametros:
        ----------
        mapping :   dict
                    Diccionario que mapea el nombre de la nueva columna a una función.
                    La función debe recibir el DataFrame como argumento y devolver una
                    Serie.

            Ejemplo:
                {
                    "columna_nueva1": lambda df: df["A"] + df["B"],
                    "columna_nueva2": lambda df: df["A"] * 2,
                }
        """
        self.mapeado = mapeado

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        for nuevo_nombre, funcion in self.mapeado.items():
            df[nuevo_nombre] = funcion(df)
        return df


class EliminarColumnaOperacion(Operacion):
    def __init__(self, columnas: Union[str, List[str]]):
        self.columnas = [columnas] if isinstance(columnas, str) else columnas

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.drop(columns=self.columnas, errors='ignore')


class SeleccionarColumnasOperacion(Operacion):
    def __init__(self, columnas: Union[str, List[str]]):
        """
        columnas : Lista de columnas a seleccionar.
        """
        self.columnas = columnas

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[self.columnas]


class AgruparPorOperacion(Operacion):
    def __init__(
        self,
        columnas: Union[str, List[str]],
        funcion_ag: Dict[
            str,
            Union[
                str,
                Callable[..., Any],
                List[Union[str, Callable[..., Any]]]
            ]
        ]
    ):
        """
        Parametros:
          columnas  :       str | []
                            Nombre de la columna o lista de columnas por las cuales se
                            agrupará el DataFrame.
          funciones_agg :   Diccionario que mapea nombres de columna a una función de
                            agregación o a una lista de funciones.
                            Ejemplo: {'Values1': 'sum', 'Values2': 'mean'}
        """
        if isinstance(columnas, str):
            self.columnas = [columnas]
        else:
            self.columnas = columnas
        self.funcion_ag = funcion_ag

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        # Validacion de columnas faltantes
        columnas_faltantes = [col for col in self.columnas if col not in df.columns]
        if columnas_faltantes:
            raise KeyError(
                f"Las columnas {columnas_faltantes} no existen en el DataFrame"
            )

        for col in self.funcion_ag.keys():
            if col not in df.columns:
                raise KeyError(
                    f"La columna {col} no existe en el DataFrame"
                )

        grupo = df.groupby(self.columnas).agg(self.funcion_ag)  # type: ignore
        grupo = grupo.reset_index()
        return grupo


class ExplodeColumnaOperacion(Operacion):
    def __init__(self, columna: str):
        """
        Parametros:
        ----------
        columna :   str
                    Nombre de la columna que contiene listas
        """
        self.columna = columna

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.columna not in df.columns:
            return df
        return df.explode(self.columna)


class OrdenarPorOperacion(Operacion):
    def __init__(self, columna: str, ascendente: bool = True):
        self.columna = columna
        self.ascendente = ascendente

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        df.sort_values(  # type: ignore
            by=self.columna,
            ascending=self.ascendente,
            inplace=True
        )
        return df


class InnerJoinOperacion(Operacion):
    def __init__(
        self,
        otros: Union[pd.DataFrame, List[pd.DataFrame]],
        como: Literal[
            "inner",
            "left",
            "right",
            "outer",
            "cross",
            "left_anti",
            "right_anti"
        ] = "inner",
        en_izq: Optional[Union[str, List[str]]] = None,
        en_der: Optional[Union[str, List[str]]] = None,
        en: Optional[Union[str, List[str]]] = None,
        sufijos: Union[
            List[Optional[str]],
            Tuple[str, str],
            Tuple[None, str],
            Tuple[str, None]
        ] = ("_x", "_y")
    ):
        """
        Parametros:
        ----------
        otros : DataFrame (o dato convertible a DataFrame) que se unirá con el DataFrame
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
            if not isinstance(otro, pd.DataFrame):  # type: ignore
                otro = pd.DataFrame(otro)

            # Validacion de columnas
            if self.en:
                cols = (
                    [self.en] if isinstance(self.en, str) else self.en  # type: ignore
                )
                if not all(col in resultado.columns for col in cols):
                    raise ValueError(
                        f"Alguna columna de '{self.en}' no existe en el DataFrame base."
                    )
                if not all(col in otro.columns for col in cols):
                    raise ValueError(
                        f"Alguna columna de '{self.en}' no existe en el DataFrame "
                        "a unir."
                    )
            if self.en_izq:
                cols = (
                    [self.en_izq]
                    if isinstance(self.en_izq, str)  # type: ignore
                    else self.en_izq
                )
                if not all(col in resultado.columns for col in cols):
                    raise ValueError(
                        f"Alguna columna de '{self.en_izq}' \
                        no existe en el DataFrame base."
                    )
            if self.en_der:
                cols = (
                    [self.en_der]
                    if isinstance(self.en_der, str)  # type: ignore
                    else self.en_der
                )
                if not all(col in otro.columns for col in cols):
                    raise ValueError(
                        f"La columna '{self.en_der}' \
                        no existe en el DataFrame a unir."
                    )
            # Eliminar los duplicados
            if self.en_der:
                otro = otro.drop_duplicates(subset=self.en_der)
            if self.en_izq:
                resultado = resultado.drop_duplicates(subset=self.en_izq)

            # Alerta si no ha coincidencia
            if self.en:
                interseccion = set(resultado[self.en]).intersection(set(otro[self.en]))
                if not interseccion:
                    logger.warning("Advertencia: No hay coincidencias en las claves.")

            resultado = pd.merge(  # type: ignore
                left=resultado,
                right=otro,
                how=self.como,  # type: ignore
                left_on=self.en_izq,
                right_on=self.en_der,
                on=self.en,
                suffixes=self.sufijos
            )
        return resultado


class AgregarTiempoOperacion(Operacion):
    def __init__(
        self,
        nombre_columna: str,
        horas: int = 0,
        minutos: int = 0,
        segundos: int = 0
    ):
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
        # Funcion interna para agregar el timedelta a cada celda
        def sumar_tiempo(x: Any) -> Any:
            # si es nulo
            if pd.isna(x):  # type: ignore
                return x
            # Si a es Timestamp
            if isinstance(x, pd.Timestamp):
                return x + self.tiempo
            # Si es un objeto datetime.time
            if isinstance(x, time):
                # Uso de fecha fija
                dt_combinado = datetime.combine(date(1900, 1, 1), x)
                nuevo_dt = dt_combinado + self.tiempo
                return nuevo_dt.time()
            # Si es una cadena de otro formato
            try:
                ts = cast(pd.Timedelta, pd.to_datetime(x))  # type: ignore
                return ts + self.tiempo
            except Exception as e:
                # Si falla la conversion, retorna sin agregar
                logger.exception("Fallo la conversion de tiempo", e)
                return x

        df[self.nombre_columna] = (
            df[self.nombre_columna].apply(sumar_tiempo)  # type: ignore
        )
        return df


class DiferenciaTiempoOperacion(Operacion):
    def __init__(
        self,
        columna_inicio: str,
        columna_fin: str,
        columna_resultado: str,
        formato: Optional[Union[str, Callable[[pd.Timedelta], str]]] = None
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
        self.formato = formato

    def convertir_valores(
        self,
        valor: Any
    ) -> Optional[Union[pd.Timestamp, pd.Timedelta]]:
        """ Intentara convertir el valor a un objeto timestamp o time"""
        if pd.isna(valor):  # type: ignore
            return None
        # Si Timestamp o Timedelta
        if isinstance(valor, pd.Timedelta) or isinstance(valor, pd.Timestamp):
            return valor
        # Si es datetime
        if isinstance(valor, datetime):
            return pd.Timestamp(valor)

        # Si es time
        if isinstance(valor, time):
            try:
                fecha_actual = datetime.now().date()
                val = (
                    pd.Timestamp.combine(
                        date=fecha_actual,
                        time=valor
                    )  # type: ignore
                )
                return val
            except Exception:
                return None

        # Si es una cadena
        if isinstance(valor, str):
            try:
                val = pd.to_datetime(valor, errors='raise')  # type: ignore
                return val
            except Exception:
                try:
                    # Puede ser timedelta
                    val = pd.to_timedelta(valor, errors='raise')  # type: ignore
                    return val
                except Exception:
                    return None
        # Si es numerico o otro
        return None

    def formato_diferencia(
        self,
        dif: pd.Timedelta
    ) -> str:
        """Formatea un pd.Timedelta"""
        def formato_hhmmss(td: pd.Timedelta) -> str:
            total_sec = int(td.total_seconds())
            horas, remanente = divmod(total_sec, 3600)
            minutos, segundos = divmod(remanente, 60)
            return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

        def formato_mmss(td: pd.Timedelta) -> str:
            total_seg = int(td.total_seconds())
            minutos, segundos = divmod(total_seg, 60)
            return f"{minutos:02d}:{segundos:02d}"

        def formato_dia_hhmmss(td: pd.Timedelta) -> str:
            dias = td.days
            remanente_seg = int(td.total_seconds()) - dias * 86400
            horas, remanente = divmod(remanente_seg, 3600)
            minutos, segundos = divmod(remanente, 60)
            if dias > 0:
                return (
                    f"""{dias} {'dias' if dias != 1 else 'día'},
                    {horas:02d}:{minutos:02d}:{segundos:02d}"""
                )
            return (
                f"{horas:02d}h {minutos:02d}m {segundos:02d}s"
            )

        # Si self.formato es callable
        if callable(self.formato):
            return self.formato(dif)
        # Si la cadena, se reconocen los formatos predefinidos
        elif isinstance(self.formato, str):
            formato_lower = self.formato.lower()
            if formato_lower == "hh:mm:ss":
                return formato_hhmmss(dif)
            elif formato_lower == "mm:ss":
                return formato_mmss(dif)
            elif formato_lower == "d hh:mm:ss":
                return formato_dia_hhmmss(dif)
            else:
                return str(dif)
        else:
            return str(dif)

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        # Validacion de columnas
        # if (
        #     self.columna_fin not in df.columns
        # ):
        #     return df

        # # Detectar automaticamente la ultima columna de control disponible
        # texto = self.columna_fin
        # txt = re.sub(r"\d+$", "", texto)
        # columnas_ctrl = [c for c in df.columns if c.startswith(txt)]
        # if not columnas_ctrl:
        #     return df

        # # Ordenar por indice numerico  tomar la ultima
        # columnas_ctrl.sort(key=lambda x: int(x.split(" ")[1]))
        # ultima_columna = columnas_ctrl[-1]

        # Trabajamos de forma no destructiva
        def calcular_diferencia(fila: pd.Series) -> Union[pd.Timedelta, float]:

            val_inicio = self.convertir_valores(fila[self.columna_inicio])
            val_fin = self.convertir_valores(fila[self.columna_fin])

            if (val_inicio is None) or (val_fin is None):
                return np.nan

            # Si ambos valores son Timestamp
            if (
                isinstance(val_inicio, pd.Timestamp)
                and isinstance(val_fin, pd.Timestamp)
            ):
                if val_inicio > val_fin:
                    val_inicio, val_fin = val_fin, val_inicio
                return val_fin - val_inicio

            # Si ambos son Timedelta
            if (
                isinstance(val_inicio, pd.Timedelta)
                and isinstance(val_fin, pd.Timedelta)
            ):
                return val_fin - val_inicio

            # Si uno es Timedelta y el otro Timestamp
            return np.nan

        diferencia = df.apply(calcular_diferencia, axis=1)  # type: ignore

        def aplicar_formato(td: Any) -> Union[str, Any]:
            if pd.notna(td):
                return self.formato_diferencia(td)
            return td

        # Formateo de la diferencia
        if self.formato:
            diferencia = diferencia.apply(  # type: ignore
                aplicar_formato
            )

        df[self.columna_resultado] = diferencia
        return df


class PromedioDiferenciaTiempoOperacion(Operacion):
    def __init__(
        self,
        columna_resultado: str,
        nueva_columna: str
    ):
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
        """
        Calcula el promedio de la columna de diferencia de tiempo
        y lo asigna a una nueva columna
        """
        # Validar datos
        if self.columna_resultado not in df.columns:
            raise KeyError(
                f"La columna {self.columna_resultado} no existe en el"
                f"DataFrame."
            )

        promedio: Union[pd.Timedelta, float] = df[self.columna_resultado].mean()

        # Si el promedio es Timedelta, se tiene que convertir a string legible
        if isinstance(promedio, pd.Timedelta):
            df[self.nueva_columna] = str(promedio)
        else:
            df[self.nueva_columna] = promedio

        return df


class FormatoHTMLOperacion(OperacionFormato):
    def __init__(
        self,
        color_texto: Optional[str] = None,
        columna_icono: Optional[str] = None,
        icon_mapping: Optional[Dict[str, str]] = None,
        **kwargs: Any
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
        self.icon_mapping = icon_mapping or {}
        self.color_texto = color_texto
        self.kwargs = kwargs

    def apply(self, df: pd.DataFrame) -> Optional[str]:
        """
        Convierte el DataFrame en HTML, aplicando iconos y color de texto
        """
        # Si se ha definido una columna para iconos y existe un mapping,
        # actualizamos cada celda de esa columna anteponiendo el icono correspondiente.
        if self.columna_icono and self.icon_mapping:
            def agregar_icono(x: Any) -> str:
                x_str = str(x)
                if x_str in self.icon_mapping:
                    return f"{self.icon_mapping[x_str]} {x_str}"

                return x_str

            df[self.columna_icono] = (
                df[self.columna_icono].apply(agregar_icono)  # type: ignore
            )

        html_resultado: str = df.to_html(**self.kwargs)  # type: ignore
        if self.color_texto:
            return f'<div style="color: {self.color_texto};">{html_resultado}</div>'

        return html_resultado  # type: ignore


class TransponerFilasAColumnasOperacion(Operacion):
    def __init__(
        self,
        sep: str = "_",
        filas: Optional[List[Any]] = None
    ):
        """
        Parametros:
        ----------
        sep: Separador que se usará para combinar el nombre de la columna original con
            el índice de fila. Por defecto, se usa "_".
        """
        self.sep = sep
        self.filas = filas

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Recorre cada fila del DataFrame y genera un diccionario donde cada clave es:
            "{nombre_columna}{sep}{índice_fila}"
        y su correspondiente valor es el valor de esa celda.
        Finalmente, crea un DataFrame de una sola fila a partir de ese diccionario.
        """
        nuevo_data = {}
        for index, fila in df.iterrows():
            # si Filas esta definida, solo se toman las filas cuyo indice esta en la
            # lista
            if self.filas is None or index in self.filas:
                for columna in df.columns:
                    # Forma el nuevo nombre de la columna combinando el nuevo
                    nombre_nueva_columna = f"{columna}{self.sep}{index}"
                    nuevo_data[nombre_nueva_columna] = fila[columna]
        # Retorna un DataFrame de una sola fila con la informacion
        return pd.DataFrame([nuevo_data])


class FormatoFechaOperacion(Operacion):
    def __init__(
        self,
        columnas: Union[str, List[str]],
        formato: str = '%d de %B de %Y, %H:%M:%S',
        locale_str: str = 'es_ES.UTF-8'
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

        def formatear_valor(x: Any):
            if pd.isna(x):  # type: ignore
                return ""
            if isinstance(x, pd.Timestamp):
                return x.strftime(self.formato)
            # Si el objeto es timedelta
            elif isinstance(x, pd.Timedelta):
                return self._formatear_timedelta(x)

            return str(x)

        for columna in self.columnas:
            if columna in df.columns:
                # Convertir la columnas a datetime (si no lo es)
                if (
                    not pd.api.types.is_datetime64_any_dtype(  # type: ignore
                        df[columna]
                    )
                    and not pd.api.types.is_timedelta64_dtype(  # type: ignore
                        df[columna]
                    )
                ):
                    df[columna] = pd.to_datetime(  # type: ignore
                        df[columna],
                        errors='coerce'
                    )
                # Aplicar formato si el valor es valido
                df[columna] = df[columna].apply(formatear_valor)  # type: ignore
        # Restaurar el locale original
        try:
            locale.setlocale(locale.LC_TIME, original_locale)
        except locale.Error:
            pass
        return df

    def _formatear_timedelta(self, td: pd.Timedelta) -> str:
        comp = td.components
        dias = comp.days
        horas = comp.hours
        minutos = comp.minutes
        segundos = comp.seconds

        if dias > 0:
            return f"""{dias} {'dias' if dias != 1 else 'día'},
                {horas:02d}:{minutos:02d}:{segundos:02d}"""
        if horas > 0:
            return f"{horas:02d}h {minutos:02d}m {segundos:02d}s"

        return f"{minutos:02d}m {segundos:02d}s"


class CambiarColorTextoCondicionalOperacion(Operacion):
    def __init__(
        self,
        condicion: Callable[[Any], bool],
        color: str,
        columnas: Optional[List[str]] = None
    ):
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
        columnas_objetivo = self.columnas if self.columnas is not None else df.columns
        for columna in columnas_objetivo:
            if columna in df.columns:
                df[columna] = df[columna].apply(  # type: ignore
                    self._aplicar_color
                )
        return df

    def _aplicar_color(self, valor: Any) -> Any:
        if self.condicion(valor):
            return f'<span style="color: {self.color};">{valor}</span>'
        return valor


# -----------------------------------------------------------------------------
# Clase DataFrameBuilder
class DataFrameBuilder:
    def __init__(
        self,
        data: Optional[Union[pd.DataFrame, Dict[Any, Any], List[Dict[Any, Any]]]] = None
    ):
        """
        data : Puede ser un diccionario o una lista de diccionarios
        """
        if isinstance(data, pd.DataFrame):
            self._base_df = data.copy()
        else:
            self._base_df = pd.DataFrame(data) if data is not None else pd.DataFrame()
        self._operaciones: List[Operacion] = []
        self._operaciones_formato: List[OperacionFormato] = []

    def set_data(
        self,
        data: Union[pd.DataFrame, Dict[Any, Any], List[Dict[Any, Any]]]
    ):
        if isinstance(data, pd.DataFrame):
            self._base_df = data.copy()
        else:
            self._base_df = pd.DataFrame(data)
        return self

    def agregar_operacion(
        self,
        op: Operacion
    ):
        self._operaciones.append(op)
        return self

    def agregar_operacion_formato(
        self,
        op: OperacionFormato
    ):
        self._operaciones_formato.append(op)
        return self

    # Metodos helper para operaciones comunes
    def filtrar(self, condicion: Callable[[pd.DataFrame], pd.Series]):
        return self.agregar_operacion(FiltraOperacion(condicion))

    def agregar_columnas(self, mapeado: dict[str, Callable[[pd.DataFrame], pd.Series]]):
        return self.agregar_operacion(AgregarColumnasOperacion(mapeado))

    def cambiar_nombre_columnas(self, mapeado:  Dict[str, str]):
        return self.agregar_operacion(CambiarNombreColumnasOperacion(mapeado))

    def eliminar_columna(self, columna: Union[str, List[str]]):
        return self.agregar_operacion(EliminarColumnaOperacion(columna))

    def seleccionar_columna(self, columnas: Union[str, List[str]]):
        return self.agregar_operacion(SeleccionarColumnasOperacion(columnas))

    def agrupar_por(
        self,
        columnas: Union[str, List[str]],
        funcion_ag: Dict[Any, Any]
    ):
        return self.agregar_operacion(AgruparPorOperacion(columnas, funcion_ag))

    def explode_columna(self, columna: str):
        return self.agregar_operacion(ExplodeColumnaOperacion(columna))

    def expandir_lista_a_columnas(
        self,
        columna: str,
        prefijo: Optional[str] = None,
        drop_original: bool = True
    ):
        resultado = self.agregar_operacion(
            ExpandirListaColumnasOperacion(columna, prefijo, drop_original)
        )
        return resultado

    def ordenar_por(self, columna: str, ascendente: bool = True):
        return self.agregar_operacion(OrdenarPorOperacion(columna, ascendente))

    def transponer_filas_a_columnas(
        self,
        sep: str = "_",
        filas: Optional[List[Any]] = None
    ):
        """
        Agrega una operación que transforma (transpone) las filas seleccionadas en
        columnas.

        Parametros:
        ----------
        sep :   str
                Separador para unir el nombre de la columna original con el índice de la
                fila.
        filas : []
                Lista de índices a transponer. Si se omite o es None, se transponen
                todas las filas.

        Ejemplo:
            DataFrame original:

            ```
            | ID  |  A  | B   |
            |-----|-----|-----|
            | 0   | 1   | x   |
            | 1   | 2   | Y   |
            | 2   | 3   | Z   |
            ```

          Si filas = [0, 2] el resultado será:

            ```
            | A_0 | B_0 | A_2 | B_2 |
            |-----|-----|-----|-----|
            |  1  |  X  |  3  |  Z  |
            ```
        """
        return self.agregar_operacion(TransponerFilasAColumnasOperacion(sep, filas))

    def unir(
        self,
        otros: Union[pd.DataFrame, List[pd.DataFrame]],
        como: Literal[
            "inner",
            "left",
            "right",
            "outer",
            "cross",
            "left_anti",
            "right_anti"
        ] = "inner",
        en_izq: Optional[str] = None,
        en_der: Optional[str] = None,
        en: Optional[str] = None,
        sufijos: Union[
            List[Optional[str]],
            Tuple[str, str],
            Tuple[None, str],
            Tuple[str, None]
        ] = ("_x", "_y")
    ):
        resultado = self.agregar_operacion(
            InnerJoinOperacion(otros, como, en_izq, en_der, en, sufijos)
        )
        return resultado

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
        columna_resultado: str,
        formato: Optional[Union[str, Callable[[pd.Timedelta], str]]] = None
    ):
        self.agregar_operacion(
            DiferenciaTiempoOperacion(
                columna_inicio,
                columna_fin,
                columna_resultado,
                formato
            )
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
        condicion: Callable[[Any], bool],
        color: str,
        columnas: Optional[List[str]] = None
    ):
        self.agregar_operacion(
            CambiarColorTextoCondicionalOperacion(condicion, color, columnas)
        )
        return self

    def formatear_fecha(
        self,
        columnas: Union[str, List[str]],
        formato: str = '%d de %B de %Y, %H:%M:%S',
        locale_str: str = 'es_ES.UTF-8'
    ):
        self.agregar_operacion(
            FormatoFechaOperacion(columnas, formato, locale_str)
        )
        return self

    def formatear_html(
        self,
        color_texto: Optional[str] = None,
        columna_icono: Optional[str] = None,
        icon_mapping: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ):
        self.agregar_operacion_formato(
            FormatoHTMLOperacion(columna_icono, color_texto, icon_mapping, **kwargs)
        )
        return self

    def construir(self) -> pd.DataFrame:
        resultado = self._base_df.copy()
        # Operacion de datos
        for operacion in self._operaciones:
            resultado = operacion.apply(resultado)

        return resultado

    def construir_Html(self) -> str:
        resultado = self._base_df.copy()
        # Operacion de datos
        for operacion in self._operaciones:
            resultado = operacion.apply(resultado)
        # Operaciones de formato
        if not self._operaciones_formato:
            raise RuntimeError(
                "Debe existir al menos una operacion final de formato para devolver \
                str, al construir HMTL de una DataFrame"
            )
        resultado_formato: Optional[str] = None
        for operacion in self._operaciones_formato:
            resultado_formato = operacion.apply(resultado)

        if resultado_formato is None:
            raise RuntimeError(
                "La operacion final no devolvio un resultado valido."
            )

        return resultado_formato


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
