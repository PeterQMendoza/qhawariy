from flask_wtf import FlaskForm
from wtforms.fields import StringField,IntegerField,SelectField, SubmitField, PasswordField, BooleanField, DateTimeField,DateField,EmailField
from wtforms.widgets import DateTimeInput,DateInput
from wtforms_html5 import AutoAttrMeta
from wtforms.validators import DataRequired, Email, Length,AnyOf,URL

class RutaTerminalForm(FlaskForm):
    class Meta(AutoAttrMeta):
        csrf=True
    terminal1 = SelectField("Terminal 1",validators=[DataRequired("Seleccione un terminal")], id='select_terminal_1',coerce=int)
    terminal2 = SelectField("Terminal 2",validators=[DataRequired("Seleccione un terminal")], id='select_terminale_2',coerce=int)
    submit=SubmitField("Agregar")
    
class AgregarTerminalForm(FlaskForm):
    class Meta(AutoAttrMeta):
        csrf=True
    direccion= StringField("Direccion",validators=[DataRequired("Necesitamos esta informacion")])
    latitud = StringField("Ubicacion GPS latitud del terminal")
    longitud = StringField("Ubicacion GPS longitud del terminal")
    departamento = SelectField("Departamento",validators=[DataRequired("Seleccione un departamento")], id='select_departamento',coerce=int)
    provincia = SelectField("Provincia",validators=[DataRequired("Seleccione una provincia")], id='select_provincia',coerce=int)
    distrito = SelectField("Distrito",validators=[DataRequired("Seleccione un distrito")], id='select_distrito',coerce=int)
    submit=SubmitField("Guardar")

class EditarTerminalForm(FlaskForm):
    class Meta(AutoAttrMeta):
        csrf=True
    direccion= StringField("Direccion",validators=[DataRequired("Necesitamos la direccion")])
    latitud= StringField("Ubicacion GPS latitud")
    longitud = StringField("Ubicacion GPS longitud")
    departamento = SelectField("Departamento",validators=[DataRequired("Seleccione un departamento")], id='select_departamento',coerce=int)
    provincia = SelectField("Provincia",validators=[DataRequired("Seleccione una provincia")], id='select_provincia',coerce=int)
    distrito = SelectField("Distrito",validators=[DataRequired("Seleccione un distrito")], id='select_distrito',coerce=int)
    submit=SubmitField("Guardar cambio")

class AgregarRutaForm(FlaskForm):
    class Meta(AutoAttrMeta):
        csrf=True
    codigo = StringField("Codigo",validators=[DataRequired("Necesitamos esta informacion")])
    inicio_vigencia = DateField("Fecha de inicio vigencia",validators=[DataRequired("Necesitamos esta informacion")])
    fin_vigencia = DateField("Fecha de fin vigencia",validators=[DataRequired("Necesitamos esta informacion")])
    documento = StringField("Documento",validators=[DataRequired("Necesitamos esta informacion"),URL(require_tld=True,message='Una URL debe contener el sufijo de "http://"+"www."+"nombre-dominio"+"" ejemplos:http://www.domain.com o http://domain.com')])

    terminal1 = SelectField("Terminal 1",validators=[DataRequired("Seleccione un terminal")], id='select_terminal_1',coerce=int)
    terminal2 = SelectField("Terminal 2",validators=[DataRequired("Seleccione un terminal")], id='select_terminale_2',coerce=int)
    submit=SubmitField("Guardar")

class EditarRutaForm(FlaskForm):
    class Meta(AutoAttrMeta):
        csrf=True
    codigo = StringField("Codigo",validators=[DataRequired("Necesitamos esta informacion")])
    inicio_vigencia = DateField("Fecha de inicio vigencia",validators=[DataRequired("Necesitamos esta informacion")])
    fin_vigencia = DateField("Fecha de fin vigencia",validators=[DataRequired("Necesitamos esta informacion")])
    documento = StringField("Link del documento",validators=[DataRequired("Necesitamos esta informacion")])

    terminal1 = SelectField("Terminal 1",validators=[DataRequired("Seleccione un terminal")], id='select_terminal_1',coerce=int)
    terminal2 = SelectField("Terminal 2",validators=[DataRequired("Seleccione un terminal")], id='select_terminale_2',coerce=int)
    submit=SubmitField("Guardar cambio")