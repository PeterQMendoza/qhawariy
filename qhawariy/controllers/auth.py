import datetime
import logging
from typing import Optional, cast

from flask import (
    Blueprint,
    flash,
    render_template_string,
    url_for,
    # redirect,
    render_template,
    request,
    current_app,
)

from flask.typing import ResponseReturnValue
from flask_login import (
    login_user,  # type: ignore
    logout_user,
    current_user,
    login_required  # type: ignore
)

from flask_mail import Message

from werkzeug.utils import redirect
# from werkzeug.urls import url_parse
from urllib.parse import urlparse

from qhawariy import scheduler
from qhawariy import login_manager, mail
from qhawariy.models.usuario import Usuario
from qhawariy.models.usuario_rol import UsuarioRol
from qhawariy.models.rol import Rol
from qhawariy.forms.auth_form import (
    CrearNuevoPasswordForm,
    RegisterForm,
    LoginForm,
    CambiaClaveForm,
    CambiaEmailForm,
    CambiarDatosForm,
    RestablecerPasswordForm
)
from qhawariy.services.auth_service.send_mail import send_email  # type: ignore
from qhawariy.services.notifications_service.factory import NotificacionFactory
from qhawariy.utilities.decorators import admin_required
from qhawariy.utilities.redirect import redireccion_seguro

logger = logging.getLogger(__name__)

# Blueprint
bp = Blueprint("auth", __name__, url_prefix="/auth")

# Tiempo que permanecera logeado un usuario
# Para cambiar debe estar igualado al tiempo almacenado en la cookie de session
TIME_EXPIRE_LOGIN = datetime.timedelta(hours=1)


# Registrar usuario
@bp.route("/registrar", methods=("GET", "POST"))
@login_required
@admin_required
def register():
    form = RegisterForm()
    if form.validate_on_submit():  # type: ignore
        nombres = cast(str, form.nombres.data)
        apellidos = cast(str, form.apellidos.data)
        dni = cast(str, form.dni.data)
        email = cast(str, form.email.data)
        telefono = cast(str, form.telefono.data)
        clave = cast(str, form.clave.data)

        # Comprueba si el usuario este ya registrado con ese email
        user = Usuario.obtener_usuario_por_correo_electronico(email)
        if user:
            flash(f"El email: {email} ya fue registrado por otro usuario", "error")
            redireccion_seguro("auth.register", form=form)

        # Crear usuario
        user_registro: Optional[Usuario] = None
        rol = asignar_rol_inicial()
        try:
            user_registro = Usuario(
                nombres=nombres,
                apellidos=apellidos,
                dni=dni,
                telefono=telefono,
                correo_electronico=email
            )
            user_registro.establecer_clave(clave=clave)
            user_registro.guardar()
        except Exception as e:
            logger.error(f"Error: no ha sido posible registrar al usuario\n{e}")
            flash("No se pudo registrar el usuario", "error")
            redireccion_seguro("auth.register", form=form)

        if user_registro is None:
            flash("No se pudo registrar el usuario", "error")
            return render_template("auth/register.html", form=form)
        usuario_rol = UsuarioRol(user_registro.id_usuario, rol.id_rol)
        usuario_rol.guardar()

        enviar_email_bienvenida(nombres=nombres, apellidos=apellidos, email=email)
        redireccion_seguro("home.index")

    return render_template("auth/register.html", form=form)


def asignar_rol_inicial() -> Rol:
    if Usuario.existe_usuario():
        rol_trabajador = Rol.obtener_por_rol("Trabajador")
        if rol_trabajador is None:
            rol_trabajador = Rol("Trabajador")
            rol_trabajador.guardar()
        return rol_trabajador
    else:
        roles = {
            "Administrador": Rol("Administrador"),
            "Controlador": Rol("Controlador"),
            "Operacion": Rol("Operacion"),
            "Trabajador": Rol("Trabajador"),
        }
        for r in roles.values():
            r.guardar()
        return roles["Administrador"]


def enviar_email_bienvenida(
    nombres: str,
    apellidos: str,
    email: str
) -> None:
    text = f"Hola {apellidos} {nombres} Bienvenido a Qhawariy"
    msg = (
        f"<p>Hola, <strong>{apellidos} {nombres}</strong>, "
        f"Bienvenido al sistema Qhawariy</p>"
    )
    try:
        send_email(
            subject="Bienvenido a Qhawariy",
            sender=cast(str, current_app.config["DONT_REPLY_FROM_EMAIL"]),
            recipients=[email],
            text_body=text,
            html_body=msg,
        )
    except Exception as e:
        logger.warning(f"No se pudo enviar email de bienvenida: {e}")


# Inicio de sesion de usuario
@bp.route("/login", methods=("GET", "POST"))
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))
    form = LoginForm()

    error = None
    if form.validate_on_submit():  # type: ignore
        email = cast(str, form.email.data)
        password = cast(str, form.password.data)
        user = Usuario.obtener_usuario_por_correo_electronico(email)
        if user is not None:
            is_check_password = user.revisar_clave(password)
            if is_check_password:
                login_user(
                    user,
                    remember=form.remember_me.data,
                    duration=TIME_EXPIRE_LOGIN
                )
                NotificacionFactory.crear_notificacion(
                    user.id_usuario,
                    "Iniciaste sesion"
                ).guardar()
                next_page = request.args.get("next", None)
                if not next_page or urlparse(next_page).netloc != '':
                    next_page = url_for("home.index")
                return redirect(next_page)
            else:
                error = "La constraseña que ingresaste no son los correctos"
        else:
            error = f" El email:{email} no se encuentra registrado"
    return render_template("auth/login.html", form=form, error=error)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("home.index"))


# Para resteblacer cuando el usuario olvido la contrasenia
@bp.route("/restablecer-password", methods=["GET", "POST"])
def restablecer_password():
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))
    form = RestablecerPasswordForm()
    if form.validate_on_submit():  # type: ignore
        mail_validated = cast(str, form.email.data)
        user = Usuario.obtener_usuario_por_correo_electronico(mail_validated)
        if user:
            envia_restablecer_password_email(user)
            flash(
                """Las instrucciones para restablecer tu contrasenia fue enviado a
                tu correo electronico""",
                "info"
            )
            return redirect(url_for("home.index"))
        else:
            flash(
                """El correo electronico ingresado no se encuentra registrado en
                este sistema""",
                "error")
            return redirect(url_for("auth.restablecer_password"))
    return render_template("auth/restablece_password.html", form=form)


@bp.route("/restablece-password/<token>/<string:usuario_id>", methods=["GET", "POST"])
def restablecer_nuevo_password(token: str, usuario_id: str):
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))
    user = Usuario.obtener_usuario_por_id(usuario_id)
    if user is None:
        flash("El usuario no existe", "error")
        return redirect(url_for("auth.login"))
    tok = user.generar_token_restablecer_password()
    #
    usuario_validado = Usuario.validar_token_restablece_password(token, usuario_id)
    if not usuario_validado:
        flash("Error los credenciales no son validos", "error")
        return redirect(url_for("auth.login"))
    form = CrearNuevoPasswordForm()
    if form.validate_on_submit():  # type: ignore
        pass_user = cast(str, form.password.data)
        usuario_validado.establecer_clave(pass_user)
        usuario_validado.guardar()
        NotificacionFactory.crear_notificacion(
            usuario_validado.id_usuario,
            "Restableciste tu password correctamente.",
            "alto"
        ).guardar()
        next_page = request.args.get("next", None)
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for("auth.login")
        return redirect(next_page)
    return render_template(
        "auth/restablece_nuevo_password.html",
        form=form,
        token=tok,
        usuario=usuario_validado
    )


@bp.route('/edit', methods=("GET", "POST"))
@login_manager.needs_refresh_handler  # type: ignore
@login_required
def edit() -> ResponseReturnValue:
    id_user = current_user.id_usuario
    user = Usuario.obtener_usuario_por_id(id_user)
    if user is None:
        flash("El usuario no existe en la sesion dada", "error")
        return redirect(url_for("auth.login"))
    form_datos = CambiarDatosForm(obj=user)
    form_email = CambiaEmailForm(obj=user)
    form_clave = CambiaClaveForm(obj=user)
    error = ''
    if (
        form_clave.validate_on_submit() and  # type: ignore
        form_clave.submit_clave.data
    ):
        if form_clave.password.data == form_clave.password_confirmado.data:
            user.establecer_clave(form_clave.password.data)
            user.guardar()
            logout_user()
            # Notificacion
            NotificacionFactory.crear_notificacion(
                id_user,
                "Cambiaste tu contraseña correctamente",
                "alto"
            ).guardar()
            next_page = request.args.get("next", None)
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for("auth.login")
            return redirect(next_page)
        else:
            error = """La nueva contraseña y la contraseña de
                confirmacion deben ser los mismos"""
    if (
        form_email.validate_on_submit() and  # type: ignore
        form_email.submit_email.data
    ):
        user.correo_electronico = form_email.email.data
        user.guardar()
        logout_user()
        # Notificacion
        NotificacionFactory.crear_notificacion(
            id_user,
            "Cambiaste tu correo electronico correctamente.",
            "alto"
        ).guardar()
        next_page = request.args.get("next", None)
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for("auth.login")
        return redirect(next_page)
    if (
        form_datos.validate_on_submit() and  # type: ignore
        form_datos.submit_datos.data
    ):
        user.nombres = form_datos.nombres.data
        user.apellidos = form_datos.apellidos.data
        user.dni = form_datos.dni.data
        user.telefono = form_datos.telefono.data
        user.guardar()
        # Notificacion
        NotificacionFactory.crear_notificacion(
            id_user,
            "Cambiaste tus datos personales correctamente."
        ).guardar()
        next_page = request.args.get("next", None)
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for("auth.login")
        return redirect(next_page)

    return render_template(
        "auth/edit.html",
        form_datos=form_datos,
        user=user,
        form_clave=form_clave,
        form_email=form_email,
        error=error
    )


@login_manager.user_loader  # type: ignore
# @bp.before_request#Conocer al usuario
@scheduler.authenticate  # type: ignore
def load_user(user_id: str) -> Optional["Usuario"]:
    user = Usuario.obtener_usuario_por_id_alternativo(user_id)
    if user is None:
        return None
    current_app.logger.warning('Vista para usuario %s', user.nombres)
    return user


@login_manager.unauthorized_handler  # type: ignore
def unauthorized():
    flash(message="Debes iniciar sesión para visualizar la página", category="message")
    return redirect(url_for("auth.login"))


# Funciones para restablecer password
RESTABLECER_PASSWORD_EMAIL_HTML_CONTENIDO = """
<p>Hola,</p>
<p>
Tu recibiste este email porque solicitaste restablecer tu password para tu cuenta.
</p>
<p>
    Para restablecer tu password
    <a href="{{restablece_password_url}}">Haz click aqui</a>
</p>
<p>
    Alternativamente, tu puedes copiar el siguiente link en la barra de direccion de tu
    buscador:<br>
    {{restablece_password_url}}
</p>
<p>
Si tu no enviaste esta solicitud para restablecer tu password, por favor contactar con
alguien del equipo de desarrollo.
</p>
<p>
    ¡Gracias!
</p>
"""


def envia_restablecer_password_email(usuario: Usuario):
    restablece_password_url = url_for(
        "auth.restablecer_password",
        token=usuario.generar_token_restablecer_password(),
        user_id=usuario.id_usuario,
        _external=True
    )
    cuerpo_email = render_template_string(
        RESTABLECER_PASSWORD_EMAIL_HTML_CONTENIDO,
        restablece_password_url=restablece_password_url
    )

    with mail.connect() as conn:
        mensaje = Message(
            subject="Restablecer tu password",
            html=cuerpo_email,
            recipients=[usuario.correo_electronico],
        )
        conn.send(mensaje)
