# Formularios
from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms.fields import (
    core,
    StringField,
    SubmitField,
    PasswordField,
    BooleanField,
    EmailField
)
# from wtforms.widgets import DateTimeInput,DateInput
from wtforms_html5 import AutoAttrMeta
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    AnyOf,
    Regexp,
    EqualTo
)

from qhawariy.models.usuario import Usuario


def validar_dni_unico(form: FlaskForm, field: core.Field):
    """ Valida que el DNI no este duplicado en la BD"""
    usuario = Usuario.obtener_por_dni(field.data)
    if usuario:
        raise ValidationError("El DNI ya se encuentra registrado")


# Formulario para registrar un nuevo usuario al sistema
class RegisterForm(FlaskForm):
    class Meta(AutoAttrMeta):  # type: ignore
        csrf = True

    nombres = StringField("Nombres", validators=[
        DataRequired("Necesitamos tus nombres"),
        Length(max=50),
        Regexp("^[A-Za-z ]*$", 0, "Los nombres deben contener solo letras")
    ])

    apellidos = StringField("Apellidos", validators=[
        DataRequired("Necesitamos tus apellidos."),
        Length(max=50),
        Regexp("^[A-Za-z ]*$", 0, "Los apellidos deben contener solo letras.")
    ])

    dni = StringField("DNI", validators=[
        DataRequired("Esta información es necesaria."),
        Length(max=10),
        Regexp("^[0-9]*$", 0, "El Numero de documento deben contener solo numeros."),
        validar_dni_unico
    ])

    email = EmailField("Correo Electronico", validators=[
        DataRequired("Necesitamos conocer tu correo electronico."),
        Email()
    ])

    telefono = StringField("Telefono", validators=[
        DataRequired("Necesitamos conocer tu telefono."),
        Length(max=15),
        Regexp("^[0-9]*$", 0, "El telefono deben contener solo numeros.")
    ])

    clave = PasswordField("Contraseña", validators=[
        DataRequired("Es necesario poner seguridad a tu cuenta"),
        Length(
            min=8,
            max=12,
            message="La contraseña debe tener al menos de 8 a 12 caracteres."
            ),
        Regexp(
            r'(?=.*\d)',
            message="La contraseña debe tener al menos un digito."
            ),
        Regexp(
            r'(?=.*[\W_])',
            message="La contraseña debe contener al menos un carácter especial: @,#,_."
            ),
    ])
    submit = SubmitField("Agregar usuario")


# Formulario para el acceso al sistema
class LoginForm(FlaskForm):
    class Meta(AutoAttrMeta):  # type: ignore
        csrf = True

    email = StringField("Email", validators=[DataRequired("Necesitamos tu email.")])
    password = PasswordField(
        "Contraseña",
        validators=[DataRequired("Falta tu contraseña.")]
    )

    remember_me = BooleanField(
        "Recordar datos",
        default=False,
        render_kw={'checked': ''},
        validators=[AnyOf([False, True])]
    )

    submit = SubmitField("Iniciar Sesión")


# Formulario para cambiar datos de usuario
class CambiarDatosForm(FlaskForm):
    class Meta(AutoAttrMeta):  # type: ignore
        csrf = True

    nombres = StringField(
        "Nombres",
        validators=[DataRequired("Necesitamos tus nombres."), Length(max=50)]
    )

    apellidos = StringField(
        "Apellidos",
        validators=[DataRequired("Necesitamos tus apellidos."), Length(max=50)]
    )

    dni = StringField(
        "DNI",
        validators=[
            DataRequired("Esta información es necesaria."),
            Length(max=10)
        ])

    telefono = StringField(
        "Telefono",
        validators=[DataRequired("Necesitamos conocer tu telefono."), Length(max=15)]
    )

    submit_datos = SubmitField("Cambiar Datos")


class CambiaClaveForm(FlaskForm):
    class Meta(AutoAttrMeta):  # type: ignore
        csrf = True

    password = PasswordField("Nueva Contraseña", validators=[
        DataRequired("Falta tu contraseña."),
        Length(
            min=8,
            max=12,
            message="La contraseña debe tener al menos de 8 a 12 caracteres."
            ),
        Regexp(
            r'(?=.*\d)',
            message="La contraseña debe tener al menos un digito."
            ),
        Regexp(
            r'(?=.*[\W_])',
            message="La contraseña debe contener al menos un carácter especial: @,#,_."
            ),
        ]
    )

    password_confirmado = PasswordField(
        "Repetir Nueva Contraseña",
        validators=[
            DataRequired("Debes escribir nuevamente la contraseña para confirmar."),
            EqualTo(
                "password",
                message="""La contraseña de confirmacion debe ser la misma que la
                 contraseña que escribiste."""
            )
        ]
    )

    submit_clave = SubmitField("Cambiar Contraseña")


class CambiaEmailForm(FlaskForm):
    class Meta(AutoAttrMeta):  # type: ignore
        csrf = True
    email = StringField("Email", validators=[
        DataRequired("Necesitamos tu email.")
    ])

    submit_email = SubmitField("Cambiar Email")


class RestablecerPasswordForm(FlaskForm):
    class Meta(AutoAttrMeta):  # type: ignore
        csrf = True

    email = StringField(
        "Email",
        validators=[
            DataRequired("Es necesario tu email para restablecer su contraseña."),
            Email()
        ]
    )

    submit = SubmitField("Restablecer")


class CrearNuevoPasswordForm(FlaskForm):
    class Meta(AutoAttrMeta):  # type: ignore
        csrf = True

    password = PasswordField("Nuevo contraseña", validators=[
        DataRequired("Debes ingresar una contraseña para restablecer tu password"),
        Length(
            min=8,
            max=12,
            message="La contraseña debe tener al menos de 8 a 12 caracteres."
        ),
        Regexp(
            r'(?=.*\d)',
            message="La contraseña debe tener al menos un digito."
        ),
        Regexp(
            r'(?=.*[\W_])',
            message="La contraseña debe contener al menos un carácter especial: @,#,_."
        ),
    ])

    password2 = PasswordField("Repite la contraseña", validators=[
        DataRequired("Debes ingresar un valor a este campo."),
        EqualTo(
            "password",
            message="Las dos contraseña ingresados deben de ser los mismos."
        )
    ])

    submit = SubmitField("Confirmar restablece password")


class NotificacionForm(FlaskForm):
    class Meta(AutoAttrMeta):  # type: ignore
        csrf = True

    submit = SubmitField("Marcar como leida")
