# 🏙️ Práctica Madrid Sostenible - Infraestructura de Almacenamiento para la Ciudad Inteligente

Este repositorio contiene la infraestructura y scripts necesarios para construir un **Data Lakehouse** que integra datos públicos de movilidad, urbanismo, medioambiente, energía y participación ciudadana para el análisis y la toma de decisiones sostenibles en Madrid.

## 📊 Diagrama de Infraestructura

![Arquitectura del Data Lake y Data Warehouse](diagrama_infraestructura.png)

La infraestructura combina un **Data Lake multicapa** y un **Data Warehouse dimensional**, estructurado en zonas:

- **RAW ZONE**: Almacena datos originales.
- **CLEAN ZONE**: Contiene datos transformados y validados.
- **ACCESS ZONE**: Proporciona datos listos para análisis y visualización.

📌 **Casos de uso**:

- **Pregunta 1**: Cuaderno Jupyter con análisis visual desde ACCESS ZONE.
- **Pregunta 2**: Consultas SQL en PostgreSQL sobre datos limpios.
- **Pregunta 3**: Dashboards en **Apache Superset** para análisis visual ciudadano.

---

## 🧩 Modelo de Datos Diseñado

*(Pendiente de documentación)*

---

## 🔄 Procesos de Transformación ETL (Extract, Transform, Load)

### 🟠 Fase 1: Extracción

Datasets originales:

- `trafico-horario.csv`
- `bicimad-usos.csv`
- `parkings-rotacion.csv` + `ext_aparcamientos_info.csv`
- `dump-bbdd-municipal.sql`
- `avisamadrid.json`

📦 Subidos a **MinIO** (`raw` zone) mediante `upload_file_to_minio`.

📄 Conversión previa:
- `avisamadrid.json` → CSV con `extract_json_to_dataframe`
- `dump-bbdd-municipal.sql` → varios `.csv` con `extract_sql_to_dataframes`
- Fusión de aparcamientos con `merge`

---

### 🔵 Fase 2: Transformación

Transformaciones aplicadas:

- Estandarización de formatos
- Eliminación de duplicados
- Conversión de fechas y tipos
- Validaciones: no nulos, unicidad, integridad

📌 **Ejemplos por dataset**:

- **Tráfico**: limpieza de duplicados, tipado de fechas
- **Bicimad**: validación de `usuario_id`
- **Parkings**: conversión de coordenadas y tarifas
- **Energía**: control de métricas energéticas
- **Edificios/Distritos**: validación de latitudes y antigüedad
- **Zonas verdes**: normalización booleana y categórica
- **Avisamadrid**: integridad mediante claves y fechas

---

### 🟢 Fase 3: Carga

*(Detalle en la sección de puesta en marcha)*

---

## ⚙️ Puesta en Marcha de la Infraestructura

### ▶️ Arranque con Docker Compose

```bash
docker compose up -d
```

### 🐍 Dockerfile personalizado (python-client)

Incluye:

- pandas, pyarrow, matplotlib
- minio, mysql-connector-python, trino
- great-expectations, etc.

Conectividad con **MinIO**, **Trino**, **MariaDB**, **PostgreSQL**.

---

## 🪣 Buckets de MinIO

- `raw-ingestion-zone`
- `clean-zone`
- `process-zone`
- `access-zone`
- `govern-zone-metadata`

---

## 🚦 Flujo por Zonas

### 🔁 Zona 1: Raw

Carga de datos originales:

```bash
docker exec -it python-client python /scripts/01_ingest_data.py
```

### 🧹 Zona 2: Clean

Limpieza y validación:

```bash
docker exec -it python-client python /scripts/02_clean_data.py
```

### 🔧 Zona 3: Process

Agregaciones, KPIs, transformaciones para análisis:

```bash
docker exec -it python-client python /scripts/03_access_zone.py
```

---

## 📓 Análisis Visual (Pregunta 1)

Cuaderno Jupyter: `notebooks/01_congestion_vehiculos.ipynb`

- Carga desde: `trafico_congestion_por_hora.parquet`
- Herramientas: pandas, matplotlib
- Solo análisis, sin transformación

---

## 🏢 Data Warehouse (PostgreSQL)

### 4️⃣ Crear modelo en PostgreSQL

```bash
docker exec -it python-client python /scripts/04_create_datawarehouse.py
```

### 5️⃣ Cargar datos limpios

```bash
docker exec -it python-client python /scripts/05_load_warehouse_data.py
```

### ❓ Preguntas de Negocio (Task 2)

**6️⃣ Rutas BiciMAD más populares**

```bash
docker exec -it python-client python /scripts/06_query_bicimad_routes.py
```

**7️⃣ Densidad vs Transporte**

```bash
docker exec -it python-client python /scripts/07_query_demografia_transporte.py
```

---

## 📁 Estructura del Proyecto

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
```

---

## ✅ Comprobación Final

Verifica servicios activos:

```bash
docker compose ps
```

---

¡Listo para trabajar con tu pipeline de datos sostenible en Madrid! 🚀
