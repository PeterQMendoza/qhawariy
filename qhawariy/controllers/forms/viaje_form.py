import datetime
from flask_wtf import FlaskForm

import pytz
from wtforms import  IntegerField, validators

from wtforms.fields import DateField,StringField,SelectField, SubmitField, TimeField
from wtforms.widgets import DateTimeInput,DateInput
from wtforms_html5 import AutoAttrMeta
from wtforms.validators import DataRequired, Email, Length,AnyOf

lima_tz=pytz.timezone('America/Lima')

class ViajeForm(FlaskForm):
    class Meta(AutoAttrMeta):
        csrf=True
    vehiculo=SelectField("Seleccione un vehiculo",validators=[DataRequired("Seleccione un vehiculo")],id='select_vehiculo_1',coerce=int)
    ruta=SelectField("Seleccione una ruta",validators=[DataRequired("Seleccione una ruta")],id='select_ruta_1',coerce=int)
    orden=IntegerField("Numero de orden de viaje",validators=[DataRequired("Es necesarios el orden del viaje")])#referido al orden
    submit=SubmitField("Agregar")