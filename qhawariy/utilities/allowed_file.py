from flask import current_app

def allowed_file(filename):
    ALLOWED_EXTENSIONS=current_app.config['ALLOWED_EXTENSIONS']
    return '.'in filename and \
        filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS