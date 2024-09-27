from flask_wtf import FlaskForm
from wtforms.fields import StringField,IntegerField,SelectField, SubmitField, SearchField, BooleanField, DateTimeField,DateField,EmailField
from wtforms.widgets import DateTimeInput,DateInput
from wtforms_html5 import AutoAttrMeta
from wtforms.validators import DataRequired, Email, Length,AnyOf

class VehiculoForm(FlaskForm):
    class Meta(AutoAttrMeta):
        csrf=True
    flota=IntegerField("Numero de Flota",validators=[DataRequired("No especificaste la placa del vehiculo")])
    placa=StringField("Placa del vehiculo",validators=[DataRequired("No especificaste la placa del vehiculo"),Length(max=10)])
    marca=StringField("Marca del vehiculo",validators=[DataRequired("Mencionanos la marca del vehiculo?"),Length(max=40)])
    modelo=StringField("Modelo del vehiculo",validators=[DataRequired("Mencionanos su modelo?"),Length(max=40)])
    numero_asientos=IntegerField("Numero de asientos",validators=[DataRequired("Cuentanos cunatos asientos tiene")])
    fecha_fabricacion=DateField("Fecha de fabricacion",validators=[DataRequired("que fecha fue fabricado el vehiculo")])
    submit=SubmitField("Agregar vehiculo")

class EditarVehiculoForm(FlaskForm):
    class Meta(AutoAttrMeta):
        csrf=True
    flota=IntegerField("Numero de Flota",validators=[DataRequired("No especificaste la placa del vehiculo")])
    placa=StringField("Placa del vehiculo",validators=[DataRequired("No especificaste la placa del vehiculo"),Length(max=10)])
    marca=StringField("Marca del vehiculo",validators=[DataRequired("Mencionanos la marca del vehiculo?"),Length(max=40)])
    modelo=StringField("Modelo del vehiculo",validators=[DataRequired("Mencionanos su modelo?"),Length(max=40)])
    numero_asientos=IntegerField("Numero de asientos",validators=[DataRequired("Cuentanos cunatos asientos tiene")])
    fecha_fabricacion=DateField("Fecha de fabricacion",validators=[DataRequired("que fecha fue fabricado el vehiculo")])
    activo=BooleanField("Habilitado para ser programado")
    submit=SubmitField("Guardar Cambios")

class BuscarVehiculoForm(FlaskForm):
    class Meta(AutoAttrMeta):
        csrf=True
    busca=SearchField("Buscar",validators=[DataRequired("No ingresaste un valor para buscar")])
    filter=SelectField("Buscar por:", id='select_filter_1',coerce=int)
    submit=SubmitField("Buscar")