from flask_wtf import FlaskForm
from wtforms import SearchField
from wtforms.fields import StringField,IntegerField,SelectField, SubmitField, PasswordField, BooleanField, DateTimeField,DateField,EmailField
from wtforms.widgets import DateTimeInput,DateInput
from wtforms_html5 import AutoAttrMeta
from wtforms.validators import DataRequired,InputRequired ,Email, Length,AnyOf,Regexp

class PropietarioForm(FlaskForm):
    class Meta(AutoAttrMeta):
        csrf=True
    nombres = StringField("Nombres",validators=[DataRequired("Necesitamos esta informacion")])
    apellidos = StringField("Apellidos",validators=[DataRequired("Necesitamos esta informacion")])
    telefono = StringField("Telefono",validators=[DataRequired("Necesitamos esta informacion")])
    documento_identificacion = StringField("Documento_identificacion",validators=[DataRequired("Necesitamos esta informacion")])
    submit=SubmitField("Guardar")

class CambiarPropietarioForm(FlaskForm):
    class Meta(AutoAttrMeta):
        csrf=True
    nombres = StringField("Nombres",validators=[DataRequired("Necesitamos esta informacion")])
    apellidos = StringField("Apellidos",validators=[DataRequired("Necesitamos esta informacion")])
    telefono = StringField("Telefono",validators=[DataRequired("Necesitamos esta informacion")])
    documento_identificacion = StringField("Documento_identificacion",validators=[DataRequired("Necesitamos esta informacion")])
    submit=SubmitField("Guardar Cambio")


class BuscarPropietarioForm(FlaskForm):
    class Meta(AutoAttrMeta):
        csrf=True
    dni=SearchField('Buscar por DNI', validators=[InputRequired("Ingrese un documento de identidad"),Length(max=10),Regexp("^[0-9]*$",0,"El Numero de documento deben contener solo numeros")])
    submit=SubmitField("Buscar")