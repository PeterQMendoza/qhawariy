from typing import Any
from urllib.parse import urlparse
from flask import redirect, request, url_for

DEFAULT_NEXT = "/"


def redireccion_seguro(endpoint: str, **values: Any):
    """
    Redirecion segura: si 'next' es valido  relativo, usalo".
    Si no, redirige al endpoint indicado
    """
    siguiente_pagina = request.args.get("next", None)
    if not siguiente_pagina or urlparse(siguiente_pagina).netloc != '':
        return redirect(url_for(endpoint, next=DEFAULT_NEXT, **values))

    destino_por_defecto = url_for(endpoint, **values)
    if siguiente_pagina == destino_por_defecto:
        return redirect(url_for(destino_por_defecto, next=DEFAULT_NEXT, **values))

    return redirect(siguiente_pagina)
