import logging
import os
import pandas as pd

from flask import (
    Blueprint,
    redirect,
    render_template,
    send_from_directory,
    stream_template,
    flash,
    url_for,
    request,
    current_app
)
from flask_login import login_required

from urllib.parse import urlparse
# from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

from qhawariy.controllers.decorators.auth import admin_required
from qhawariy.models.propietario import Propietario
# from qhawariy.models.rol import Rol
# from qhawariy.models.usuario_rol import UsuarioRol
from qhawariy.models.vehiculo import Vehiculo
# from qhawariy.models.asociado import Asociado
from qhawariy.models.propietario_vehiculo import PropietarioVehiculo
from qhawariy.controllers.forms.propietario_form import (
    BuscarPropietarioForm,
    PropietarioForm,
    CambiarPropietarioForm
)
from qhawariy.controllers.forms.upload_file_form import UploadFileForm
from qhawariy.controllers.forms.propietario_vehiculo_form import PropietarioVehiculoForm
from qhawariy.utilities.files import FactoryExcel
from qhawariy.utilities.helpers import hacer_arbol
from qhawariy.utilities.allowed_file import allowed_file

logger = logging.getLogger(__name__)

# Blueprint
bp = Blueprint("propietario", __name__, url_prefix="/propietario")

NOMBRE_ARCHIVO = 'lista_propietarios'


@bp.route("/", methods=["GET", "POST"])
@login_required
@admin_required
def listar_propietarios():
    propietarios = Propietario.obtener_todos_propietarios()

    title = "Lista de propietarios"
    form = BuscarPropietarioForm()
    if form.validate_on_submit():
        busca = form.dni.data
        siguiente_pagina = request.args.get("next", None)
        if not siguiente_pagina or urlparse(siguiente_pagina).netloc != '':
            siguiente_pagina = url_for("propietario.buscar_propietario", busca=busca)
        return redirect(siguiente_pagina)

    return stream_template(
        "/propietario/lista_propietario.html",
        propietarios=propietarios,
        title=title,
        filename=NOMBRE_ARCHIVO+".xlsx",
        form=form
    )


@bp.route("/buscar/<string:busca>", methods=["GET", "POST"])
@login_required
@admin_required
def buscar_propietario(busca):
    busqueda = Propietario.buscar_propietarios_dni(busca)
    form = BuscarPropietarioForm()
    title = "Resultado de buscar propietario con DNI: {b} ".format(b=busca)
    if form.validate_on_submit():
        busca = form.dni.data
        siguiente_pagina = request.args.get("next", None)
        if not siguiente_pagina or urlparse(siguiente_pagina).netloc != '':
            siguiente_pagina = url_for("propietario.buscar_propietario", busca=busca)
        return redirect(siguiente_pagina)
    return render_template(
        "propietario/lista_propietario.html",
        propietarios=busqueda,
        title=title,
        filename=NOMBRE_ARCHIVO+".xlsx",
        form=form
    )


@bp.route("/nuevo", methods=["GET", "POST"])
@login_required
@admin_required
def agregar_propietario():
    form = PropietarioForm()
    error = None
    if form.validate_on_submit():
        nombres = form.nombres.data
        apellidos = form.apellidos.data
        telefono = form.telefono.data
        documento_identificacion = form.documento_identificacion.data
        propietario = Propietario.obtener_propietario_por_dni(documento_identificacion)
        if propietario is not None:
            error = f"""Propietario con Identidad: {documento_identificacion} ya se
                encuentra registrado"""
        else:
            pro = Propietario(nombres, apellidos, telefono, documento_identificacion)
            pro.guardar()
        siguiente_pagina = request.args.get("next", None)
        if not siguiente_pagina or urlparse(siguiente_pagina).netloc != '':
            siguiente_pagina = url_for("propietario.listar_propietarios")
        return redirect(siguiente_pagina)
    return render_template(
        "/propietario/nuevo_propietario.html",
        form=form,
        error=error
    )


@bp.route("/actualiza/<int:propietario_id>/", methods=["GET", "POST"])
@login_required
@admin_required
def actualizar_propietario(propietario_id):

    propietario = Propietario.obtener_propietario_por_id(propietario_id)
    form = CambiarPropietarioForm(obj=propietario)
    if propietario is not None:
        if form.validate_on_submit():
            propietario.nombres = form.nombres.data
            propietario.apellidos = form.apellidos.data
            propietario.telefono = form.telefono.data
            propietario.documento_identificacion = form.documento_identificacion.data
            propietario.guardar()
            siguiente_pagina = request.args.get("next", None)
            if not siguiente_pagina or urlparse(siguiente_pagina).netloc != '':
                siguiente_pagina = url_for("propietario.listar_propietarios")
            return redirect(siguiente_pagina)
    return render_template(
        "propietario/edita_propietario.html",
        form=form,
        propietario=propietario
    )


@bp.route("/elimina/<int:propietario_id>/", methods=["GET", "POST"])
@login_required
@admin_required
def eliminar_propietario(propietario_id):
    propietario = Propietario.obtener_propietario_por_id(propietario_id)
    if propietario is not None:
        propietario.eliminar()
    return redirect(url_for("propietario.listar_propietarios"))


@bp.route("/propietario_vehiculo/", methods=["GET", "POST"])
@login_required
@admin_required
def relacionar_propietario_vehiculo():
    vps = PropietarioVehiculo.obtener_vehiculo_join_propietario()
    propietarios = Propietario.obtener_todos_propietarios()
    vehiculos = Vehiculo.obtener_todos_vehiculos()
    form = PropietarioVehiculoForm()
    form.propietario.choices = [
        (p.id_propietario, p.apellidos+", "+p.nombres) for p in propietarios
    ]
    form.vehiculo.choices = [
        (v.id_vehiculo, str(v.flota)+" - "+v.placa) for v in vehiculos
    ]

    # Conteo de vehiculo activo y no activo por propietario
    dat_activo = PropietarioVehiculo.estadistica_pv_y_vehiculo_propietario(True)
    dat_no_activo = PropietarioVehiculo.estadistica_pv_y_vehiculo_propietario(False)
    data_list_activo = [{i: c} for o, i, c in dat_activo]
    data_list_no_activo = [{i: c} for o, i, c in dat_no_activo]
    pros = [str(p.nombres)+" "+str(p.apellidos) for p in propietarios]
    id = [p.id_propietario for p in propietarios]
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

    if form.validate_on_submit():
        propietario = form.propietario.data
        vehiculo = form.vehiculo.data
        p_v = PropietarioVehiculo(propietario, vehiculo)
        p_v.guardar()
        siguiente_pagina = request.args.get("next", None)
        if not siguiente_pagina or urlparse(siguiente_pagina).netloc != '':
            siguiente_pagina = url_for("propietario.relacionar_propietario_vehiculo")
        return redirect(siguiente_pagina)
    return render_template(
        "propietario/propietario_vehiculo.html",
        form=form,
        propietarios=propietarios,
        vehiculos=vehiculos,
        vps=vps,
        data5=da,
        data6=dna,
        pros=pros
    )


@bp.route("/propietario_vehiculo/elimina/<int:pv_id>/", methods=["GET", "POST"])
@login_required
@admin_required
def eliminar_pv(pv_id):
    pv = PropietarioVehiculo.obtener_propietario_vehiculo_por_id(pv_id)
    if pv is not None:
        pv.eliminar()
    return redirect(url_for("propietario.relacionar_propietario_vehiculo"))


@bp.route("/cargar_archivo", methods=["GET", "POST"])
@login_required
@admin_required
def cargar_archivo_propietarios():

    form = UploadFileForm()
    path = current_app.config['UPLOAD_FOLDER']
    lista_archivos = hacer_arbol(path=path)
    if form.validate_on_submit():
        if 'file' not in request.files:
            flash('No existe el archivo')
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            flash('Archivo no seleccionado')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                filename
            ))
            return redirect(url_for("propietario.cargar_archivo_propietarios"))
    return render_template(
        'propietario/carga_propietario.html',
        form=form,
        la=lista_archivos
    )


@bp.route("/descargar/<name>", methods=["GET", "POST"])
@login_required
@admin_required
def descargar_archivo(name):
    propietarios = Propietario.obtener_todos_propietarios()
    excel = FactoryExcel()
    excel.crearArchivo(
        filename=NOMBRE_ARCHIVO,
        dataframe=propietarios,
        tipo='lista',
        sheetnames=['propietarios'],
        recorrido=None,
        date=None
    ).guardar()
    return send_from_directory(current_app.config["DOWNLOAD_FOLDER"], name)


@bp.route("/agregar_masivo/<name>", methods=["GET", "POST"])
@login_required
@admin_required
def agregar_masivo(name):
    extension = os.path.splitext(name)[1][1:]
    if extension == 'xlsx':
        archivo = pd.read_excel(
            current_app.config["UPLOAD_FOLDER"]+"\\"+name,
            index_col=0
        )
        # vehiculo=Vehiculo()
        if (
            'nombres' in archivo.columns
            and 'apellidos' in archivo.columns
            and 'telefono' in archivo.columns
            and 'documento_identificacion' in archivo.columns
        ):
            for i in range(0, len(archivo)):
                dni = Propietario.obtener_propietario_por_dni(
                    archivo.iloc[i]['documento_identificacion']
                )
                no = 0
                ap = 0
                te = 0
                di = 0
                if dni is None:
                    for a in archivo.columns:
                        r = archivo.iloc[i]
                        if a == 'nombres':
                            no = r[a]
                        elif a == 'apellidos':
                            ap = r[a]
                        elif a == 'telefono':
                            te = r[a]
                        elif a == 'documento_identificacion':
                            di = r[a]

                    if no != 0 and ap != 0 and te != 0 and di != 0:
                        pro = Propietario(no, ap, te, di)
                        pro.guardar()
        else:
            flash(
                f"El archivo seleccionado {name} no tiene el formato correcto",
                category='error'
            )

    return redirect(url_for("propietario.listar_propietarios"))


@bp.route("/eliminar_archivo_subido/<name>", methods=["GET", "POST"])
@login_required
@admin_required
def eliminar_archivo_subido(name):
    # extension = os.path.splitext(name)[1][1:]
    filename = name
    try:
        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for("propietario.cargar_archivo_propietarios"))
    except Exception as e:
        flash(f"Error al eliminar el archivo {e}", "error")

    return redirect(url_for("propietario.cargar_archivo_propietarios"))
