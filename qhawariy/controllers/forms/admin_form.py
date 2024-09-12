from flask_wtf import FlaskForm
from wtforms.fields import SelectField, SubmitField
from wtforms_html5 import AutoAttrMeta
from wtforms.validators import DataRequired

# Formulario para asignar, cambiar rol a un usuario
class UserAdminForm(FlaskForm):
    class Meta(AutoAttrMeta):
        csrf=True
    
    rol=SelectField('Rol', validators=[DataRequired("Selecciona un rol")], id='select_rol',coerce=int)
    submit=SubmitField("Guardar")
