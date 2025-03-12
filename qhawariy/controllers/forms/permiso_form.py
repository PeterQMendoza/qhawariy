from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    DateTimeField,
    SearchField,
    SelectField,
    SubmitField,
    ValidationError
)
from wtforms.validators import DataRequired, InputRequired
from wtforms_html5 import AutoAttrMeta


def validate_numeric(form, field):
    if not field.data.isdigit():
        raise ValidationError(
            """EL valor debe ser numerico, que indique el numero de flota de un
            vehiculo.\nPor ejemplo: 23"""
        )


class AgregaPermisoForm(FlaskForm):
    class Meta(AutoAttrMeta):
        csrf = True

    id_vehiculo = SelectField(
        label="Seleccione vehiculo",
        validators=[DataRequired("Seleccion un vehiculo"), InputRequired()],
        id="select_id_vehiculo",
        coerce=int,
        render_kw={"step": "1"}
    )

    fecha_inicio = DateField(
        label="Fecha inicio",
        format="%Y-%m-%d",
        validators=[DataRequired()]
    )

    fecha_final = DateField(
        label="Fecha final",
        format="%Y-%m-%d",
        validators=[DataRequired()]
    )

    agregar = SubmitField("Agregar")

    def validate_fecha_menor(form, field):
        if form.fecha_inicio.data and field.data:
            if field.data <= form.fecha_inicio.data:
                raise ValidationError(
                    """La fecha final debe ser posterior a la fecha de inicio."""
                )


class EditaPermisoForm(FlaskForm):
    class Meta(AutoAttrMeta):
        csrf = True

    id_vehiculo = SelectField(
        label="Seleccione un vehiculo",
        validators=[DataRequired("Seleccion un vehiculo"), InputRequired()],
        id="select_vehiculo_e_filter_1",
        coerce=int,
        render_kw={"step": "1"}
    )

    fecha_inicio = DateTimeField(
        label="Fecha de Inicio",
        format="%Y-%m-%d %H:%M:%S",
        validators=[DataRequired("Es necesario esta informacion")]
    )

    fecha_final = DateTimeField(
        label="Fecha final",
        format="%Y-%m-%d %H:%M:%S",
        validators=[DataRequired("Es necesario esta informacion")]
    )

    submit = SubmitField("Guardar")


class BuscaPermisoForm(FlaskForm):
    class Meta(AutoAttrMeta):
        csrf = True

    busca = SearchField(
        label="Buscar por flota",
        validators=[DataRequired()]
    )

    submit = SubmitField("Buscar")
