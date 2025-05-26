
import logging
# import pandas as pd
# import numpy as np

from flask import (
    Blueprint,
    flash,
    request,
    render_template,
    redirect,
    url_for,
    abort
)
from flask_login import login_required
# from werkzeug.urls import url_parse
from urllib.parse import urlparse

from qhawariy.models.departamento import Departamento
from qhawariy.models.distrito import Distrito
from qhawariy.models.provincia import Provincia
from qhawariy.models.proxima_ruta import ProximaRuta
from qhawariy.models.ruta import Ruta
from qhawariy.forms.ruta_form import (
    AgregarRutaForm,
    AgregarTerminalForm,
    EditarRutaForm
)
from qhawariy.models.ruta_terminal import RutaTerminal
from qhawariy.models.terminal import Terminal
from qhawariy.utilities.decorators import admin_required

logger = logging.getLogger(__name__)

# Blueprint
bp = Blueprint("ruta", __name__, url_prefix="/ruta")


@bp.route("/", methods=["GET", "POST"])
@login_required
@admin_required
def lista_ruta():
    rutas = Ruta.obtener_todos_rutas()
    return render_template("ruta/lista_ruta.html", rutas=rutas)


@bp.route("/nuevo_ruta/", methods=["GET", "POST"])
@login_required
@admin_required
def agregar_ruta():

    terminales = Terminal.obtener_todos_terminales()
    rutas = Ruta.obtener_todos_rutas()

    form = AgregarRutaForm()
    form.terminal1.choices = [
        (t.id_terminal, str(t.direccion)) for t in terminales
    ]
    form.terminal2.choices = [
        (t.id_terminal, str(t.direccion)) for t in terminales
    ]
    form.proxima_ruta.choices = [
        (r.id_ruta, str(r.codigo)) for r in rutas
    ]

    if form.validate_on_submit():
        codigo = form.codigo.data
        inicio_vigencia = form.inicio_vigencia.data
        fin_vigencia = form.fin_vigencia.data
        documento = form.documento.data
        terminal1 = form.terminal1.data
        terminal2 = form.terminal2.data
        siguiente_ruta = form.proxima_ruta.data

        ruta_terminal = RutaTerminal.obtener_por_terminales(
            id_terminal1=terminal1,
            id_terminal2=terminal2
        )
        if ruta_terminal is not None:
            flash(
                message="""Existe una ruta con los terminales:{t1} y
                destino:{t2}""".format(t1=terminal1, t2=terminal2),
                category='error'
            )
        else:
            # Los terminales no pueden ser los mismos
            if terminal1 != terminal2:
                # Agregar primero ruta
                ruta = Ruta(codigo, inicio_vigencia, fin_vigencia, documento)
                ruta.guardar()
                # Agregar segundo ruta_terminal (deben de existir los dos terminales)
                rt = RutaTerminal(ruta.id_ruta, terminal1, terminal2)
                rt.guardar()

                # Agregar proxima ruta
                proxima = ProximaRuta(ruta.id_ruta, siguiente_ruta)
                proxima.guardar()

                siguiente_pagina = request.args.get("next", None)
                if not siguiente_pagina or urlparse(siguiente_pagina).netloc != '':
                    siguiente_pagina = url_for("ruta.lista_ruta")
                return redirect(siguiente_pagina)
            else:
                flash(
                    message="""Los terminales de una ruta deben encontrarse en
                    diferentes ubicaciones. Los terminales ingresados son iguales
                    'Terminal 1:{t1}' y 'Terminal 2:{t2}'"""
                    .format(
                        t1=Terminal.obtener_terminal_por_id(terminal1).direccion,
                        t2=Terminal.obtener_terminal_por_id(terminal2).direccion
                    ),
                    category='Advertencia'
                )

    return render_template("/ruta/agrega_ruta.html", form_ruta=form)


@bp.route("/nuevo_terminal/", methods=["GET", "POST"])
@login_required
@admin_required
def agregar_terminal():

    terminales = Terminal.obtener_todos_terminales()

    departamentos = Departamento.obtener_todos_departamentos()
    provincias = Provincia.obtener_todos_provincias()
    distritos = Distrito.obtener_todos_distritos()

    form = AgregarTerminalForm()
    form.departamento.choices = [
        (d.id_departamento, str(d.nombre))for d in departamentos
    ]
    form.provincia.choices = [
        (p.id_provincia, str(p.nombre))for p in provincias
    ]
    form.distrito.choices = [
        (d.id_distrito, str(d.nombre))for d in distritos
    ]

    if form.validate_on_submit():
        direccion = form.direccion.data
        latitud = form.latitud.data
        longitud = form.longitud.data
        departamento = form.departamento.data
        provincia = form.provincia.data
        distrito = form.distrito.data

        terminal = Terminal(
            direccion=direccion,
            latitud=latitud,
            longitud=longitud,
            id_departamento=departamento,
            id_provincia=provincia,
            id_distrito=distrito
        )
        terminal.guardar()

        siguiente_pagina = request.args.get("next", None)
        if not siguiente_pagina or urlparse(siguiente_pagina).netloc != '':
            siguiente_pagina = url_for("ruta.agregar_ruta")
        return redirect(siguiente_pagina)

    return render_template(
        "/ruta/agrega_terminal.html",
        form=form,
        terminales=terminales
    )


@bp.route("/eliminar_terminal/<int:terminal_id>/", methods=["GET", "POST"])
@login_required
@admin_required
def eliminar_terminal(terminal_id):
    terminal = Terminal.obtener_terminal_por_id(terminal_id)
    if terminal is None:
        logger.info(f"La ruta {terminal_id} no existe")
        abort(404)
    else:
        terminal.eliminar()
        logger.info(f"El terminal {terminal_id} ha sido eliminado")
    return redirect(url_for("ruta.agregar_terminal"))


@bp.route("/ruta/<int:ruta_id>/", methods=["GET", "POST"])
@login_required
@admin_required
def actualizar_ruta(ruta_id):

    ruta = Ruta.obtener_ruta_por_id(ruta_id)
    ruta_actual = ProximaRuta.obtener_por_ruta_actual(ruta_id)
    ruta_terminal = RutaTerminal.obtener_rt_por_ruta(ruta.id_ruta)

    if ruta is None:
        logger.info(f"La ruta {ruta_id} no existe")
        abort(404)
    else:
        terminales = Terminal.obtener_todos_terminales()
        rutas = Ruta.obtener_todos_rutas()
        form = EditarRutaForm(obj=ruta)
        form.terminal1.choices = [
            (t.id_terminal, str(t.direccion)) for t in terminales
        ]
        form.terminal2.choices = [
            (t.id_terminal, str(t.direccion)) for t in terminales
        ]
        lista_proxima = [(0, 'Ninguno')]
        opciones_rutas = [(r.id_ruta, str(r.codigo)) for r in rutas]
        form.proxima_ruta.choices = lista_proxima+opciones_rutas

        if form.validate_on_submit():
            terminal1 = form.terminal1.data
            terminal2 = form.terminal2.data
            siguiente_ruta = form.proxima_ruta.data
            # Los terminales no pueden ser los mismos
            if terminal1 != terminal2:
                ruta.codigo = form.codigo.data
                ruta.inicio_vigencia = form.inicio_vigencia.data
                ruta.fin_vigencia = form.fin_vigencia.data
                ruta.documento = form.documento.data
                ruta.guardar()

                ruta_terminal.id_terminal = terminal1
                ruta_terminal.id_terminal_2 = terminal2
                ruta_terminal.guardar()

                if ruta_actual is None:
                    nuevo_proxima = ProximaRuta(ruta_id, None)
                    ruta_actual = nuevo_proxima

                if siguiente_ruta == 0:
                    siguiente_ruta = None

                ruta_actual.ruta_proxima = siguiente_ruta
                ruta_actual.guardar()

                logger.info(f"La ruta {ruta_id} ha sido actualizado")
                flash(
                    "La ruta {ruta_id} ha sido actualizado".format(ruta_id=ruta.codigo),
                    category="Info"
                )
                siguiente_pagina = request.args.get("next", None)
                if not siguiente_pagina or urlparse(siguiente_pagina).netloc != '':
                    siguiente_pagina = url_for("ruta.lista_ruta")
                return redirect(siguiente_pagina)
            else:
                flash(
                    message="""Los terminales de una ruta deben encontrarse en
                    diferentes ubicaciones. Los terminales ingresados son iguales
                    'Terminal 1:{t1}' y 'Terminal 2:{t2}'""".format(
                        t1=Terminal.obtener_terminal_por_id(terminal1).direccion,
                        t2=Terminal.obtener_terminal_por_id(terminal2).direccion
                    ),
                    category='Advertencia'
                )
        else:
            form.terminal1.data = str(ruta_terminal.terminal.direccion)
            form.terminal2.data = str(ruta_terminal.terminal2.direccion)
            form.proxima_ruta.data = str(ruta_actual.proxima.codigo)

    # return redirect("ruta/ruta_list.html")
    return render_template(
        "ruta/edita_ruta.html",
        form=form,
        ruta=ruta,
        proxima=ruta_actual
    )


@bp.route("/ruta/delete/<int:ruta_id>/", methods=["POST"])
@login_required
@admin_required
def eliminar_ruta(ruta_id):
    ruta = Ruta.obtener_ruta_por_id(ruta_id)
    if ruta is None:
        logger.info(f"La ruta {ruta_id} no existe")
        abort(404)
    else:
        ruta.eliminar()
        logger.info(f"El vehiculo {ruta_id} ha sido eliminado")
    return redirect(url_for("ruta.lista_ruta"))
