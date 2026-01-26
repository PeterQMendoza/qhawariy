from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TimeField
from wtforms_html5 import AutoAttrMeta
from wtforms.validators import DataRequired, Length


# Formularios para cambiar datos de la entidad Control
class ControlTiempoForm(FlaskForm):
    class Meta(AutoAttrMeta):  # type: ignore
        csrf = True
    tiempo = TimeField(
        "Tiempo",
        format="%H:%M:%S",
        validators=[DataRequired("Es necesario ingresar el tiempo")],
        render_kw={"step": "1"}
    )

    control = SelectField(
        "Codigo punto Control",
        validators=[DataRequired()],
        id="control_selected_1",
        coerce=int
    )

    submit = SubmitField("Agregar")


class ControlForm(FlaskForm):
    class Meta(AutoAttrMeta):  # type: ignore
        csrf = True

    codigo = StringField(
        "Codigo",
        validators=[DataRequired(), Length(max=8)]
    )

    latitud = StringField(
        "Latitud",
        validators=[
            DataRequired("Ingrese la ubicacion del punto de control")
        ]
    )

    longitud = StringField(
        "Longitud",
        validators=[
            DataRequired("Ingrese la ubicacion del punto de control")
        ]
    )

    submit = SubmitField("Agregar")


class ControlRutaForm(FlaskForm):
    class Meta(AutoAttrMeta):  # type: ignore
        csrf = True
    ruta = SelectField(
        "Seleccione ruta",
        validators=[DataRequired()],
        id="controlRuta_ruta_selected_1",
        coerce=int
    )
    control = SelectField(
        "Seleccione control",
        validators=[DataRequired()],
        id="controlRuta_control_selected_1",
        coerce=int
    )

    submit = SubmitField("Agregar")
