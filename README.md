<p align="center">
    <img src="https://github.com/PeterQMendoza/qhawariy/blob/master/qhawariy/static/img/logo_qhawariy_color.svg" width="180px" height="180px">
</p>

# Qhawariy
![python](https://img.shields.io/badge/python-v3.12.6-blue.svg)
![flask](https://img.shields.io/badge/flask-v3.0.3-violet.svg)
![Leaflet](https://img.shields.io/badge/Leaflet-v1.9.4-green.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-v2.0.34-red.svg)
![geopandas](https://img.shields.io/badge/geopandas-v1.0.1-skyblue.svg)

Sistema para la administración y control de flotas de vehículos de transporte público

## Instalación
1. Clona este repositorio:
    ```bash
    git clone https://github.com/PeterQMendoza/qhawariy.git

2. Ve al directorio del proyecto:
    ```bash
    cd nombredelproyecto

3. Crea un entorno virtual de python y activalo:
    ```bash
    python -m venv .venv
    source .venv/Scripts/activate

5. Instala las dependencias del archivo requirements.txt:
    ```bash
    pip install -r requirements.txt

## Convención de nombres de ramas para nueva funcionalidad o ampliación de codigo
### Formato:
`feature/[MODULO]-[DESCRIPCION]-[VERSION|TAG|ID]`

### Reglas:
- Usa el prefijo `feature/` para indicar nuevos módulos.
- Describe brevemente el módulo y la funcionalidad que estás añadiendo.
- Usa guiones para separar palabras.
- Opcional: Agrega identificadores de versiones o números de tickets.

### Ejemplos:
- `feature/auth-login` - Nuevo módulo de inicio de sesión.
- `feature/cart-management` - Funcionalidad para la gestión del carrito de compras.
- `feature/reporting-tool-v1` - Módulo de generación de reportes, versión inicial.

## Convención de nombres de ramas para corrección de errores
Para la corrección de errores, sigue este esquema de nomenclatura:
- **Prefijo**: Usa `fix/` para indicar que la rama corrige un error.
- **Formato**: `[fix/]-[TIPO]-[MODULO]-[SEVERIDAD]-[ID]`

### Desglose:
- **TIPO**:
    -`BUG`: Error en el funcionamiento del sistema.
    -`UI`: Problemas relacionados con la interfaz de usuario.
    -`API`: Problema con la comunicación o respuesta de la API.
    -`DB`: Problema en la Base de Datos.
    -`SEC`: Problema de seguridad.
- **MODULO**: Nombre abreviado, en 4 letras, del módulo afectado (por ejemplo: AUTH para la autenticacion, etc)
- **SEVERIDAD**:
    -`CRIT`: Critico, necesita solución inmediate.
    -`HIGH`: Alta prioridad, solución prioritaria.
    -`MED`: Media prioridad, puede esterar un poco más.
    -`LOW`: Baja prioridad, mejoras menores.
- **ID**: Identificador incremental único (001, 002, ...).

### Ejemplos:
- `fix/BUG-AUTH-HIGH-003`: Error de inicio de sesión con prioridad alta.
- `fix/UI-VIAJ-MED-001`: Problema con prioridad media en la interfaz de viaje

### Gestión
1. El equipo de testing debe registrar los errores utilizando esta convención.
2. Los desarrolladores deben referirse a este código en los commits relacionados.
3. El equipo debe usar el código en sus herramientas de seguimiento como Jira, Trello, o GitHub Issues.

### Convención de COMMITS en código de error:
-Codigó: 
    ```bash
    git commit -m "Corrige BUG-AUTH-HIGH-003: Error de autenticación con credenciales válidas"

## License
Qhawariy software con licencia open-sourced software bajo la [BSD 3-Clause License].(https://opensource.org/licenses/BSD-3-Clause)
