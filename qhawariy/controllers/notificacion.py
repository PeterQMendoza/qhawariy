import logging

from flask import (
    Blueprint,
    redirect,
    render_template,
    url_for
)

from flask_login import (
    current_user,
    login_required  # type: ignore
)

from flask_wtf import csrf

from qhawariy.models.notificacion import Notificacion


logger = logging.getLogger(__name__)

bp = Blueprint("notificacion", __name__, url_prefix="/notificaciones")


@bp.route("notificaciones", methods=["GET"])
@login_required
def mostrar_notificaciones():
    notificaciones = Notificacion.obtener_todos_por_usuario(
        # Objeto Usuario.id_usuario
        current_user.id_usuario
    )
    token = csrf.generate_csrf()  # type: ignore
    return render_template(
        "notificacion/lista_notificaciones.html",
        notificaciones=notificaciones,
        token=token
    )


@bp.route("/leida/<int:notificacion_id>", methods=["POST"])
@login_required
def marcar_como_leida(notificacion_id: int):
    notificacion = Notificacion.obtener_por_id(notificacion_id)
    if notificacion:
        notificacion.marcar_como_leida()
        notificacion.guardar()
    return redirect(url_for("notificacion.mostrar_notificaciones"))
