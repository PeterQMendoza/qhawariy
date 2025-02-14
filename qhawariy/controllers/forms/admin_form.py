import datetime
from flask_wtf import FlaskForm
from wtforms import IntegerField, IntegerRangeField, TimeField, FormField, FieldList
from wtforms.fields import SelectField, SubmitField
from wtforms_html5 import AutoAttrMeta
from wtforms.validators import DataRequired,Optional,NumberRange

class NumeroForm(FlaskForm):
    control=SelectField('Control', validators=[Optional()],id='id_control_config',coerce=int)

# Formulario para asignar, cambiar rol a un usuario
class UserAdminForm(FlaskForm):
    class Meta(AutoAttrMeta):
        csrf=True
    
    rol=SelectField('Rol', validators=[DataRequired("Selecciona un rol")], id='select_rol',coerce=int)
    submit=SubmitField("Guardar")

# Formulario que permite establecer configuracio con respeco a la parte operativa
# de la aplicacion
class ConfiguracionForm(FlaskForm):
    class Meta(AutoAttrMeta):
        csrf=True
    tiempo_espera_vehiculo=TimeField(
        label="Tiempo que puede esperar un vehiculo para inciar viaje",
        validators=[DataRequired()],
        format="%H:%M"
    )
    tiempo_total_en_recorrido=TimeField(
        label="Tiempo que tarda en realizar recorrido de viaje",
        validators=[DataRequired()],
        format="%H:%M"
    )
    horario_inicio=TimeField(
        label="Tiempo que inicia la sesion de trabajo (debe especificar antes de que inicie el horario del primer vehiculo en salir)",
        validators=[DataRequired()],
        format="%H:%M"
    )
    horario_fin=TimeField(
        label="Tiempo que culmina toda los viajes realizados (por defecto: 9:59 PM)",
        validators=[DataRequired()],
        format="%H:%M"
    )
    cantidad_vehiculos_a_programar=IntegerRangeField(
        label="Cantidad maxima de vehiculos a programar",
        validators=[DataRequired(),NumberRange(min=0,max=44)],
        render_kw={"step":"1"},
    )
    secuencia_control_ida=FieldList(FormField(NumeroForm),min_entries=5)
    secuencia_control_vuelta=FieldList(FormField(NumeroForm),min_entries=5)

    submit=SubmitField(label="Guardar todo")
