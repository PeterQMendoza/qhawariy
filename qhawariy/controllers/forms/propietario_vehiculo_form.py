from flask_wtf import FlaskForm
from wtforms.fields import SelectField, SubmitField
from wtforms_html5 import AutoAttrMeta
from wtforms.validators import DataRequired


class PropietarioVehiculoForm(FlaskForm):
    class Meta(AutoAttrMeta):
        csrf = True
    propietario = SelectField(
        'Seleccione un propietario',
        validators=[DataRequired("selecciona un propietario")],
        id='select_propietario',
        coerce=int
    )

    vehiculo = SelectField(
        'Seleccione un vehiculo',
        validators=[DataRequired("selecciona un vehiculo")],
        id='select_vehiculo',
        coerce=int
    )

    submit = SubmitField("Agregar relación")
