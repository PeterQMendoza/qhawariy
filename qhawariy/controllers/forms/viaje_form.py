from flask_wtf import FlaskForm

import pytz
from wtforms import IntegerField

from wtforms.fields import SelectField, SubmitField
from wtforms_html5 import AutoAttrMeta
from wtforms.validators import DataRequired

lima_tz = pytz.timezone('America/Lima')


class ViajeForm(FlaskForm):
    class Meta(AutoAttrMeta):
        csrf = True

    vehiculo = SelectField(
        "Seleccione un vehiculo",
        validators=[DataRequired("Seleccione un vehiculo")],
        id='select_vehiculo_1',
        coerce=int
    )
    ruta = SelectField(
        "Seleccione una ruta",
        validators=[DataRequired("Seleccione una ruta")],
        id='select_ruta_1',
        coerce=int
    )
    # Referido al orden
    orden = IntegerField(
        "Numero de orden de viaje",
        validators=[DataRequired("Es necesarios el orden del viaje")]
    )
    submit = SubmitField("Agregar")
