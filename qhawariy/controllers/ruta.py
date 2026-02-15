
import datetime
import logging
from typing import cast
# import pandas as pd
# import numpy as np

from flask import (
    Blueprint,
    flash,
    render_template,
    redirect,
    url_for,
    abort
)
from flask_login import login_required  # type: ignore
# from werkzeug.urls import url_parse
# from urllib.parse import urlparse

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
from qhawariy.utilities.redirect import redireccion_seguro

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

    if form.validate_on_submit():  # type: ignore
        codigo = cast(str, form.codigo.data)
        inicio_vigencia = cast(datetime.datetime, form.inicio_vigencia.data)
        fin_vigencia = cast(datetime.datetime, form.fin_vigencia.data)
        documento = cast(str, form.documento.data)
        terminal1 = form.terminal1.data
        terminal2 = form.terminal2.data
        siguiente_ruta = form.proxima_ruta.data

        ruta_terminal = RutaTerminal.obtener_por_terminales(
            id_terminal1=terminal1,
            id_terminal2=terminal2
        )
        if ruta_terminal:
            # Los terminales no pueden ser los mismos
            flash(
                f"Existe una ruta con los terminales:{terminal1} y"
                f"destino:{terminal2}",
                'error'
            )
        elif terminal1 == terminal2:
            flash(
                f"Los terminales deben ser distintos. Ingresaste el mismo terminal "
                f"para ambos: {Terminal.obtener_terminal_por_id(terminal1)}",
                "warning"
            )
        else:
            try:
                # Agregar primero ruta
                ruta = Ruta(codigo, inicio_vigencia, fin_vigencia, documento)
                ruta.guardar()
                # Agregar segundo ruta_terminal (deben de existir los dos terminales)
                rt = RutaTerminal(ruta.id_ruta, terminal1, terminal2)
                rt.guardar()

                # Agregar proxima ruta
                proxima = ProximaRuta(ruta.id_ruta, siguiente_ruta)
                proxima.guardar()

                redireccion_seguro("ruta.lista_ruta")
            except Exception as e:
                flash(f"Ocurrió un error al guardar la ruta: {e}", "error")

    return render_template("/ruta/agrega_ruta.html", form_ruta=form)


@bp.route("/nuevo_terminal/", methods=["GET", "POST"])
@login_required
@admin_required
def agregar_terminal():
    form = AgregarTerminalForm()

    form.departamento.choices = [
        (d.id_departamento, str(d.nombre))
        for d in Departamento.obtener_todos_departamentos()
    ]
    form.provincia.choices = [
        (p.id_provincia, str(p.nombre))
        for p in Provincia.obtener_todos_provincias()
    ]
    form.distrito.choices = [
        (d.id_distrito, str(d.nombre))
        for d in Distrito.obtener_todos_distritos()
    ]
    terminales = Terminal.obtener_todos_terminales()

    if form.validate_on_submit():  # type: ignore
        try:
            terminal = Terminal(
                direccion=cast(str, form.direccion.data),
                latitud=cast(float, form.latitud.data),
                longitud=cast(float, form.longitud.data),
                id_departamento=cast(int, form.departamento.data),
                id_provincia=cast(int, form.provincia.data),
                id_distrito=cast(int, form.distrito.data)
            )
            terminal.guardar()
            redireccion_seguro("ruta.agregar_ruta")
        except Exception as e:
            flash(f"Ocurrió un error al guardar el terminal: {e}", "error")

    return render_template(
        "/ruta/agrega_terminal.html",
        form=form,
        terminales=terminales
    )


@bp.route("/eliminar_terminal/<int:terminal_id>/", methods=["GET", "POST"])
@login_required
@admin_required
def eliminar_terminal(terminal_id: int):
    terminal = Terminal.obtener_terminal_por_id(terminal_id)
    if not terminal:
        logger.info(f"La ruta {terminal_id} no existe")
        abort(404)
        redireccion_seguro("ruta.agregar_terminal")
    terminal.eliminar()
    logger.info(f"El terminal {terminal_id} ha sido eliminado")
    return redirect(url_for("ruta.agregar_terminal"))


@bp.route("/ruta/<int:ruta_id>/", methods=["GET", "POST"])
@login_required
@admin_required
def actualizar_ruta(ruta_id: int):
    ruta = Ruta.obtener_ruta_por_id(ruta_id)
    if not ruta:
        logger.info(f"La ruta {ruta_id} no existe")
        abort(404)

    ruta_actual = ProximaRuta.obtener_por_ruta_actual(ruta_id)
    ruta_terminal = RutaTerminal.obtener_rt_por_ruta(ruta.id_ruta)
    if not ruta_terminal:
        flash(f"La ruta {ruta}, no tiene asignado a ninguna terminal")
        redireccion_seguro("ruta_lista_ruta")
        abort(404)

    terminales = Terminal.obtener_todos_terminales()
    rutas = Ruta.obtener_todos_rutas()
    form = EditarRutaForm(obj=ruta)
    form.terminal1.choices = [
        (t.id_terminal, str(t.direccion)) for t in terminales
    ]
    form.terminal2.choices = [
        (t.id_terminal, str(t.direccion)) for t in terminales
    ]
    lista_proxima = [(0, 'Ninguno')] + [(r.id_ruta, str(r.codigo)) for r in rutas]
    form.proxima_ruta.choices = lista_proxima  # type: ignore

    if form.validate_on_submit():  # type: ignore
        terminal1 = cast(int, form.terminal1.data)
        terminal2 = cast(int, form.terminal2.data)
        siguiente_ruta = cast(int, form.proxima_ruta.data)
        # Los terminales no pueden ser los mismos
        if terminal1 != terminal2:
            ruta.codigo = cast(str, form.codigo.data)
            ruta.inicio_vigencia = cast(datetime.datetime, form.inicio_vigencia.data)
            ruta.fin_vigencia = cast(datetime.datetime, form.fin_vigencia.data)
            ruta.documento = cast(str, form.documento.data)
            ruta.guardar()

            ruta_terminal.id_terminal = terminal1
            ruta_terminal.id_terminal_2 = terminal2
            ruta_terminal.guardar()

            if ruta_actual is None:
                ruta_actual = ProximaRuta(ruta_id, None)

            ruta_actual.ruta_proxima = None if siguiente_ruta == 0 else siguiente_ruta
            ruta_actual.guardar()

            logger.info(f"La ruta {ruta_id} ha sido actualizado")
            flash(
                f"La ruta {ruta.codigo} ha sido actualizado",
                "info"
            )
            redireccion_seguro("ruta.lista_ruta")
        else:
            flash(
                f"Los terminales deben ser distintos. Ingresaste el mismo: "
                f"Terminal 1: {Terminal.obtener_terminal_por_id(terminal1)}, "
                f"Terminal 2: {Terminal.obtener_terminal_por_id(terminal2)}",
                category="warning"
            )
    else:
        form.terminal1.data = str(ruta_terminal.id_terminal)
        form.terminal2.data = str(ruta_terminal.id_terminal_2)
        if ruta_actual and ruta_actual.proxima:
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
def eliminar_ruta(ruta_id: int):
    ruta = Ruta.obtener_ruta_por_id(ruta_id)
    if ruta is None:
        logger.info(f"La ruta {ruta_id} no existe")
        abort(404)
    else:
        ruta.eliminar()
        logger.info(f"El vehiculo {ruta_id} ha sido eliminado")
    return redirect(url_for("ruta.lista_ruta"))
