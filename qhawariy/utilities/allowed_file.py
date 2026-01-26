from typing import Set, cast
from flask import current_app


def allowed_file(filename: str) -> bool:
    ALLOWED_EXTENSIONS: Set[str] = cast(
        Set[str],
        current_app.config['ALLOWED_EXTENSIONS']
    )
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
