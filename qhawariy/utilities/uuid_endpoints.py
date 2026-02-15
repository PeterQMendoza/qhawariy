from typing import Any, Optional
import uuid
import base64
from sqlalchemy import CHAR, Dialect, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql.type_api import TypeEngine


class ShortUUID(TypeDecorator[CHAR]):
    """
    ShortUUID: Maneja los UUIDs de los modelos y su representacion corta
    en base58/base64 que se utilizar en los endpoints
    - Ejemplo: http://www.qhawariy/usuarios/hUHuis65sd
    """
    impl = CHAR(36)

    def load_dialect_impl(
        self,
        dialect: Dialect
    ) -> TypeEngine[Any]:
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(
        self,
        value: Optional[Any],
        dialect: Any
    ) -> Optional[str]:
        if value is None:
            return None

        if isinstance(value, uuid.UUID):  # type: ignore
            return str(value)

        try:
            return str(uuid.UUID(value))
        except (ValueError, AttributeError, TypeError):
            pass

        try:
            # decodifica corto_id a UUID
            almohadilla = value + '=' * (-len(value) % 4)
            raw_bytes = base64.urlsafe_b64decode(almohadilla)
            if len(raw_bytes) == 16:
                return str(uuid.UUID(bytes=raw_bytes))
        except Exception:
            pass

        raise ValueError(
            f"EL valor no corresponde a un UUID valido ni a un short_id: {value}"
        )

    def process_result_value(
        self,
        value: Optional[str],
        dialect: Any
    ) -> Optional[Any]:
        if value is None:
            return None
        # SI es un objeto UUID
        if isinstance(value, uuid.UUID):
            return base64.urlsafe_b64encode(value.bytes).rstrip(b'=').decode('utf-8')
        # string
        if isinstance(value, str):  # type: ignore
            return (
                base64.urlsafe_b64encode(uuid.UUID(value).bytes)
                .rstrip(b'=')
                .decode('utf-8')
            )
        # bytes
        if isinstance(value, (bytes, bytearray)):
            return base64.urlsafe_b64encode(value).rstrip(b'=').decode('utf-8')

        raise ValueError(f"Tipo inesperado para UUID: {type(value)}")
