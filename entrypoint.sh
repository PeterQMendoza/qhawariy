#!/bin/sh
set -e

APP_UID=${APP_UID:-1000}
APP_GID=${APP_GID:-1000}

# Asegurar existencia de la cache y permisos
mkdir -p /qhawariy/.webassets-cache

# Intentar cambiar propietario (Si el FS lo permite)
chown -R ${APP_UID}:${APP_GID} /qhawariy || true

# Permisos razonables para la cache
chmod -R 750 /qhawariy/static/.webassets-cache || true

# Ejecutar el comando como appuser si estamos en root
if [ "$(id -u)" = "0" ]; then
  exec su -s /bin/sh appuser -c "$*"
else
  exec "$@"
fi