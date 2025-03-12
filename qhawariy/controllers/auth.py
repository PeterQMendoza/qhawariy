import datetime

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

from flask_login import (
    login_user,
    logout_user,
    current_user,
    login_required
)

from flask_mail import Message
from flask_wtf import csrf

from werkzeug.utils import redirect
# from werkzeug.urls import url_parse
from urllib.parse import urlparse

from qhawariy import scheduler
from qhawariy import login_manager, mail
from qhawariy.models.usuario import Usuario
from qhawariy.models.usuario_rol import UsuarioRol
from qhawariy.models.rol import Rol
from qhawariy.controllers.decorators.auth import admin_required, send_email
from qhawariy.controllers.forms.auth_form import (
    CrearNuevoPasswordForm,
    RegisterForm,
    LoginForm,
    CambiaClaveForm,
    CambiaEmailForm,
    CambiarDatosForm,
    RestablecerPasswordForm
)

# Blueprint
bp = Blueprint("auth", __name__, url_prefix="/auth")

# Tiempo que permanecera logeado un usuario
# Para cambiar debe estar igualado al tiempo almacenado en la cookie de session
TIME_EXPIRE_LOGIN = datetime.timedelta(hours=1)


# Registrar usuario
@bp.route("/register", methods=("GET", "POST"))
@login_required
@admin_required
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        nombres = form.nombres.data
        apellidos = form.apellidos.data
        dni = form.dni.data
        email = form.email.data
        telefono = form.telefono.data
        clave = form.clave.data
        # Comprueba si el usuario este ya registrado con ese email
        user = Usuario.obtener_usuario_por_correo_electronico(email)

        if user is not None:
            flash(f"El email: {email} ya fue registrado por otro usuario", "error")
        else:
            # Establece al primer usuario como administrador
            us = Usuario.obtener_todos_usuarios()
            rol = None
            if len(us) == 0:
                # No se encuentra ningun usuario registrado
                # crear todos los roles
                rol_admin = Rol('Administrador')
                rol_admin.guardar()
                rol_controlador = Rol("Controlador")
                rol_controlador.guardar()
                rol_operacion = Rol("Operacion")
                rol_operacion.guardar()
                rol_trabajador = Rol("Trabajador")
                rol_trabajador.guardar()
                # Asignar el rol de administrador
                rol = rol_admin
            else:
                # asignar al usuario que se esta registrando como trabajador
                # que no podra visualizar nada
                rol_trabajador = Rol.obtener_por_rol("Trabajador")
                if rol_trabajador is None:
                    rol_trabajador = Rol("Trabajador")
                    rol_trabajador.guardar()
                rol = rol_trabajador
            user = Usuario(
                nombres=nombres,
                apellidos=apellidos,
                dni=dni,
                telefono=telefono,
                correo_electronico=email
            )
            user.establecer_clave(clave)
            user.guardar()
            # Se establece como trabajador
            usuario_rol = UsuarioRol(user.id_usuario, rol.id_rol)
            usuario_rol.guardar()

            # Envia un email al nuevo usuario por registrase al sistema (deshabilitado)
            text = f'Hola {apellidos}{nombres},Bienvenido a Sistema experto de Qhawariy'
            msg = f"<p> Hola,<strong>{apellidos}{nombres}</strong>,Bienvenido al qh</p>"
            send_email(
                subject=" Bienvenido a Qhawariy",
                sender=current_app.config['DONT_REPLY_FROM_EMAIL'],
                recipients=[email,],
                text_body=text,
                html_body=msg
            )
            # Redireccionamos a listar usuario
            next_page = request.args.get("next", None)
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for("admin.listar_usuarios")
            return redirect(next_page)

    return render_template("auth/register.html", form=form)


# Inicio de sesion de usuario
@bp.route("/login", methods=("GET", "POST"))
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))
    form = LoginForm()
    csrf.generate_csrf()

    error = None
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = Usuario.obtener_usuario_por_correo_electronico(email)
        if user is not None:
            is_check_password = user.revisar_clave(password)
            if is_check_password:
                login_user(
                    user,
                    remember=form.remember_me.data,
                    duration=TIME_EXPIRE_LOGIN
                )
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
    if form.validate_on_submit():
        user = Usuario.obtener_usuario_por_correo_electronico(form.email.data)
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


@bp.route("/restablece-password/<token>/<int:usuario_id>", methods=["GET", "POST"])
def restablecer_nuevo_password(token, usuario_id):
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))
    user = Usuario.obtener_usuario_por_id(usuario_id)
    tok = user.generar_token_restablecer_password()
    #
    usuario_validado = Usuario.validar_token_restablece_password(token, usuario_id)
    if not usuario_validado:
        flash("Error los credenciales no son validos", "error")
    form = CrearNuevoPasswordForm()
    if form.validate_on_submit():
        usuario_validado.establecer_clave(form.password.data)
        usuario_validado.guardar()
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
@login_manager.needs_refresh_handler
@login_required
def edit():
    id_user = current_user.id_usuario
    user = Usuario.obtener_usuario_por_id(id_user)
    form_datos = CambiarDatosForm(obj=user)
    form_email = CambiaEmailForm(obj=user)
    form_clave = CambiaClaveForm(obj=user)
    error = ''
    if form_clave.validate_on_submit() and form_clave.submit_clave.data:
        if form_clave.password.data == form_clave.password_confirmado.data:
            user.establecer_clave(form_clave.password.data)
            user.guardar()
            logout_user()
            next_page = request.args.get("next", None)
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for("auth.login")
            return redirect(next_page)
        else:
            error = """La nueva contraseña y la contraseña de
                confirmacion deben ser los mismos"""
    if form_email.validate_on_submit() and form_email.submit_email.data:
        user.correo_electronico = form_email.email.data
        user.guardar()
        logout_user()
        next_page = request.args.get("next", None)
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for("auth.login")
        return redirect(next_page)
    if form_datos.validate_on_submit() and form_datos.submit_datos.data:
        user.nombres = form_datos.nombres.data
        user.apellidos = form_datos.apellidos.data
        user.dni = form_datos.dni.data
        user.telefono = form_datos.telefono.data
        user.guardar()
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


@login_manager.user_loader
# @bp.before_request#Conocer al usuario
@scheduler.authenticate
def load_user(user_id):
    current_app.logger.debug('Vista para usuario %s', user_id)
    user = Usuario.query.filter_by(id_alternativo=user_id).first()
    if not id:
        return None
    return user


@login_manager.unauthorized_handler
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
