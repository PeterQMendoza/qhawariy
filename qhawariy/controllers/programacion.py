import datetime

import logging
import pandas as pd

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    send_from_directory,
    stream_template,
    url_for,
    request
)
from flask_login import login_required

# from werkzeug.urls import url_parse
from urllib.parse import urlparse

from qhawariy.controllers.decorators.auth import operacion_required
from qhawariy.models.disponible_vehiculo import DisponibleVehiculo
from qhawariy.models.fecha import Fecha
from qhawariy.models.ruta import Ruta
from qhawariy.models.programacion import Programacion
from qhawariy.models.ruta_terminal import RutaTerminal
from qhawariy.models.vehiculo import Vehiculo
from qhawariy.models.vehiculo_programado import VehiculoProgramado
from qhawariy.controllers.forms.programacion_form import (
    ProgramacionForm,
    AgregaVehiculoProgramadoForm,
    BuscarProgramacionForm
)
from qhawariy.controllers.datasets.dataset_factory import DatasetFactory
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
    if form.validate_on_submit():
        ruta_f = form.ruta.data
        fecha_programa = form.fecha_programa.data
        # Crear una programacion con fecha y ruta unica
        fp = Fecha.obtener_fecha_por_fecha(fecha_programa)
        if fp is None:
            fecha = Fecha(fecha_programa)
            fecha.guardar()
            unico_fr = Programacion.obtener_por_fecha_y_ruta(
                fecha=fecha.id_fecha,
                ruta=ruta_f
            )
            if unico_fr is None:
                programa = Programacion(fecha.id_fecha, ruta_f)
                programa.guardar()
                siguiente_pagina = request.args.get("next", None)
                if not siguiente_pagina or urlparse(siguiente_pagina).netloc != '':
                    siguiente_pagina = url_for("programacion.agregar_programacion")
                return redirect(siguiente_pagina)
        else:
            unico_fr = Programacion.obtener_por_fecha_y_ruta(
                fecha=fp.id_fecha,
                ruta=ruta_f
            )
            if unico_fr is None:
                programa = Programacion(fp.id_fecha, ruta_f)
                programa.guardar()
                siguiente_pagina = request.args.get("next", None)
                if not siguiente_pagina or urlparse(siguiente_pagina).netloc != '':
                    siguiente_pagina = url_for("programacion.agregar_programacion")
                return redirect(siguiente_pagina)
            else:
                flash(
                    message="""La ya existe una programación con fecha: {t} y ruta con
                    código:{r}""".format(
                        t=fecha_programa,
                        r=Ruta.obtener_ruta_por_id(ruta_f).codigo
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
def agregar_vehiculo_programado(programacion_id):
    """Ruta que permite agregar vehiculos a una programacion
        param: programacion_id valor entero que representa el id de programacion
    """
    pro = Programacion.obtener_programacion_por_id(programacion_id)
    ruta = Ruta.obtener_ruta_por_id(pro.id_ruta)
    lista_vp = VehiculoProgramado.obtener_vp_join_vehiculo(programacion_id)

    # Mostrar solo los vehiculos disponibles de acuerdo a la fecha establecido
    # en el programa
    fecha = pro.fecha
    dv = DisponibleVehiculo.obtener_vehiculos_disponibles(fecha.fecha)
    vehiculos = []
    if dv is not None:
        for v in dv:
            vehiculos.append(v.vehiculo)
    else:
        vehiculos = Vehiculo.obtener_todos_vehiculos_activos()

    form = AgregaVehiculoProgramadoForm()
    form.vehiculo.choices = [
        (v.id_vehiculo, str(v.flota)+": "+v.placa)for v in vehiculos
    ]
    if form.validate_on_submit():
        vp = form.vehiculo.data
        tiempo = form.tiempo.data
        vehiculo_en_espera = form.vehiculo_en_espera.data
        # Realizar programacion una vez por vehiculo y con tiempo unico
        vehiculo_unico = VehiculoProgramado.obtener_vp_por_programacion_y_id_vehiculo(
            programacion_id=programacion_id,
            vehiculo_id=vp
        )
        if vehiculo_unico is None:
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
                    message="""El tiempo de salida debe ser único, ya hay un vehicul
                    o con salida:{t}""".format(t=tiempo),
                    category='error'
                )
        else:
            flash(
                message="""Ya existe una programacion con la flota
                :{v}""".format(v=Vehiculo.obtener_vehiculo_por_id(vp).flota),
                category='error'
            )
    return render_template(
        "programacion/lista_vehiculo_programado.html",
        form=form,
        programa=pro,
        vps=lista_vp,
        ruta=ruta
    )


@bp.route("/eliminar_vehiculo/<int:vp_id>/", methods=["GET", "POST"])
@login_required
@operacion_required
def eliminar_vehiculo_programado(vp_id):
    vp = VehiculoProgramado.obtener_vp_por_id(vp_id)
    # excepcion de eliminar valores nulo..
    if vp is not None:
        vp.eliminar()
    return redirect(url_for(
        "programacion.agregar_vehiculo_programado",
        programacion_id=vp.id_programacion
    ))


@bp.route("/eliminar_programacion/<int:p_id>/", methods=["GET", "POST"])
@login_required
@operacion_required
def eliminar_programacion(p_id):
    p = Programacion.obtener_programacion_por_id(p_id)
    if p is not None:
        p.eliminar()
        siguiente_pagina = request.args.get("next", None)
        if not siguiente_pagina or urlparse(siguiente_pagina).netloc != '':
            siguiente_pagina = url_for("programacion.agregar_programacion")
        return redirect(siguiente_pagina)
    return redirect(url_for("programacion.agregar_programacion"))


@bp.route("/descarga/<name>", methods=["GET", "POST"])
@login_required
@operacion_required
def descargar_resumen(name):
    return send_from_directory(current_app.config["DOWNLOAD_FOLDER"], name)


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
def mostrar_resumen_semana(fecha):
    # CORREGIR ERROR CUANDO NO SE TIENE PROGRAMACIONES
    # Formulario de busqueda
    try:
        ahora = datetime.datetime.strptime(fecha, "%Y-%m-%d")
    except Exception:
        ahora = datetime.datetime.now(tz=LIMA_TZ)

    form = BuscarProgramacionForm()
    if form.validate_on_submit():
        fecha_busca = form.fecha.data
        siguiente_pagina = request.args.get("next", None)
        if not siguiente_pagina or urlparse(siguiente_pagina).netloc != '':
            siguiente_pagina = url_for(
                "programacion.mostrar_resumen_semana",
                fecha=fecha_busca
            )
        return redirect(siguiente_pagina)

    aux = datetime.datetime.weekday(ahora)
    # fecha de hace 7 dias (de acuerdo al requerimiento)
    inicio_semana = ahora-datetime.timedelta(days=aux)
    fin_semana = ahora+datetime.timedelta(days=6-aux)

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

    if vehiculos == []:
        # Es necesario tener una programacion de vehiculo
        vehiculos = [VehiculoProgramado.obtener_vp_ultimo()]
        flash("Todavia no has realizados programaciones para esta fecha", "info")

    if vehiculos_en_espera == []:
        vehiculos_en_espera = [VehiculoProgramado.obtener_vp_ultimo_espera()]

    # obtener informacion por cada rutas
    rutas_terminal = RutaTerminal.obtener_todas_rt()
    recorridos = [
        "De:"+a.terminal.direccion+" A:"+a.terminal2.direccion for a in rutas_terminal
    ]
    date_str = inicio_semana.strftime("%A %d de %B de %Y")
    date_str = date_str.join(" al "+fin_semana.strftime("%A %d de %B de %Y"))
    rutas = [a.ruta.codigo for a in rutas_terminal]

    # procesar los datos
    rutas_vehiculos = [
        RutaTerminal.obtener_rt_por_ruta(
            a.programa.id_ruta
        ).ruta.codigo for a in vehiculos
    ]

    resumen = procesar_data(vehiculos, rutas_vehiculos)
    # de espera
    data_espera = procesar_data_espera(vehiculos_en_espera, ahora)

    # obtener df por cada ruta
    list_df = []
    dict_df = []
    for a in range(len(rutas)):
        aux = tabla(ruta=a, data=resumen, rutas=rutas, date=ahora)
        list_df.append(aux)
        dict_df.append({rutas[a]: aux})

    # Crear archivo excel para el resumen
    filename = 'Resumen_programacion'+"_"+inicio_semana.strftime("%d-%m-%Y")
    filename = filename.join("_"+fin_semana.strftime("%d-%m-%Y"))

    # Agregar la tabla de vehiculos en espera al final
    rutas.append("Vehiculos en espera")
    list_df.append(data_espera)
    dict_df.append({rutas[-1]: data_espera})
    recorridos.append("Lista de vehiculos en espera")

    excel = FactoryExcel()
    excel.crearArchivo(
        filename=filename,
        dataframe=list_df,
        recorrido=recorridos,
        date=date_str,
        sheetnames=rutas,
        tipo='resumen'
    ).guardar()

    return render_template(
        "programacion/resumen_programacion.html",
        filename=filename+".xlsx",
        data1=list_df[0],
        data2=list_df[1],
        data3=list_df[2],
        data4=list_df[3],
        df=dict_df,
        test=resumen,
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
    ahora = datetime.datetime.now(LIMA_TZ)
    ahora = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    rutas = Ruta.obtener_todos_rutas()

    #
    ida = []
    vuelta = []
    vehiculos_ida = []
    vehiculos_vuelta = []
    for r in rutas:
        vp = VehiculoProgramado.vista_diaria(ahora, r.id_ruta)
        if r.id_ruta == 1:
            ida.extend(vp)
            vehiculos_ida.extend([v.vehiculo for v in vp])

        if r.id_ruta == 2 or r.id_ruta == 3:
            vuelta.extend(vp)
            vehiculos_vuelta.extend([v.vehiculo for v in vp])

    if vehiculos_ida == [] and vehiculos_vuelta == []:
        flash(f"No existe programacion para hoy {ahora}", "info")
        return render_template("programacion/vista_diaria.html", data1='', data2='')

    dataset = DatasetFactory()
    dts_ida = dataset.create_dataset(ida, vehiculos_ida)
    dts_ida.process_dataframe()
    dts_ida_html = dts_ida._dataframe.to_html(
        classes='table table-striped',
        index=True,
        escape=False
    )
    dts_vuelta = dataset.create_dataset(vuelta, vehiculos_vuelta)
    dts_vuelta.process_dataframe()
    dts_vuelta_html = dts_vuelta._dataframe.to_html(
        classes='table table-striped',
        index=True,
        escape=False
    )

    return render_template(
        "programacion/vista_diaria.html",
        data1=dts_ida_html,
        data2=dts_vuelta_html
    )


def procesar_data(data, rutas):
    resumen = convertir_DataFrame(data)
    # eliminar la primera columna id_vp
    resumen = resumen.drop(columns=["id_vp"])

    # El filtrado debe ser por ruta y mostrar en estadistica por ruta y salida
    resumen['ruta'] = rutas
    resumen.id_programacion = [a.programa.fecha.fecha.date() for a in data]
    resumen.id_vehiculo = [str(a.vehiculo.flota) for a in data]
    # cambiar el nombre de la columnas
    resumen = resumen.rename(columns={"id_programacion": "fecha_programa"})
    resumen = resumen.rename(columns={"id_vehiculo": "flota"})
    resumen = resumen.rename(columns={"tiempo": "Tiempo"})
    # cambiar el orden de las columnas
    resumen = resumen.reindex(columns=['fecha_programa', 'Tiempo', 'flota', 'ruta'])
    return resumen


def procesar_data_espera(data: list, date: datetime.datetime):
    resumen = convertir_DataFrame(data)
    resumen = resumen.drop(columns=["tiempo", "vehiculo_en_espera"])
    resumen = resumen.rename(columns={"id_vp": "vp"})

    resumen.id_programacion = [a.programa.fecha.fecha.date() for a in data]
    resumen.id_vehiculo = [str(a.vehiculo.flota) for a in data]

    tiempo = date
    # Generamos una lista de las fechas de las semana
    lista_fecha = []
    aux = tiempo.weekday()
    for a in range(aux):
        t = tiempo-datetime.timedelta(days=(aux-a))
        lista_fecha.append(t)
    for c in range(7-aux):
        t = tiempo+datetime.timedelta(days=c)
        lista_fecha.append(t)
    # crear dataframe por cada dia de la semana
    df_espera = pd.DataFrame(data=resumen.vp)
    df_espera = df_espera.drop_duplicates()
    df_espera = df_espera.set_index("vp")
    # a=ruta
    for b in range(len(lista_fecha)):
        d_aux = resumen.loc[resumen.id_programacion == lista_fecha[b].date()]
        # Salida_1
        # eliminamos todas las columnas no necesarias
        d_aux = d_aux.drop(columns=['id_programacion'])
        d_salida = d_aux.set_index('vp')
        df_espera[lista_fecha[b].strftime('%A %d')] = d_salida
    df_espera = df_espera.sort_index()
    df_espera = df_espera.dropna(how='all')
    df_espera = df_espera.fillna(value='')

    return df_espera


# funcion auxiliar para crear tablas
def tabla(ruta, data, rutas, date):
    tiempo = date
    # Generamos una lista de las fechas de las semana
    lista_fecha = []
    aux = tiempo.weekday()
    for a in range(aux):
        t = tiempo-datetime.timedelta(days=(aux-a))
        lista_fecha.append(t)
    for c in range(7-aux):
        t = tiempo+datetime.timedelta(days=c)
        lista_fecha.append(t)
    # crear dataframe por cada dia de la semana
    data_t = pd.DataFrame(data=data.Tiempo)
    data_t = data_t.drop_duplicates()
    data_resultado = data_t.set_index('Tiempo')
    a = ruta
    for b in range(len(lista_fecha)):
        d_aux = data.loc[data.fecha_programa == lista_fecha[b].date()]
        # Salida_1
        d_salida = d_aux.loc[d_aux.ruta == rutas[a]]
        # eliminamos todas las columnas no necesarias
        d_salida = d_salida.drop(columns=['fecha_programa', 'ruta'])
        # establecemos el index al tiempo de salida
        d_salida = d_salida.set_index('Tiempo')
        # data_resultado=data_resultado.merge(d_salida)
        data_resultado[lista_fecha[b].strftime('%A %d')] = d_salida
    data_resultado = data_resultado.sort_index()
    data_resultado = data_resultado.dropna(how='all')
    data_resultado = data_resultado.fillna(value='')
    return data_resultado
