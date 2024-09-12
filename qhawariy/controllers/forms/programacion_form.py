import datetime
from flask_wtf import FlaskForm

import pytz
from wtforms import DateTimeLocalField, validators

from wtforms.fields import StringField,TimeField,SelectField, SubmitField, PasswordField, BooleanField, DateTimeField,DateField,EmailField
from wtforms_html5 import AutoAttrMeta
from wtforms.validators import DataRequired,InputRequired

LIMA_TZ=pytz.timezone('America/Lima')

class ProgramacionForm(FlaskForm):
    class Meta(AutoAttrMeta):
        csrf=True
    ruta=SelectField('Seleccione una ruta', validators=[DataRequired("Selecciona una ruta")], id='select_ruta_1',coerce=int)
    fecha_programa=DateField("Fecha de programacion",validators=[InputRequired("Es necesario esta informacion")])
    submit=SubmitField("Agregar")

class AgregaVehiculoProgramadoForm(FlaskForm):
    class Meta(AutoAttrMeta):
        csrf=True
    vehiculo=SelectField('Seleccione un vehiculo', validators=[DataRequired("selecciona un vehiculo")], id='select_vehiculo',coerce=int)
    tiempo=TimeField("Tiempo de salida (HH:MM:SS)",format="%H:%M:%S",validators=[DataRequired("Necesitamos esta informacion"),validators.InputRequired()],render_kw={"step": "1"})
    submit=SubmitField("Agregar vehiculo")

class BuscarProgramacionForm(FlaskForm):
    class Meta(AutoAttrMeta):
        csrf=True
    fecha=DateField('Buscar por fecha', validators=[InputRequired("selecciona una fecha")],default=datetime.datetime.now(tz=LIMA_TZ),render_kw={"step": "1"})
    submit=SubmitField("Buscar")
