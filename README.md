# Práctica Madrid Sostenible - Infraestructura de Almacenamiento para la Ciudad Inteligente

Este repositorio contiene la infraestructura y scripts necesarios para construir un **Data Lakehouse** que integra datos públicos de movilidad, urbanismo, medioambiente, energía y participación ciudadana para el análisis y la toma de decisiones sostenibles en Madrid.

## Diagrama de Infraestructura

![Arquitectura del Data Lake y Data Warehouse](diagrama_infraestructura.png)


La infraestructura diseñada combina un **Data Lake multicapa** y un **Data Warehouse dimensional** para garantizar una gestión flexible, escalable y orientada al análisis de datos urbanos. En la **RAW ZONE** del Data Lake se almacenan los datos en su formato original, mientras que en la **CLEAN ZONE** se aplican transformaciones y validaciones para asegurar calidad y coherencia. Finalmente, la **ACCESS ZONE** ofrece datos listos para el análisis, que alimentan tanto notebooks como bases de datos analíticas.

- 🔍 **Pregunta 1:** Se abordará mediante un cuaderno `.ipynb`, trabajando directamente sobre los datasets ya transformados en la *ACCESS ZONE*.
- 🗃️ **Pregunta 2:** Se resolverá con consultas **SQL** sobre una base de datos **PostgreSQL** que contiene las tablas generadas a partir de los datos limpios.
- 📊 **Pregunta 3:** Se responderá mediante la construcción de **dashboards en Apache Superset**, conectados al **Data Warehouse**, con el objetivo de facilitar el análisis visual a perfiles no técnicos como ciudadanos o asociaciones vecinales.

---

##  Modelo de Datos Diseñado

*(Pendiente de documentación)*

---

##  Procesos de Transformación ETL (Extract, Transform, Load)

###  Fase 1: Extracción

Datasets originales:

- `trafico-horario.csv`
- `bicimad-usos.csv`
- `parkings-rotacion.csv` + `ext_aparcamientos_info.csv`
- `dump-bbdd-municipal.sql`
- `avisamadrid.json`

 Suidos a **MinIO** (`raw` zone) mediante `upload_file_to_minio`.

Conversión previa:
- `avisamadrid.json` → CSV con `extract_json_to_dataframe`
- `dump-bbdd-municipal.sql` → varios `.csv` con `extract_sql_to_dataframes`
- Fusión de aparcamientos con `merge`

---

### Fase 2: Transformación

Transformaciones aplicadas:

- Estandarización de formatos
- Eliminación de duplicados
- Conversión de fechas y tipos
- Validaciones: no nulos, unicidad, integridad

 **Ejemplos por dataset**:

- **Tráfico**: limpieza de duplicados, tipado de fechas
- **Bicimad**: validación de `usuario_id`
- **Parkings**: conversión de coordenadas y tarifas
- **Energía**: control de métricas energéticas
- **Edificios/Distritos**: validación de latitudes y antigüedad
- **Zonas verdes**: normalización booleana y categórica
- **Avisamadrid**: integridad mediante claves y fechas

---

### Fase 3: Carga

1. **Clonar el repositorio**  
   ```bash
   git clone https://github.com/HugoFraile7/Practica2_InfBigData
   cd proyecto-madridsostenible


---

## Puesta en Marcha de la Infraestructura

### Arranque con Docker Compose

```bash
docker compose up -d 
```

Crea en docker todos los contenedores necesarios para el desarrollo de la práctica(Conectividad con **MinIO**, **Trino**, **MariaDB**, **PostgreSQL**) además desde un **Dcokerfile** auxiliar instala todas las dependecias necearias.



- `raw-ingestion-zone`
- `clean-zone`
- `process-zone`
- `access-zone`
- `govern-zone-metadata(información de realización de la práctica)`

---

## Flujo por Zonas

### Zona 1: Raw

Carga de datos originales:

```bash
docker exec -it python-client python /scripts/01_ingest_data.py
```

### Zona 2: Clean

Limpieza y normalización de los datos:

```bash
docker exec -it python-client python /scripts/02_clean_data.py
```

### Zona 3: Process

Agregaciones, KPIs, transformaciones para análisis:

```bash
docker exec -it python-client python /scripts/03_access_zone.py
```

---

## Análisis Visual (Pregunta 1)

Cuaderno Jupyter: `notebooks/01_congestion_vehiculos.ipynb`

-En este cuaderno se carga el dataset **trafico.parquet**, y se realizan las visualizaciones pertinentes para responder a la primera cuestión.

---

## Data Warehouse (PostgreSQL)

### 4️ Crear modelo en PostgreSQL
-Se crean las tablas necesarias.
```bash
docker exec -it python-client python /scripts/04_create_datawarehouse.py
```

### 5️ Carga datos
-Se insertan los datos en las tablas previamente creadas en la etapa anterior.
```bash
docker exec -it python-client python /scripts/05_load_warehouse_data.py
```

### Preguntas de Negocio (Task 2)

** 6️ Rutas BiciMAD más populares**

```bash
docker exec -it python-client python /scripts/06_query_bicimad_routes.py
```

** Densidad vs Transporte**

```bash
docker exec -it python-client python /scripts/07_query_demografia_transporte.py
```

---

##  Estructura del Proyecto

```
/scripts
├── 01_ingest_data.py
├── 02_clean_data.py
├── 03_access_zone.py
├── 04_create_datawarehouse.py
├── 05_load_warehouse_data.py
├── 06_query_bicimad_routes.py
├── 07_query_demografia_transporte.py

/notebooks
└── 01_congestion_vehiculos.ipynb
🚀
