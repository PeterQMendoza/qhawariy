import os
from pathlib import Path
from typing import Dict, Optional, Type

# Carpeta BASE del proyecto
BASE_DIR = Path(__file__).resolve().parents[1]

DEFAULT_SECRET_KEY = "66149efe039c9daaeda402ec5613d643b47c8960641d42664b4abcd48c683e32"
DEFAULT_PASSWORD_ADMIN = "1admin@qh"


def construir_postgres_uri(
    user: str,
    password: str,
    host: str,
    port: str,
    db: str,
    sslmode: Optional[str] = None
) -> str:
    """
    Construye una URI para SQLAlchemy con PostgreSQL (psycopg).
    Si password está vacío, omite la contraseña en la URI.
    """
    # Escapar caracteres especiales si es necesario (opcional)
    auth = f"{user}:{password}@" if password else f"{user}@"
    uri = f"postgresql+psycopg2://{auth}{host}:{port}/{db}"
    if sslmode:
        uri += f"?sslmode={sslmode}"
    return uri


class BaseConfig:
    APP_ENV = os.getenv("APP_ENV", "development")

    # Debug / Server
    DEBUG = False
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", "8000"))  # type: ignore

    # Paths
    BASE_DIR: Path = BASE_DIR
    # Configuracion de las rutas de archivos para cargar y manejar
    # archivos
    FILES_DIR: Path = BASE_DIR / "files"
    SHAPEFILE_FOLDER: Path = FILES_DIR / "shapefile"
    UPLOAD_FOLDER: Path = FILES_DIR / "uploads"
    DOWNLOAD_FOLDER: Path = FILES_DIR / "downloads"
    COORD_DATA_FOLDER: Path = FILES_DIR / "data"
    LOGS_FOLDER: Path = FILES_DIR / "logs"
    ALLOWED_EXTENSIONS = {'txt', 'csv', 'xlsx'}

    # Seguridad
    SECRET_KEY: str = os.getenv("SECRET_KEY", DEFAULT_SECRET_KEY)
    # Clave para usuario admin
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", DEFAULT_PASSWORD_ADMIN)

    # SQLALCHEMY por defecto (sobrescribe en subclase)
    SQLALCHEMY_DATABASE_URI: str = ""
    SQLALCHEMY_ECHO: bool = os.getenv(
        "SQL_ALCHEMY_ECHO",
        "False"
    ).lower() in ("1", "true")
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # Pool / performance (ajustar segun carga)
    SQLALCHEMY_ENGINE_OPTIONS: Dict[str, int] = {
        "pool_size": int(os.getenv("DB_POOL_SIZE", "5")),
        "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "10")),
        "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
        "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "1800")),
    }

    # Flask-Mail
    # Configuracion para email
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = os.getenv("MAIL_PORT", "587")
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_DEBUG = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = MAIL_USERNAME
    MAIL_MAX_EMAILS = None
    # 'smtp.gmail.com'
    MAIL_HOST = None
    DONT_REPLY_FROM_EMAIL = "direction from"
    ADMINS = ("admin@qhawariy.com",)

    # Caching
    # Configuracion para alamacenamiento cache con redis y flask-caching
    CACHE_TYPE = os.getenv("CACHE_TYPE", 'RedisCache')
    CACHE_REDIS_HOST = os.getenv("CACHE_REDIS_HOST", 'localhost')
    CACHE_REDIS_PORT = int(os.getenv("CACHE_REDIS_PORT", "6379"))
    CACHE_REDIS_DB = int(os.getenv("CACHE_REDIS_DB", "0"))

    # Configuracion para manejo de memoria cache con Flask-Caching
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", "300"))

    # Otros
    ITEMS_PER_PAGES = int(os.getenv("ITEMS_PER_PAGE", "20"))
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16*1024*1024))

    # Configuracion para claves recapcha
    # RECAPTCHA_PARAMETERS = {'hl': 'zh', 'render': 'explicit'}
    # RECAPTCHA_DATA_ATTRS = {'theme': 'dark'}

    # Configuracion para guardar las sessiones en las cookies
    REMEMBER_COOKIE_NAME = 'qhawariy_remember'
    REMEMBER_COOKIE_DURATION = 3600
    REMEMBER_COOKIE_SAMESITE = 'Lax'

    # Configuracion de tokens CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = SECRET_KEY
    WTF_CSRF_TIME_LIMIT = 3600
    WTF_CSRF_FIELD_NAME = 'csrf_token'

    # SESSION
    # para proteccion de sessiones y almacenamiento sessiones en l
    # cookies
    SESSION_PROTECTION = "strong"
    SESSION_COOKIE_NAME = 'qhawariy_session'
    # SESSION_COOKIE_DOMAIN='192.168.91.8:5000'
    SESSION_COOKIE_PATH = '/'
    SESSION_COOKIE_SAMESITE = 'Lax'
    # Establecer en True para paginas seguras HTTPS
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    # SESSION_COOKIE_SAMESITE=None#'Lax'
    PERMANENT_SESSION_LIFETIME = 3600

    # Configuracion para restablecer credenciales de usarios y
    # logearse en el sistema
    RESET_PASS_TOKEN_MAX_AGE = 3600


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_ECHO = True

    # DB Postgres
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "etms")
    DB_SSLMODE = os.getenv("DB_SSLMODE", None)

    SQLALCHEMY_DATABASE_URI = construir_postgres_uri(
        DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, sslmode=DB_SSLMODE
    )

    SQLALCHEMY_BINDS = {
        "users": construir_postgres_uri(
            os.getenv("DB_USERS_USER", DB_USER),
            os.getenv("DB_USERS_PASSWORD", DB_PASSWORD),
            os.getenv("DB_USERS_HOST", DB_HOST),
            os.getenv("DB_USERS_PORT", DB_PORT),
            os.getenv("DB_USERS_NAME", "etms_users"),
            os.getenv("DB_USERS_SSLMODE", DB_SSLMODE)
        )
    }


class TestingConfig(BaseConfig):
    DEBUG = False

    # DB
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "etms_test")
    DB_SSLMODE = os.getenv("DB_SSLMODE", None)
    SQLALCHEMY_DATABASE_URI = construir_postgres_uri(
        DB_USER,
        DB_PASSWORD,
        DB_HOST,
        DB_PORT,
        DB_NAME,
        sslmode=DB_SSLMODE
    )
    SQLALCHEMY_BINDS = {}  # definir si es necesario

    # MAIL
    MAIL_SUPPRESS_SEND = True
    MAIL_ASCII_ATTACHMENTS = False
    MAIL_BACKEND = ''


class ProductionConfig(BaseConfig):
    DEBUG = False
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "db.example.com")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "etms")
    DB_SSLMODE = os.getenv("DB_SSLMODE", "require")
    SQLALCHEMY_DATABASE_URI = construir_postgres_uri(
        DB_USER,
        DB_PASSWORD,
        DB_HOST,
        DB_PORT,
        DB_NAME,
        sslmode=DB_SSLMODE
    )
    SQLALCHEMY_BINDS = {}  # definir si es necesario


CONFIG_MAP: Dict[str, Type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "Production": ProductionConfig,
    "default": DevelopmentConfig
}
