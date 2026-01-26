import logging
from typing import List, Optional, TypedDict
from flask.typing import ResponseReturnValue
import folium.plugins
import pandas as pd
import datetime
import copy

import folium
from folium.plugins import (
    AntPath
)

from flask import (
    Blueprint,
    g,
    render_template,
    current_app
)
from flask_login import (
    login_required,  # type: ignore
    current_user
)
# from werkzeug.urls import url_parse
# from urllib.parse import urlparse

from qhawariy.models.fecha import Fecha
from qhawariy.models.propietario_vehiculo import PropietarioVehiculo
from qhawariy.models.propietario import Propietario
from qhawariy.models.ruta_terminal import RutaTerminal
from qhawariy.models.terminal import Terminal
from qhawariy.models.usuario_rol import UsuarioRol
from qhawariy.models.vehiculo import Vehiculo
from qhawariy.models.vehiculo_programado import VehiculoProgramado
from qhawariy.models.viaje import Viaje
from qhawariy.models.control import Control

from qhawariy.utilities.builtins import COLORES, LIMA_TZ
from qhawariy.utilities.files import FactoryShapefile
# from qhawariy.utilities.helpers import a_dict

logger = logging.getLogger(__name__)

# Blueprint
bp = Blueprint("estadistica", __name__, url_prefix="/estadistica")


class PuntoFlota(TypedDict):
    x: str
    y: int


class TiempoVP(TypedDict):
    Flota: str
    Tiempo: Optional[datetime.datetime]
    Ruta: str


def ordenar_valor(lista: list[PuntoFlota]) -> list[PuntoFlota]:
    """Ordena lista de diccionarios por el valor y en orden descendente"""
    n = len(lista)
    for i in range(n):
        swapped = False
        for j in range(0, n-i-1):
            if lista[j]['y'] < lista[j+1]['y']:
                lista[j], lista[j+1] = lista[j+1], lista[j]
                swapped = True
        if not swapped:
            break
    return lista


def inicializar_copia_vacia(base: List[dict[str, int]]) -> List[dict[str, int]]:
    """Devuelve una copia vacia profunda con valores 'y' inicializados"""
    copia = copy.deepcopy(base)
    for em in copia:
        em.update(y=0)
    return copia


@bp.route("/estadistica", methods=["GET", "POST"])
@login_required
def mostrar_estadisticas() -> ResponseReturnValue:
    # Validacion de usuario
    if not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()  # type: ignore

    id_user = current_user.id_usuario
    ur = UsuarioRol.obtener_por_id_usuario(id_user)
    rol = ur.rol if ur else None

    # Fechas y datos base
    fechas = Fecha.obtener_todas_fechas()
    lista_fechas = [f.fecha for f in fechas]
    dat1 = VehiculoProgramado.estadistica_vp_fecha_programa()
    data_list1 = [{'x': v.strftime('%d-%m-%Y'), 'y': r} for _, v, r in dat1]

    # Rutas y secuencias
    rutas = RutaTerminal.obtener_todas_rt()
    lista_rutas = [
        VehiculoProgramado.estadistica_vp_fecha_programa_y_ruta(lr.ruta.id_ruta)
        for lr in rutas
    ]

    empty = inicializar_copia_vacia(data_list1)
    lista_copia_vacias = [
        copy.deepcopy(empty)
        for _ in rutas
    ]

    for i, ruta_data in enumerate(lista_rutas):
        for _, f, c in ruta_data:
            if f in lista_fechas:
                for em in lista_copia_vacias[i]:
                    if em['x'] == f.strftime('%d-%m-%Y'):
                        em.update({'x': f.strftime('%d-%m-%Y'), 'y': c})

    # Estadistica por flota
    dat2 = VehiculoProgramado.estadistica_vp_flota_programa()
    vehiculos = Vehiculo.obtener_todos_vehiculos_activos()
    t_empty: List[PuntoFlota] = [
        {'x': f'Flota {v.flota}', 'y': 0} for v in vehiculos
    ]

    data_list2: List[PuntoFlota] = [
        {'x': f'Flota +{v}', 'y': r} for _, v, r in dat2
    ]

    # Ordenar dicccionario por valor
    for v in data_list2:
        for e in t_empty:
            if v['x'] == e['x']:
                e['y'] = v['y']
    t_empty = ordenar_valor(t_empty)

    # Programados vs no programados
    veh = Vehiculo.estadistica_todos_vehiculos_activos()
    dat3 = VehiculoProgramado.estadistica_vp_fecha_programado_no_programado()
    data_list3 = None
    if dat3:
        total = veh[0][1]
        dt = dat3[0][1].strftime('%d-%m-%Y')
        pro = dat3[0][2]
        data_list3 = [([pro, (total-pro)], dt)]
    else:
        data_list3 = []

    # GRAFICO DE LA DONA
    # Cantidad de vehiculos por ruta
    dat4 = VehiculoProgramado.estadistica_cantidad_vehiculos_por_ruta()
    data_list4 = {str(s): c for _, s, c in dat4}

    # GRAFICO DE BARRA PROPIETARIO
    # Conteo de vehiculo activo y no activo por propietario
    props = Propietario.obtener_todos_propietarios()
    propietarios = [f"{p.nombres} {p.apellidos}" for p in props]
    ids = [p.id_propietario for p in props]
    da = [0]*len(ids)
    dna = [0]*len(ids)

    dat_activo = PropietarioVehiculo.estadistica_pv_y_vehiculo_propietario(True)
    dat_no_activo = PropietarioVehiculo.estadistica_pv_y_vehiculo_propietario(False)
    data_list_activo = [{i: c} for _, i, c in dat_activo]
    data_list_no_activo = [{i: c} for _, i, c in dat_no_activo]

    for i in data_list_activo:
        for k, v in i.items():
            aux = ids.index(k)
            if k in ids:
                da[aux] = v
            else:
                da[aux] = 0
    for i in data_list_no_activo:
        for k, v in i.items():
            aux = ids.index(k)
            if k in ids:
                dna[aux] = v
            else:
                dna[aux] = 0

    # GRAFICO DE TIEMPOS
    # Para grafico de puntos
    vp = VehiculoProgramado.estadistica_vp_tiempos()
    tiempos = [
        {
            'tiempo': t.strftime("%H:%M"),
            'cantidad': c
        } for _, t, c in vp if t is not None
    ]

    # Estadistica para viajes
    # Cantidad de viajes hechos por vehiculos
    viajes_por_vehiculos = Viaje.estadistica_viajes_por_vehiculo()
    vpv: List[PuntoFlota] = [
        {'x': f"Flota{f}", 'y': conteo} for _, f, conteo in viajes_por_vehiculos
    ]
    vpvs: List[PuntoFlota] = [
        # Inicia con cada conteo de vehiculo 0
        {'x': 'Flota '+str(v.flota), 'y': 0} for v in vehiculos
    ]
    # Ordenar dicccionario por valor
    for v in vpv:
        for e in vpvs:
            if v['x'] == e['x']:
                e['y'] = v['y']
    vpvs = ordenar_valor(vpvs)

    # Cantidad de viajes por fecha y ruta
    total_viajes_por_fecha = Viaje.estadistica_viajes_por_fecha()
    lista_tvf = [
        {'x': f.strftime('%d-%m-%Y'), 'y': c} for _, f, c in total_viajes_por_fecha
    ]

    lvfr = inicializar_copia_vacia(lista_tvf)
    lvfrs = [copy.deepcopy(lvfr) for _ in rutas]

    for i, ruta_data in enumerate(
        [Viaje.estadistica_viajes_por_fecha_ruta(r.ruta.id_ruta) for r in rutas]
    ):
        for _, f, c in ruta_data:
            if f in lista_fechas:
                for em in lvfrs[i]:
                    if em['x'] == f.strftime('%d-%m-%Y'):

                        em.update({'y': c})

    return render_template(
        "estadistica/muestra_estadistica.html",
        rol=rol,
        data1=data_list1,
        lista_ruta_conteo=lista_copia_vacias,
        data2=t_empty,
        data3=data_list3,
        data4=data_list4,
        data5=da,
        data6=dna,
        data7=vpvs,
        data8=lista_tvf,
        lista_viajes_por_ruta_fecha=lvfrs,
        propietarios=propietarios,
        tiempos=tiempos,
        test=tiempos
    )


def obtener_intervalo_fecha() -> tuple[datetime.datetime, datetime.datetime]:
    """Devuelve el intervalo entre ayer y ahora en la zona horaria LIMA_TZ."""
    ahora = datetime.datetime.now(tz=LIMA_TZ)
    inicio_dia = datetime.datetime(
        year=ahora.year, month=ahora.month, day=ahora.day,
        hour=0, minute=0, second=0, tzinfo=LIMA_TZ
    )
    hace = inicio_dia - datetime.timedelta(days=1)
    return hace, ahora


def obtener_terminales_y_controles(
) -> tuple[list[list[float]], list[tuple[str, list[float]]]]:
    """Devuelve coordenadas de terminales y controles."""
    terminales = Terminal.obtener_todos_terminales()
    controles = Control.obtener_todos()

    coords_terminales = [
        [float(t.latitud), float(t.longitud)]
        for t in terminales if t and t.latitud and t.longitud
    ]

    coords_controles = [
        [float(c.latitud), float(c.longitud)]
        for c in controles if c and c.longitud and c.latitud
    ]

    codigos = [str(c.codigo) for c in controles]
    data_controles = list(zip(codigos, coords_controles))

    return coords_terminales, data_controles


def configurar_scripts_personalizados(m: folium.Map) -> None:
    """Agregar scripts para posicionar controles"""
    scripts = {
        "zoom_control": f"""<script nonce="{g.nonce}">
        document.addEventListener("DOMContentLoaded", function() {{
            document.querySelector("div.leaflet-bottom.leaflet-right").insertBefore(
                document.querySelector("div.leaflet-control-zoom"),
                document.querySelector("div.leaflet-control-attribution")
            );
        }});
        </script>""",
        "control_scale": f"""<script nonce="{g.nonce}">
        document.addEventListener("DOMContentLoaded", function() {{
            document.querySelector("div.leaflet-bottom.leaflet-right").insertBefore(
                document.querySelector("div.leaflet-control-scale"),
                document.querySelector("div.leaflet-control-attribution")
            );
        }});
        </script>""",
        "control_locate": f"""<script nonce="{g.nonce}">
        document.addEventListener("DOMContentLoaded", function() {{
            document.querySelector("div.leaflet-top.leaflet-right").insertBefore(
                document.querySelector("div.leaflet-control-locate"),
                document.querySelector("leaflet-control-layers")
            );
        }});
        </script>"""
    }
    for script in scripts.values():
        m.get_root().html.add_child(folium.Element(script))  # type: ignore


@bp.route("/map", methods=["GET", "POST"])
@login_required
def mostrar_mapa() -> ResponseReturnValue:
    # Intervalos de fechas
    hace, ahora = obtener_intervalo_fecha()

    # Vehiculos programados
    vps = VehiculoProgramado.obtener_todos_vp_fecha(hace, ahora)
    # ruta = [v.programa.ruta.codigo for v in vps]
    tiempos_vp: List[TiempoVP] = [
        {
            "Flota": str(vp.vehiculo.flota),
            "Tiempo": vp.tiempo,
            "Ruta": vp.programa.ruta.codigo
        } for vp in vps
    ]
    daf = pd.DataFrame(data=tiempos_vp)
    # daf=daf.set_index("ruta")

    # Mostrar las terminales y controles en el mapa
    coords_terminales, data_controles = obtener_terminales_y_controles()

    # Obtener una DataFrame con las coodenadas de las rutas
    # dgp=dataframe_rutas()
    filename = "rutas_ETMS_tc-34.shp"
    shp = FactoryShapefile().crearArchivo(filename)
    dgp = shp.geo_data_frame
    dgp['ind'] = range(dgp.shape[0])
    dgp['coords'] = dgp.apply(shp.obtenerLongitudLatitud, axis=1)  # type: ignore
    dgp = dgp.to_crs(3857)

    # Crear mapa base
    m = folium.Map(
        control_scale=True,
        zoom_control=True
    ).add_child(  # type: ignore
        folium.LatLngPopup()
    )
    configurar_scripts_personalizados(m)

    # Recorridos

    folium.GeoJson(
        dgp,
        name="Recorrido",
        tooltip=folium.GeoJsonTooltip(fields=["Código", "Dirección"]),
        style_function=lambda x: {  # type: ignore
            "color": COLORES[x['properties']['ind']],
            "weight": 5,
            "fillOpacity": 0.9,
        },  # type: ignore
        show=False,
    ).add_to(m)  # type: ignore
    m.fit_bounds(m.get_bounds())  # type: ignore

    ida = folium.FeatureGroup(name="Recorrido ida").add_to(m)  # type: ignore
    vuelta = folium.FeatureGroup(
        name="Recorrido vuelta",
        show=False
    ).add_to(m)  # type: ignore

    AntPath(
        locations=dgp.coords.iloc[0],
        # reverse="True",
        dash_array=[20, 20],
        delay='4000',
        color='#05be50',
        opacity='0.8',
        pulseColor='#05be50',
    ).add_to(ida)  # type: ignore

    AntPath(
        locations=dgp.coords.iloc[1],
        # reverse="True",
        dash_array=[20, 20],
        delay='4000',
        color='#eb0046',
        opacity='0.8',
        pulseColor='#eb0046',
    ).add_to(vuelta)  # type: ignore

    # Mostrar los terminales
    fg = folium.FeatureGroup(name="Terminales").add_to(m)  # type: ignore
    for p in coords_terminales:
        folium.Marker(
            p,
            popup="Terminal de la Empresa de Transporte.",
            icon=folium.Icon(color="red", icon="ok-sign"),
            draggable=True
        ).add_to(fg)  # type: ignore

    # Mostrar controles
    fg2 = folium.FeatureGroup(name="Controles").add_to(m)  # type: ignore
    for cod, coords in data_controles:
        folium.Marker(
            coords,
            popup=f'Punto de Control:{cod}',
            icon=folium.Icon(color="blue", icon="ok-sign"),
            draggable=True
        ).add_to(fg2)  # type: ignore

    # Plugins
    folium.FitOverlays().add_to(m)  # type: ignore
    folium.LayerControl().add_to(m)  # type: ignore
    folium.plugins.LocateControl(
        auto_start=False,
        strings={
            "title": "Mostrar tu posicion actual",
            "popup": "Tu te encuentras dentro de esta area"
        }
    ).add_to(m)  # type: ignore

    folium.plugins.Geocoder(
        collapsed=True
    ).add_to(m)  # type: ignore

    folium.plugins.Fullscreen(
        position='topright',
        title="Pantalla Completa",
        title_cancel='Salir Pantalla Completa',
    ).add_to(m)  # type: ignore

    # Renderizado
    m.get_root().render()  # type: ignore
    header = m.get_root().header.render()  # type: ignore
    body_html = m.get_root().html.render()  # type: ignore
    script = m.get_root().script.render()  # type: ignore

    # icon_seq=folium.f
    # Element("""<link rel="shortcut icon"
    # href="{{ url_for('static', filename='img/icon_seq.ico') }}"
    # type="image/x-icon">""")
    # return m.get_root().render()
    return render_template(
        "mapa/mapa.html",
        header=header,
        body_html=body_html,
        script=script,
        coords=coords_terminales,
        vps=tiempos_vp,
        ruta=daf.to_html()
    )
