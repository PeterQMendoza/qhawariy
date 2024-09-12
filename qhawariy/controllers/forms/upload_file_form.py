from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired,FileAllowed
from wtforms.fields import FileField, SubmitField
from wtforms_html5 import AutoAttrMeta

class UploadFileForm(FlaskForm):
    class Meta(AutoAttrMeta):
        csrf=True
    file=FileField("Seleccione un archivo con extension txt, csv o xlsx",validators=[FileRequired(),FileAllowed(["txt", "csv", "xlsx"], "El archivo no tiene una extensión de: txt, csv, xlsx",),],render_kw={"class": "form-control-file border"},)
    submit=SubmitField("Subir Archivo")