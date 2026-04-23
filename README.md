# RedAtlas Technical Challenge

Scraper inmobiliario en Python para Zillow (Puerto Rico), con extracción de resultados de búsqueda para **venta** y **alquiler**, persistencia en SQLite mediante SQLAlchemy y trazabilidad por logs.

## 1) Descripción del proyecto

Este proyecto automatiza la recolección de listings de Zillow utilizando Playwright.

Flujo general:

1. Inicializa configuración de scraping y conexión a base de datos.
2. Recorre dos segmentos de Zillow PR:
   - `sales` (For sale)
   - `rentals` (For rent)
3. Navega la página, simula comportamiento humano y resuelve captcha cuando aparece.
4. Extrae el JSON embebido en `#__NEXT_DATA__`.
5. Obtiene `listResults` y lo guarda en archivos locales por tipo de operación.
6. Normaliza campos clave y hace upsert en la tabla `listings`.

Punto de entrada: `main.py`

## 2) Secuencia del scraping

Secuencia basada en el código actual:

1. **Arranque de pipeline** (`main.py`)
   - Crea `ScrapingSettings`, `LoadData(ManageDB())` y `Scraping()`.
   - Itera `web_paths` con:
     - `{ "path": "sales", "filter": "For sale" }`
     - `{ "path": "rentals", "filter": "For rent" }`

2. **Inicialización navegador** (`src/config/scraping_settings.py`)
   - Lanza Chromium con Playwright (actualmente `headless=False`).
   - Crea contexto con user-agent y viewport definidos.

3. **Navegación y anti-bot** (`src/scripts/scraping.py`)
   - Navega a `https://www.zillow.com/pr/{path}`.
   - Ejecuta comportamiento humano simulado (scroll + mouse move).
   - Intenta resolver captcha (`src/utils/solve_captcha.py`).

4. **Extracción de resultados** (`src/scripts/scraping.py`)
   - Espera `#__NEXT_DATA__`.
   - Parsea JSON y accede al path:
     - `props.pageProps.searchPageState.cat1.searchResults.listResults`
   - Guarda respaldo en:
     - `data/for_sale/data_page.json`
     - `data/for_rent/data_page.json`

5. **Carga a base de datos** (`src/scripts/load_data.py`)
   - Recorre cada item de `listResults`.
   - Convierte tipos con helpers `safe_float` / `safe_int`.
   - Crea entidad `Listing` y realiza `session.merge(listing)` para upsert por `zpid`.
   - Commit final de la transacción.

6. **Observabilidad** (`src/config/logger.py`)
   - Registra logs en consola y en `logs/pipeline.log`.

## 3) Datos extraídos (esquemas, paths, filtros)

### 3.1 Filtros y segmentos

Configurados en `ScrapingSettings.web_paths`:

- For sale → path `sales`
- For rent → path `rentals`

### 3.2 Path de extracción en JSON

JSON fuente (DOM):

- Selector: `#__NEXT_DATA__`

Path usado para resultados:

- `props.pageProps.searchPageState.cat1.searchResults.listResults`

### 3.3 Archivos de salida

- `data/for_sale/data_page.json`
- `data/for_rent/data_page.json`

Estos dos archivos JSON se generan como respaldo intermedio para validar campos (por ejemplo `price`, `address`, `beds`, `baths`) antes de persistir los datos en la base de datos.

### 3.4 Esquema de datos crudo (muestra de `listResults`)

Campos comunes observados en los JSON de salida:

- `zpid`
- `detailUrl`
- `statusType`
- `price` (string con moneda, por ejemplo `"$125,000"`)
- `beds`
- `baths`
- `area`
- `address`
- `imgSrc`
- `latLong.latitude`
- `latLong.longitude`
- `hdpData.homeInfo.*` (metadata extendida)

Nota: en alquiler aparecen estructuras como `units[]` con precio por unidad, y en algunos casos no hay precio único a nivel raíz.

### 3.5 Esquema persistido en base de datos

Tabla: `listings` (`src/models/listing.py`)

- `zpid` (PK, String)
- `url` (String)
- `listing_status` (String)
- `property_type` (String)
- `latitude` (Float)
- `longitude` (Float)
- `price` (Integer)
- `bedrooms` (Integer)
- `bathrooms` (Float)
- `living_area` (Integer)
- `address` (Text)
- `description` (Text)
- `photo_url` (String)
- `data` (Text, JSON serializado de `homeInfo`)
- `scraped_at` (String, datetime UTC ISO)
- `status` (String)

Tabla: `errors` (`src/models/errors.py`)  (Donde quedan almacenados los logs de ejecucion en caso de error)

- `id` (PK, Integer)
- `timestamp` (String, datetime UTC ISO)
- `error` (String) (json with error type and message)

## 4) Tecnologías usadas

- **Python 3.10**
- **Playwright** (`playwright`) para automatización web
- **playwright-stealth** para hardening anti-bot (importado en settings)
- **SQLAlchemy 2.x** para ORM y persistencia
- **SQLite** como base local (`zillow_props.db`)
- **python-dotenv / dotenv** para variables de entorno
- **Logging** estándar de Python para observabilidad

Dependencias declaradas: ver `requirements.txt`.

## 5) Preguntas de arquitectura (Q&A)

### Pregunta 1

**Tu scraper con Playwright lleva 2 horas corriendo, no hay errores, pero el proceso está consumiendo 1.8 GB de RAM y cada página tarda el doble que al inicio. ¿Cómo diagnosticás qué está pasando y cómo lo resolverías? ¿Qué cambiarías en tu código o en la config de PM2?**

**Respuesta**

Como primer paso, revisaría los logs de ejecución, para saber que parte se trabo el proceso, revisaría si se esta cerrando la conexión al final de cada iteración, revisaría que no queden tantas response en memoria cache

### Pregunta 2

**El scraper corrió sin errores durante 3 días, pero al revisar la base de datos te das cuenta que la mitad de los registros tienen `price = null` y `address = null`. No hubo ningún crash ni log de error. ¿Qué pudo haber pasado y cómo diseñarías el sistema para detectar esto antes de que ocurra?**

**Respuesta**

En ese caso, es un problema de extracción del dato, en el elemento HTML o algúna conversión de precios a numero antes de guardar en la base de datos. Agregaria una validación para que el precio no se nulo, ni este vacio, es decir sea mayor que 0

### Pregunta 3

**Tenés un scraper corriendo 24/7 en PM2 y necesitás deployar un fix urgente. El proceso está en el medio de una corrida, procesando la página 15 de 40. ¿Cómo hacés el deploy sin perder el progreso ni duplicar registros ya procesados?**

**Respuesta**

Para no romper el proceso que esta corriendo, guardaría los datos en la base hasta donde llego el scrapper, y cuando este deployado con el cambio, lo configuro para que empiece desde la ultima pagina donde quedo sin ejecutar.

## Ejecución rápida

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/matiasfeliu92/red_atlas_technical_challenge.git
   ```
2. Entrar a la carpeta del proyecto:
   ```bash
   cd red_atlas_technical_challenge
   ```
3. Crear/activar entorno virtual.
4. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
5. Instalar navegador de Playwright:
   ```bash
   playwright install chromium
   ```
6. Ejecutar:
   ```bash
   python main.py
   ```

## Estructura resumida

```text
main.py
requirements.txt
data/
  for_rent/data_page.json
  for_sale/data_page.json
logs/pipeline.log
src/
  config/
  models/
  scripts/
  utils/
zillow_props.db
```
