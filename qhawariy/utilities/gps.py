from typing import List, Optional, Tuple
from sqlalchemy import func
from qhawariy import db


class GPSMixin:
    """Mixin para modelos con columna Geometry POINT (SRID 4326)."""
    ubicacion = None

    @classmethod
    def obtener_latitudes_longitudes(cls) -> Optional[Tuple[List[float], List[float]]]:
        """
        Devuelve (latitud, longitud) de la terminal
        """
        # Nota: ST_X= longitud, ST_Y = latitud
        puntos = (
            db.session.query(
                func.ST_X(cls.ubicacion),
                func.ST_Y(cls.ubicacion)
            )
            .all()
        )
        if puntos:
            latitudes: List[float] = [lat for lat, _ in puntos]
            longitudes: List[float] = [lon for _, lon in puntos]
            return latitudes, longitudes

        return None
