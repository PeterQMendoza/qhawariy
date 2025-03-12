import logging
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
    render_template,
    current_app
)
from flask_login import (
    login_required,
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


@bp.route("/estadistica", methods=["GET", "POST"])
@login_required
def mostrar_estadisticas():
    # Mostrar las estadisticas com punto de referencia al nombre codigo de las rutas
    # Para visualizar panel
    if current_user.is_authenticated:
        id_user = current_user.id_usuario
        ur = UsuarioRol.obtener_por_id_usuario(id_user)
        rol = ur.rol
    else:
        rol = None

    if not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()

    # Datos para grafico de linea
    # obtener todas las fechas registradas
    fechas = Fecha.obtener_todas_fechas()
    lista_todas_las_fechas = [f.fecha for f in fechas]
    dat1 = VehiculoProgramado.estadistica_vp_fecha_programa()
    data_list1 = [{'x': v.strftime('%d-%m-%Y'), 'y': r} for c, v, r in dat1]
    # df=[v for c,v,r in dat1]
    df = lista_todas_las_fechas

    rutas = RutaTerminal.obtener_todas_rt()
    lista_rutas = []
    for lr in rutas:
        lista_rutas.append(
            VehiculoProgramado.estadistica_vp_fecha_programa_y_ruta(lr.ruta.id_ruta)
        )

    # Para obtener registro de 0 para cada dia si no tiene programaciones de vehiculos
    # Copia profunda sin referencia
    empty = copy.deepcopy(data_list1)
    for em in empty:
        for k, a in em.items():
            em.update(y=0)

    # crear copias vacias para cada ruta
    lista_copia_vacias = []
    for i in range(len(rutas)):
        aux = copy.deepcopy(empty)
        lista_copia_vacias.append(aux)

    for i in range(len(rutas)):
        for o, f, c in lista_rutas[i]:
            if f in df:
                for em in lista_copia_vacias[i]:
                    if em['x'] == f.strftime('%d-%m-%Y'):
                        em.update({'x': f.strftime('%d-%m-%Y'), 'y': c})

    dat2 = VehiculoProgramado.estadistica_vp_flota_programa()
    vehiculos = Vehiculo.obtener_todos_vehiculos_activos()
    t_empty = [{'x': 'Flota '+str(v.flota), 'y': 0} for v in vehiculos]
    data_list2 = [{'x': 'Flota '+str(v), 'y': r} for c, v, r in dat2]
    # Ordenar dicccionario por valor
    d_test = copy.deepcopy(data_list2)
    for v in d_test:
        for e in t_empty:
            if v['x'] == e['x']:
                e['y'] = v['y']
    n = len(t_empty)
    for i in range(n):
        swapped = False
        for j in range(0, n-i-1):
            if t_empty[j]['y'] < t_empty[j+1]['y']:
                t_empty[j], t_empty[j+1] = t_empty[j+1], t_empty[j]
                swapped = True
        if not swapped:
            break

    #
    veh = Vehiculo.estadistica_todos_vehiculos_activos()
    dat3 = VehiculoProgramado.estadistica_vp_fecha_programado_no_programado()
    data_list3 = None
    if dat3 is not None:
        data_list3 = []
    else:
        total = veh[0][1]
        dt = dat3[0][1].strftime('%d-%m-%Y')
        pro = dat3[0][2]
        data_list3 = [[pro, (total-pro)], dt]

    # GRAFICO DE LA DONA
    # Datos de cantidad de vehiculos por ruta
    dat4 = VehiculoProgramado.estadistica_cantidad_vehiculos_por_ruta()
    data_list4 = {str(s): c for o, s, c in dat4}

    # GRAFICO DE BARRA PROPIETARIO
    # Conteo de vehiculo activo y no activo por propietario
    props = Propietario.obtener_todos_propietarios()
    dat_activo = PropietarioVehiculo.estadistica_pv_y_vehiculo_propietario(True)
    dat_no_activo = PropietarioVehiculo.estadistica_pv_y_vehiculo_propietario(False)
    data_list_activo = [{i: c} for o, i, c in dat_activo]
    data_list_no_activo = [{i: c} for o, i, c in dat_no_activo]
    propietarios = [str(p.nombres)+" "+str(p.apellidos) for p in props]
    id = [p.id_propietario for p in props]
    da = [0]*len(id)
    dna = [0]*len(id)
    for i in data_list_activo:
        for k, v in i.items():
            aux = id.index(k)
            if k in id:
                da[aux] = v
            else:
                da[aux] = 0
    for i in data_list_no_activo:
        for k, v in i.items():
            aux = id.index(k)
            if k in id:
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
        } for v, t, c in vp if t is not None
    ]

    # Estadistica para viajes
    # Cantidad de viajes hechos por vehiculos
    viajes_por_vehiculos = Viaje.estadistica_viajes_por_vehiculo()
    vpv = [
        {'x': "Flota "+str(f), 'y': conteo} for vo, f, conteo in viajes_por_vehiculos
    ]
    vpvs = [
        # Inicia con cada conteo de vehiculo 0
        {'x': 'Flota '+str(v.flota), 'y': 0} for v in vehiculos
    ]
    # Ordenar dicccionario por valor
    d_test = copy.deepcopy(vpv)
    for v in d_test:
        for e in vpvs:
            if v['x'] == e['x']:
                e['y'] = v['y']
    n = len(vpvs)
    for i in range(n):
        swapped = False
        for j in range(0, n-i-1):
            if vpvs[j]['y'] < vpvs[j+1]['y']:
                vpvs[j], vpvs[j+1] = vpvs[j+1], vpvs[j]
                swapped = True
        if not swapped:
            break

    # Cantidad de viajes por fecha y ruta
    total_viajes_por_fecha = Viaje.estadistica_viajes_por_fecha()
    lista_tvf = [
        {'x': f.strftime('%d-%m-%Y'), 'y': c} for v, f, c in total_viajes_por_fecha
    ]
    lista_fechas = lista_todas_las_fechas
    lista_viajes_fecha_ruta = []
    for r in rutas:
        lista_viajes_fecha_ruta.append(
            Viaje.estadistica_viajes_por_fecha_ruta(r.ruta.id_ruta)
        )

    # Inicializamos una dict con valores a 0 de todos los viajes realizados por fecha
    # Copia profunda sin referencia
    lvfr = copy.deepcopy(lista_tvf)
    for em in lvfr:
        for k, a in em.items():
            em.update(y=0)

    # Creamos copias vacias de viajes para cada ruta
    lvfrs = []
    for i in range(len(rutas)):
        aux = copy.deepcopy(lvfr)
        lvfrs.append(aux)

    for i in range(len(rutas)):
        for o, f, c in lista_viajes_fecha_ruta[i]:
            if f in lista_fechas:
                for em in lvfrs[i]:
                    if em['x'] == f.strftime('%d-%m-%Y'):
                        em.update({'x': f.strftime('%d-%m-%Y'), 'y': c})

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


@bp.route("/map", methods=["GET", "POST"])
@login_required
def mostrar_mapa():
    # obtener las coordenadas gps de las terminales, de las rutas programadas
    # y mostrarlas en el mapa
    ahora = datetime.datetime.now(tz=LIMA_TZ)
    date = datetime.datetime(
        year=ahora.year,
        month=ahora.month,
        day=ahora.day,
        hour=0,
        minute=0,
        second=0
    )
    hace = date-datetime.timedelta(days=1)

    vps = VehiculoProgramado.obtener_todos_vp_fecha(hace, ahora)
    # ruta = [v.programa.ruta.codigo for v in vps]
    tiempos_vp = [
        {
            "Flota": str(vp.vehiculo.flota),
            "Tiempo": vp.tiempo,
            "Ruta": vp.programa.ruta.codigo
        } for vp in vps
    ]
    daf = pd.DataFrame(data=tiempos_vp)
    # daf=daf.set_index("ruta")

    # Mostrar las terminales y controles en el mapa
    terminales = Terminal.obtener_todos_terminales()
    controles = Control.obtener_todos()
    # data_terminales = {
    #     'Direccion': [d.direccion for d in terminales if d != '' and d is not None]
    # }
    latitud_terminales = [
        str(t.latitud) for t in terminales if t != '' and t is not None
    ]
    longitud_terminales = [
        str(t.longitud) for t in terminales if t != '' and t is not None]
    latitud_controles = [
        str(c.latitud) for c in controles if c != '' and c is not None
    ]
    longitud_controles = [
        str(c.longitud) for c in controles if c != '' and c is not None
    ]
    # obtener lon y lat de una cadena de texto
    coords_terminales = [list(z) for z in zip(latitud_terminales, longitud_terminales)]
    coords_controles = [list(z) for z in zip(latitud_controles, longitud_controles)]
    codigos = [str(c.codigo) for c in controles]
    data_controles = [list(c) for c in zip(codigos, coords_controles)]

    # Obtener una DataFrame con las coodenadas de las rutas
    # dgp=dataframe_rutas()
    filename = "rutas_ETMS_tc-34.shp"
    file = FactoryShapefile()
    shp = file.crearArchivo(filename)
    dgp = shp.geo_data_frame

    dgp['ind'] = [i for i in range(dgp.shape[0])]
    dgp['coords'] = dgp.apply(shp.obtenerLongitudLatitud, axis=1)
    dgp = dgp.to_crs(3857)

    LatLng = folium.LatLngPopup()

    m = folium.Map(
        control_scale=True,
        zoom_control=True
    ).add_child(
        LatLng
    )

    # Establecer la posicion de zoom control lado inferior derecho
    map_script_zoom_control = """<script>
        document.addEventListener("DOMContentLoaded", function() {\
        document.querySelector("div.leaflet-bottom.leaflet-right").insertBefore(\
            document.querySelector("div.leaflet-control-zoom"),
            document.querySelector("div.leaflet-control-attribution")\
        );\
    });</script>"""
    m.get_root().html.add_child(folium.Element(map_script_zoom_control))

    # Establecer la posicion de control de escala al lado inferior derecha
    map_script_control_scale = """<script>\
        document.addEventListener("DOMContentLoaded", function() {\
        document.querySelector("div.leaflet-bottom.leaflet-right").insertBefore(\
            document.querySelector("div.leaflet-control-scale"),
            document.querySelector("div.leaflet-control-attribution")\
        );\
        });</script>"""
    m.get_root().html.add_child(folium.Element(map_script_control_scale))

    # Establecer la posicion de ubicacion al lado superior derecha
    map_script_control_locate = """<script>
        document.addEventListener("DOMContentLoaded", function() {\
            document.querySelector("div.leaflet-top.leaflet-right").insertBefore(\
                document.querySelector("div.leaflet-control-locate"),
                document.querySelector("leaflet-control-layers")\
            );\
        });</script>"""
    m.get_root().html.add_child(folium.Element(map_script_control_locate))

    colors = COLORES

    folium.GeoJson(
        dgp,
        name="Recorrido",
        tooltip=folium.GeoJsonTooltip(fields=["Código", "Dirección"]),
        style_function=lambda x: {
            "color": colors[x['properties']['ind']],
            "weight": 5,
            "fillOpacity": 0.9,
        },
        show=False,
    ).add_to(m)
    m.fit_bounds(m.get_bounds())

    ida = folium.FeatureGroup(name="Recorrido ida").add_to(m)
    vuelta = folium.FeatureGroup(name="Recorrido vuelta", show=False).add_to(m)

    AntPath(
        locations=dgp.coords.iloc[0],
        # reverse="True",
        dash_array=[20, 20],
        delay='4000',
        color='#05be50',
        opacity='0.8',
        pulseColor='#05be50',
    ).add_to(ida)

    AntPath(
        locations=dgp.coords.iloc[1],
        # reverse="True",
        dash_array=[20, 20],
        delay='4000',
        color='#eb0046',
        opacity='0.8',
        pulseColor='#eb0046',
    ).add_to(vuelta)
    # mostrar lista de puntos gps de los terminales registrados
    fg = folium.FeatureGroup(name="Terminales").add_to(m)
    for p in coords_terminales:
        folium.Marker(
            p,
            popup="Terminal de la Empresa de Transporte.",
            icon=folium.Icon(color="red", icon="ok-sign"),
            draggable=True
        ).add_to(fg)
    # mostrar lista de puntos gps de los controles registrados
    fg2 = folium.FeatureGroup(name="Controles").add_to(m)
    for c, co in data_controles:
        folium.Marker(
            co,
            popup=f'Punto de Control:{c}',
            icon=folium.Icon(color="blue", icon="ok-sign"),
            draggable=True
        ).add_to(fg2)

    folium.FitOverlays().add_to(m)
    folium.LayerControl().add_to(m)

    folium.plugins.LocateControl(
        auto_start=False,
        strings={
            "title": "Mostrar tu posicion actual",
            "popup": "Tu te encuentras dentro de esta area"
        }
    ).add_to(m)

    folium.plugins.Geocoder(
        collapsed=True
    ).add_to(m)

    folium.plugins.Fullscreen(
        position='topright',
        title="Pantalla Completa",
        title_cancel='Salir Pantalla Completa',
    ).add_to(m)

    m.get_root().render()
    header = m.get_root().header.render()
    body_html = m.get_root().html.render()
    script = m.get_root().script.render()

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


# def obtenerLonLatDeString(lista: list):
#     lat = []
#     lon = []
#     for g in lista:
#         if g != '' and g is not None:
#             try:
#                 x, y = g.split(',')
#                 lon.append(float(y))
#                 lat.append(float(x))
#             except Exception as e:
#                 flash(
#                   f"""Los datos registrados en la terminal no presenta el fomato de:
#                   'Latitud,Longitud' \nDetalles de error:{e}""",
#                   "Error"
#                 )
#     return [list(z) for z in zip(lat, lon)]
