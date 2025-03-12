from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField
from wtforms_html5 import AutoAttrMeta
from wtforms.validators import DataRequired


class RolForm(FlaskForm):
    class Meta(AutoAttrMeta):
        csrf = True
    rol = StringField(
        "Nombre de rol",
        validators=[DataRequired("Necesitamos saber el nombre que tendra el rol")]
    )

    submit = SubmitField("Guardar")
