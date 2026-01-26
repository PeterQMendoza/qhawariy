import logging
import os
from typing import Any, List, cast
import pandas as pd

from datetime import (
    datetime,
    timedelta
)

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    send_from_directory,
    stream_template,
    url_for,
    request
)
from flask_login import login_required  # type: ignore

# from werkzeug.urls import url_parse
from urllib.parse import urlparse

from qhawariy.models.disponible_vehiculo import DisponibleVehiculo
from qhawariy.models.fecha import Fecha
from qhawariy.models.ruta import Ruta
from qhawariy.models.programacion import Programacion
from qhawariy.models.ruta_terminal import RutaTerminal
from qhawariy.models.vehiculo import Vehiculo
from qhawariy.models.vehiculo_programado import VehiculoProgramado
from qhawariy.forms.programacion_form import (
    ProgramacionForm,
    AgregaVehiculoProgramadoForm,
    BuscarProgramacionForm
)
from qhawariy.services.data_service.dataset_factory import DatasetFactory
from qhawariy.utilities.decorators import operacion_required
from qhawariy.utilities.files import FactoryExcel
from qhawariy.utilities.helpers import convertir_DataFrame
from qhawariy.utilities.builtins import LIMA_TZ

logger = logging.getLogger(__name__)

# Blueprint
bp = Blueprint("programacion", __name__, url_prefix="/programacion")


@bp.route("/agregar", methods=["GET", "POST"])
@login_required
@operacion_required
def agregar_programacion():
    """"
    Muestra la lista de programaciones guardadas.
    Ademas permite agregar una nueva programacion
    """
    busqueda = Programacion.obtener_programas()
    rutas = Ruta.obtener_todos_rutas()

    form = ProgramacionForm()
    form.ruta.choices = [(r.id_ruta, r.codigo) for r in rutas]

    if form.validate_on_submit():  # type: ignore
        ruta_f = form.ruta.data
        fecha_programa = cast(datetime, form.fecha_programa.data)

        # Buscar y crear fecha
        fp = Fecha.obtener_fecha_por_fecha(fecha_programa)
        if fp is None:
            fecha = Fecha(fecha_programa)
            fecha.guardar()
            id_fecha = fecha.id_fecha
        else:
            id_fecha = fp.id_fecha

        # Verificar si existe programacion para esa fecha y ruta
        unico_fr = Programacion.obtener_por_fecha_y_ruta(
            fecha=id_fecha,
            ruta=ruta_f
        )

        if unico_fr is None:
            programa = Programacion(id_fecha, ruta_f)
            programa.guardar()

            siguiente_pagina = request.args.get("next", None)
            if not siguiente_pagina or urlparse(siguiente_pagina).netloc != '':
                siguiente_pagina = url_for("programacion.agregar_programacion")
            return redirect(siguiente_pagina)
        else:
            ruta_obj = Ruta.obtener_ruta_por_id(ruta_f)
            if ruta_obj is None:
                flash(
                    message=f"No se encontro la ruta con id {ruta_f}",
                    category='error'
                )
            else:
                flash(
                    message=(
                        f"Ya existe una programación con fecha: "
                        f"{fecha_programa} y ruta con código:"
                        f"{Ruta.obtener_ruta_por_id(ruta_f).codigo}"  # type: ignore
                    ),
                    category='error'
                )
    return render_template(
        "programacion/lista_programacion.html",
        form=form,
        programas=busqueda,
        rutas=rutas
    )


#
@bp.route("/agrega_vehiculo/<int:programacion_id>/", methods=["GET", "POST"])
@login_required
@operacion_required
def agregar_vehiculo_programado(programacion_id: int):
    """
    Ruta que permite agregar vehiculos a una programacion
    param: programacion_id valor entero que representa el id de programacion
    """
    pro = Programacion.obtener_programacion_por_id(programacion_id)
    if pro is None:
        flash("No se encontró la programación solicitada.", category="error")
        return redirect(url_for("programacion.agregar_programacion"))

    ruta = Ruta.obtener_ruta_por_id(pro.id_ruta)
    lista_vp = VehiculoProgramado.obtener_vp_join_vehiculo(programacion_id)

    # Mostrar solo los vehiculos disponibles de acuerdo a la fecha establecido
    # en el programa
    fecha = pro.fecha
    dv = DisponibleVehiculo.obtener_vehiculos_disponibles(fecha.fecha)

    if dv:
        vehiculos = [v.vehiculo for v in dv]
    else:
        vehiculos = Vehiculo.obtener_todos_vehiculos_activos()

    form = AgregaVehiculoProgramadoForm()
    form.vehiculo.choices = [
        (v.id_vehiculo, f"{v.flota}: {v.placa}") for v in vehiculos
    ]
    if form.validate_on_submit():  # type: ignore
        vp = form.vehiculo.data
        tiempo = cast(datetime, form.tiempo.data)
        vehiculo_en_espera = form.vehiculo_en_espera.data

        # Validar que no se repita el mismo vehiculo en la programacion
        vehiculo_unico = VehiculoProgramado.obtener_vp_por_programacion_y_id_vehiculo(
            programacion_id=programacion_id,
            vehiculo_id=vp
        )

        if vehiculo_unico is None:
            # Validar que no se repita el mismo tiempo
            tiempo_unico = VehiculoProgramado.obtener_vp_por_programacion_y_tiempo(
                programacion_id=programacion_id,
                tiempo=tiempo
            )
            if tiempo_unico is None:
                vehiculo_programado = VehiculoProgramado(
                    tiempo,
                    vehiculo_en_espera,
                    vp,
                    programacion_id
                )
                vehiculo_programado.guardar()

                siguiente_pagina = request.args.get("next", None)
                if not siguiente_pagina or urlparse(siguiente_pagina).netloc != '':
                    siguiente_pagina = url_for(
                        "programacion.agregar_vehiculo_programado",
                        programacion_id=pro.id_programacion
                    )
                return redirect(siguiente_pagina)
            else:
                flash(
                    message=f"El tiempo de salida debe ser único, ya hay un vehicul\
                    o con salida:{tiempo}",
                    category='error'
                )
        else:
            vehiculo_obj = Vehiculo.obtener_vehiculo_por_id(vp)
            flota = vehiculo_obj.flota if vehiculo_obj else "desconocida"
            flash(
                message=f"Ya existe una programacion con la flota:{flota}",
                category='error'
            )
    return render_template(
        "programacion/lista_vehiculo_programado.html",
        form=form,
        error_espera=None,
        programa=pro,
        vps=lista_vp,
        ruta=ruta
    )


@bp.route("/eliminar_vehiculo/<int:vp_id>/", methods=["GET", "POST"])
@login_required
@operacion_required
def eliminar_vehiculo_programado(vp_id: int):
    vp = VehiculoProgramado.obtener_vp_por_id(vp_id)
    # excepcion de eliminar valores nulo..
    if vp is None:
        flash("No se encontro el vehiculo programado.", category="error")
        return redirect(url_for("programacion.agregar_programacion"))

    vp.eliminar()
    return redirect(url_for(
        "programacion.agregar_vehiculo_programado",
        programacion_id=vp.id_programacion
    ))


@bp.route("/eliminar_programacion/<int:p_id>/", methods=["GET", "POST"])
@login_required
@operacion_required
def eliminar_programacion(p_id: int):
    p = Programacion.obtener_programacion_por_id(p_id)
    if p is None:
        flash("No se encontro la programacion solicitada", "error")
    else:
        p.eliminar()
        flash("Programacion eliminada correctamente", "success")

    # Determinar pagina de redireccion
    siguiente_pagina = request.args.get("next", None)
    if not siguiente_pagina or urlparse(siguiente_pagina).netloc != "":
        siguiente_pagina = url_for("programacion.agregar_programacion")
    return redirect(siguiente_pagina)


@bp.route("/descarga/<name>", methods=["GET", "POST"])
@login_required
@operacion_required
def descargar_resumen(name: str):
    descarga_folder = cast(str, current_app.config["DOWNLOAD_FOLDER"])

    # Construir ruta absoluta y alidar que el archivo existe
    file_path = os.path.join(descarga_folder, name)
    if not os.path.isfile(file_path):
        abort(404, descrition="Archivo no encontrado")
    return send_from_directory(descarga_folder, name, as_attachment=True)


@bp.route("/resumen", methods=["GET"])
@login_required
@operacion_required
def cargar_resumen():
    return stream_template(
        "loading.html",
        path="resumen/",
        title="Cargando resumen",
        filename='actual'
    )


@bp.route("/resumen/<string:fecha>", methods=["GET", "POST"])
@login_required
@operacion_required
def mostrar_resumen_semana(fecha: str):
    # CORREGIR ERROR CUANDO NO SE TIENE PROGRAMACIONES
    # Formulario de busqueda
    try:
        ahora = datetime.strptime(fecha, "%Y-%m-%d")
    except Exception:
        ahora = datetime.now(tz=LIMA_TZ)

    form = BuscarProgramacionForm()
    if form.validate_on_submit():  # type: ignore
        fecha_busca = form.fecha.data
        siguiente_pagina = request.args.get("next", None)
        if not siguiente_pagina or urlparse(siguiente_pagina).netloc != '':
            siguiente_pagina = url_for(
                "programacion.mostrar_resumen_semana",
                fecha=fecha_busca
            )
        return redirect(siguiente_pagina)

    aux = datetime.weekday(ahora)
    # fecha de hace 7 dias (de acuerdo al requerimiento)
    inicio_semana = ahora-timedelta(days=aux)
    fin_semana = ahora+timedelta(days=6-aux)

    # obtener los vehiculos programados de la semana (no todos)
    vehiculos = VehiculoProgramado.obtener_todos_vp_fecha(
        desde=inicio_semana,
        hasta=fin_semana
    )

    # Obtener vehiculos en espera
    vehiculos_en_espera = VehiculoProgramado.obtener_todos_vp_en_espera_fecha(
        desde=inicio_semana,
        hasta=fin_semana
    )

    if not vehiculos:
        # Es necesario tener una programacion de vehiculo
        # Muestra ultima programacion de vehiculo
        flash("Todavia no has realizados programaciones para esta fecha", "info")
        ultimo = VehiculoProgramado.obtener_vp_ultimo()
        if ultimo:
            vehiculos = [ultimo]
        else:
            vehiculos = []

    # obtener informacion por cada rutas
    rutas_terminal = RutaTerminal.obtener_todas_rt()
    recorridos = [
        f"De: {rt.terminal.direccion} A:{rt.terminal2.direccion}"
        for rt in rutas_terminal
    ]
    date_str = "De {} al {}".format(
        inicio_semana.strftime("%A %d de %B de %Y"),
        fin_semana.strftime("%A %d de %B de %Y")
    )
    rutas = [a.ruta.codigo for a in rutas_terminal]

    # procesar los datos
    rutas_vehiculos = [
        RutaTerminal.obtener_rt_por_ruta(
            v.programa.id_ruta  # type: ignore
        ).ruta.codigo for v in vehiculos if v is not None  # type: ignore
    ] or rutas

    resumen = procesar_data(vehiculos, rutas_vehiculos)
    # de espera
    if not vehiculos_en_espera:
        data_espera = pd.DataFrame()
    else:
        ultimo_espera = VehiculoProgramado.obtener_vp_ultimo_espera()
        vehiculos_en_espera = [ultimo_espera] if ultimo_espera else []
        data_espera = procesar_data_espera(vehiculos_en_espera, ahora)

    # obtener DataFrame por cada ruta
    list_df: list[pd.DataFrame] = []
    dict_df: list[dict[str, pd.DataFrame]] = []
    for idx, ruta in enumerate(rutas):
        tabla_df = tabla(ruta=idx, data=resumen, rutas=rutas, date=ahora)
        list_df.append(tabla_df)
        dict_df.append({ruta: tabla_df})

    # Crear archivo excel para el resumen
    filename = "Resumen_programacion_{}_{}".format(
        inicio_semana.strftime("%d-%m-%Y"),
        fin_semana.strftime("%d-%m-%Y")
    )

    # Agregar la tabla de vehiculos en espera al final
    rutas.append("Vehiculos en espera")
    list_df.append(data_espera)
    dict_df.append({rutas[-1]: data_espera})
    recorridos.append("Lista de vehiculos en espera")

    try:
        excel = FactoryExcel()
        excel.crearArchivo(
            filename=filename,
            dataframe=list_df,
            recorrido=recorridos,
            date=date_str,
            sheetnames=rutas,
            tipo='resumen'
        ).guardar()
    except ValueError as e:
        logger.error(f"error: {e}")

    return render_template(
        "programacion/resumen_programacion.html",
        filename=f"{filename}.xlsx",
        data1=list_df[0] if len(list_df) > 0 else None,
        data2=list_df[1] if len(list_df) > 1 else None,
        data3=list_df[2] if len(list_df) > 2 else None,
        data4=list_df[3] if len(list_df) > 3 else None,
        df=dict_df,
        test=vehiculos,
        rt=rutas_terminal,
        form=form,
        fecha_inicio=inicio_semana,
        fecha_fin=fin_semana
    )


@bp.route("/ver_diaria", methods=["GET", "POST"])
@login_required
@operacion_required
def ver_diario_programacion():
    # obtener la programacion de vehiculos por fecha
    ahora = datetime.now(LIMA_TZ)
    ahora = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    rutas = Ruta.obtener_todos_rutas()

    #
    ida: List[Any] = []
    vuelta: List[Any] = []
    vehiculos_ida: List[Any] = []
    vehiculos_vuelta: List[Any] = []

    # Clasificacion programacion por ruta
    for ruta in rutas:
        vp = VehiculoProgramado.vista_diaria(ahora, ruta.id_ruta)
        if ruta.id_ruta == 1:
            ida.extend(vp)  # type: ignore
            vehiculos_ida.extend([v.vehiculo for v in vp])  # type: ignore

        elif ruta.id_ruta in (2, 3):
            vuelta.extend(vp)  # type: ignore
            vehiculos_vuelta.extend([v.vehiculo for v in vp])  # type: ignore

    # Validar si no hay programaciones
    if not vehiculos_ida and not vehiculos_vuelta:
        flash(f"No existe programacion para hoy {ahora.strftime('%d/%m/%Y')}", "info")
        return render_template("programacion/vista_diaria.html", data1='', data2='')

    # Procesar datasets
    dataset = DatasetFactory()

    dts_ida = dataset.create_dataset(ida, vehiculos_ida)
    dts_ida.proccess_dataframe()
    dts_ida_html = dts_ida.dataframe.to_html(
        classes='table table-striped',
        index=True,
        escape=False
    )
    dts_vuelta = dataset.create_dataset(vuelta, vehiculos_vuelta)
    dts_vuelta.proccess_dataframe()
    dts_vuelta_html = dts_vuelta.dataframe.to_html(
        classes='table table-striped',
        index=True,
        escape=False
    )

    return render_template(
        "programacion/vista_diaria.html",
        data1=dts_ida_html,
        data2=dts_vuelta_html
    )


def procesar_data(data: List[Any], rutas: List[Any]):
    columnas = ['fecha_programa', 'Tiempo', 'flota', 'ruta']
    if not data:
        return pd.DataFrame(columns=columnas)

    # Convertir lista de objetos a DataFrame
    resumen = convertir_DataFrame(data)

    # Eliminar columnas innecesarias
    if "id_vp" in resumen.columns:
        resumen = resumen.drop(columns=["id_vp"])

    # Agregar columnas calculadas
    resumen['ruta'] = rutas
    resumen.id_programacion = [a.programa.fecha.fecha.date() for a in data]
    resumen.id_vehiculo = [str(a.vehiculo.flota) for a in data]

    # Renombrae columnas
    resumen = resumen.rename(
        columns={
            "id_programacion": "fecha_programa",
            "id_vehiculo": "flota",
            "tiempo": "Tiempo"
        }
    )
    # Reordenar columnas
    resumen = resumen.reindex(columns=columnas)  # type: ignore
    return resumen


def procesar_data_espera(data: List[Any], date: datetime):
    resumen = convertir_DataFrame(data)

    resumen = resumen.drop(columns=["tiempo", "vehiculo_en_espera"])
    resumen = resumen.rename(columns={"id_vp": "vp"})

    resumen.id_programacion = [a.programa.fecha.fecha.date() for a in data]
    resumen.id_vehiculo = [str(a.vehiculo.flota) for a in data]

    # Generar lista de fechas de las semana
    semana = date.weekday()  # lunes=0, domingo=6
    inicio_semana = date - timedelta(days=semana)
    lista_fecha = [inicio_semana + timedelta(days=i) for i in range(7)]

    # crear dataframe con los vp unicos
    df_espera = pd.DataFrame(data=resumen.vp)
    df_espera = df_espera.drop_duplicates()
    df_espera = df_espera.set_index("vp")  # type: ignore

    # Construir columnas por cada dia de la semana
    for fecha in lista_fecha:
        d_aux = resumen.loc[
            resumen.id_programacion == fecha.date()
        ]
        d_aux = d_aux.drop(columns=['id_programacion'])
        d_salida = d_aux.set_index('vp')  # type: ignore
        df_espera[fecha.strftime('%A %d')] = d_salida

    # Limpieza final
    df_espera = df_espera.sort_index()  # type: ignore
    df_espera = df_espera.dropna(how='all')  # type: ignore
    df_espera = df_espera.fillna(value='')  # type: ignore

    return df_espera


# funcion auxiliar para crear tablas
def tabla(
    ruta: int,
    data: pd.DataFrame,
    rutas: List[Any],
    date: datetime
) -> pd.DataFrame:
    # Generar lista de fechas de las semana
    semana = date.weekday()  # lunes=0, domingo=6
    inicio_semana = date - timedelta(days=semana)
    lista_fecha = [inicio_semana + timedelta(days=i) for i in range(7)]

    # Crear dataframe base con tiempos unicos
    data_resultado = data[["Tiempo"]].drop_duplicates().set_index('Tiempo')  # type: ignore

    # Iterar sobre cada dia de la semana
    ruta_actual = rutas[ruta]
    for fecha in lista_fecha:
        # Filtrar por fecha y ruta
        d_aux = data.loc[data.fecha_programa == fecha.date()]
        d_salida = d_aux.loc[d_aux.ruta == ruta_actual]  # type: ignore

        # Eliminamos columnas innecesarias
        d_salida = d_salida.drop(  # type: ignore
            columns=[
                    c for c in ['fecha_programa', 'ruta']
                    if c in d_salida.columns  # type: ignore
            ]
        )
        # Establecer index en tiempo
        d_salida = d_salida.set_index('Tiempo')  # type: ignore

        # Anadir columna a resultado
        data_resultado[fecha.strftime('%A %d')] = d_salida

    # Limpieza final
    data_resultado = data_resultado.sort_index()  # type: ignore
    data_resultado = data_resultado.dropna(how='all')  # type: ignore
    data_resultado = data_resultado.fillna(value='')  # type: ignore
    return data_resultado
