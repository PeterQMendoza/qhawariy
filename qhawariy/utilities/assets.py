from flask import current_app as app
from flask_assets import (Bundle, Environment)


def compile_stylesheet_bundles(assets: Environment) -> Environment:
    """
    Crea paquetes CSS minimizados a partir de estilos
        :param Environment assets: entorno Flask para activos estaticos.
        :return Environment
    """
    # Paquetes de hojas de estilo principal
    principal = Bundle(
        "source/styles/style.css",
        "source/styles/map.css",
        "source/styles/programa.css",
        filters="cssmin",
        output="dist/css/style_qhawariy.css",
        extra={"rel": "stylesheet/css"},
    )
    timeline_fleet = Bundle(
        "source/styles/timeline_fleet.css",
        filters="cssmin",
        output="dist/css/timeline_fleet_qhawariy.css",
        extra={"rel": "stylesheet/css"},
    )

    assets.register('estilos_principales', principal)  # type: ignore
    assets.register('estilos_timeline_fleet', timeline_fleet)  # type: ignore

    if app.config['APP_ENV_DEVELOPMENT'] == 'development':
        principal.build()  # type: ignore
        timeline_fleet.build()  # type: ignore
    return assets


def compile_js_assets(assets: Environment) -> Environment:
    """
    Crea un paquete Javascript minimizado a partir de archivos javascript sin formato
        :param Environment assets: Entorno Flask para activos estaticos.
        :return Environment
    """
    principal = Bundle(
        "source/js/app.js",
        filters='jsmin',
        output="dist/js/app_qhawariy.min.js",
    )

    time = Bundle(
        "source/js/time.js",
        filters='jsmin',
        output="dist/js/time_qhawariy.min.js",
    )

    estadistica = Bundle(
        "source/js/estadistica.js",
        filters='jsmin',
        output="dist/js/estadistica_qhawariy.min.js",
    )

    loading = Bundle(
        "source/js/loading.js",
        filters='jsmin',
        output="dist/js/loading_qhawariy.min.js",
    )

    programacion = Bundle(
        "source/js/programacion.js",
        filters='jsmin',
        output="dist/js/programacion_qhawariy.min.js",
    )

    calendar = Bundle(
        "source/js/calendar.js",
        filters='jsmin',
        output="dist/js/calendar_qhawariy.min.js",
    )

    chartjs = Bundle(
        "source/js/chart/chart.js",
        filters='jsmin',
        output="dist/js/chart.min.js",
    )

    timeline_fleet = Bundle(
        "source/js/timeline_fleet.js",
        filters='jsmin',
        output="dist/js/timeline_fleet_qhawariy.min.js",
    )

    assets.register('principal_js', principal)  # type: ignore
    assets.register('calendar_js', calendar)  # type: ignore
    assets.register('programacion_js', programacion)  # type: ignore
    assets.register('loading_js', loading)  # type: ignore
    assets.register('estadistica_js', estadistica)  # type: ignore
    assets.register('time_js', time)  # type: ignore
    assets.register('chart_js', chartjs)  # type: ignore
    assets.register('timeline_fleet_js', timeline_fleet)  # type: ignore

    # Cambiar en modo produccion
    if app.config['APP_ENV_DEVELOPMENT'] == "development":
        principal.build()  # type: ignore
        calendar.build()  # type: ignore
        programacion.build()  # type: ignore
        loading.build()  # type: ignore
        estadistica.build()  # type: ignore
        time.build()  # type: ignore
        chartjs.build()  # type: ignore
        timeline_fleet.build()  # type: ignore
    return assets
