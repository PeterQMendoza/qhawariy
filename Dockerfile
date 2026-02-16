# Usar una imagen base de Python
FROM python:3.12-slim

ARG APP_UID=1000
ARG APP_GID=1000

# Crear grupo y usuario con UID/GID controlados
RUN groupadd -g ${APP_GID} appuser || true \
    && useradd -m -u ${APP_UID} -g ${APP_GID} appuser

# Instalar certificados
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Instalar git y cliente SSH
RUN apt-get update && apt-get install -y \
    git \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias del sistema (para postgresql client, curl, etc)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar locales
RUN apt-get update && apt-get install -y locales \
    && sed -i '/es_PE.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen es_PE.UTF-8 \
    && update-locale LANG=es_PE.UTF-8

ENV LANG=es_PE.UTF-8
ENV LANGUAGE=es_PE:es
ENV LC_ALL=es_PE.UTF-8

# Estalecer directorio de trabajo
WORKDIR /qhawariy

# Actualizar pip antes de instalar dependencias
RUN pip install --upgrade pip setuptools wheel

# Copiar e Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el codigo de la aplicacion
COPY . .

# Dar permisos al usuario no root
RUN mkdir -p /qhawariy/static/.webassets-cache \
    && chown -R appuser:appuser /qhawariy \
    && chmod -R 750 /qhawariy/static/.webassets-cache

# Copiar entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Exponer puerto Flask
EXPOSE 5000

# ENTRYPOINT corre como root para poder ajustar permiso
ENTRYPOINT ["/entrypoint.sh"]

# Ejecutar como usuario no root
USER appuser

# Comando de arranque con uso de gunicorn como servidor WSGI
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "120", "--threads", "2", "app:app"]