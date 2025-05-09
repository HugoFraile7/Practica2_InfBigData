import pandas as pd
from sqlalchemy import create_engine
from psycopg2.extras import execute_values
from utils import download_dataframe_from_minio

# 🔗 Conexión a PostgreSQL
engine = create_engine("postgresql+psycopg2://bbdd_postgre:bbdd_postgre@bbdd_postgre:5432/bbdd_postgre", isolation_level="AUTOCOMMIT")
conn = engine.raw_connection()
cur = conn.cursor()

# --------------------------------------
# 📥 Carga de BiciMAD
# --------------------------------------
print("⏳ Descargando y cargando BiciMAD desde MinIO…")
df_bicimad = download_dataframe_from_minio(
    'access-zone', 'bicimad/bicimad-usos.parquet', format='parquet'
)

# Asegurar que las columnas de fecha sean datetime
df_bicimad['fecha_hora_inicio'] = pd.to_datetime(df_bicimad['fecha_hora_inicio'], errors='coerce')
df_bicimad['fecha_hora_fin'] = pd.to_datetime(df_bicimad['fecha_hora_fin'], errors='coerce')

# 👉 Insertar en tabla staging
execute_values(cur, """
INSERT INTO stg_viaje (
    usuario_id, tipo_usuario, estacion_origen, estacion_destino,
    duracion_segundos, distancia_km, calorias_estimadas,
    co2_evitado_gramos, fecha_hora_inicio, fecha_hora_fin
) VALUES %s;
""", df_bicimad[[
    'usuario_id', 'tipo_usuario', 'estacion_origen', 'estacion_destino',
    'duracion_segundos', 'distancia_km', 'calorias_estimadas',
    'co2_evitado_gramos', 'fecha_hora_inicio', 'fecha_hora_fin'
]].values.tolist())
print("✅ Datos cargados en stg_viaje")

# 👉 Insertar en dimensiones
cur.execute("""
INSERT INTO dim_usuario (usuario_id, tipo_usuario)
SELECT DISTINCT usuario_id, tipo_usuario FROM stg_viaje
ON CONFLICT (usuario_id) DO NOTHING;
""")

cur.execute("""
INSERT INTO dim_estacion (estacion_id)
SELECT DISTINCT estacion_origen FROM stg_viaje
UNION
SELECT DISTINCT estacion_destino FROM stg_viaje
ON CONFLICT (estacion_id) DO NOTHING;
""")

# 👉 Insertar en tabla de hechos
cur.execute("""
INSERT INTO fact_viaje (
  usuario_sk, origen_sk, destino_sk,
  duracion_segundos, distancia_m, calorias, co2_evitado_g,
  fecha_hora_inicio, fecha_hora_fin
)
SELECT
  u.usuario_sk,
  o.estacion_sk,
  d.estacion_sk,
  s.duracion_segundos,
  (s.distancia_km * 1000)::int,
  s.calorias_estimadas::int,
  s.co2_evitado_gramos::int,
  s.fecha_hora_inicio,
  s.fecha_hora_fin
FROM stg_viaje s
JOIN dim_usuario  u ON u.usuario_id  = s.usuario_id
JOIN dim_estacion o ON o.estacion_id = s.estacion_origen
JOIN dim_estacion d ON d.estacion_id = s.estacion_destino;
""")
print("🚴 Datos cargados en fact_viaje correctamente")

# --------------------------------------
# 🅿️ Carga de datos de aparcamientos
# --------------------------------------
print("⏳ Descargando y cargando datos de aparcamientos desde MinIO…")
df_parking = download_dataframe_from_minio(
    'access-zone', 'parking/parkings.parquet', format='parquet'
)

# 👉 Insertar en dim_aparcamiento
execute_values(cur, """
INSERT INTO dim_aparcamiento (
  aparcamiento_id, nombre, direccion, capacidad_total,
  plazas_movilidad_reducida, plazas_vehiculos_electricos,
  tarifa_hora_euros, horario, latitud, longitud
) VALUES %s
ON CONFLICT (aparcamiento_id) DO NOTHING;
""", df_parking[[
    'aparcamiento_id', 'nombre', 'direccion', 'capacidad_total',
    'plazas_movilidad_reducida', 'plazas_vehiculos_electricos',
    'tarifa_hora_euros', 'horario', 'latitud', 'longitud'
]].drop_duplicates().values.tolist())
print("✅ Datos cargados en dim_aparcamiento")

# 👉 Insertar en dim_distrito (si aplica)
execute_values(cur, """
INSERT INTO dim_distrito (
  distrito_id, latitud, longitud
) VALUES %s
ON CONFLICT (distrito_id) DO NOTHING;
""", df_parking[[
    'distrito_id', 'latitud', 'longitud'
]].drop_duplicates().values.tolist())
print("✅ Datos cargados en dim_distrito (parciales)")

# 👉 Insertar en fact_parking_ocupacion
execute_values(cur, """
INSERT INTO fact_parking_ocupacion (
  aparcamiento_id, fecha, hora, porcentaje_ocupacion, distrito_id
) VALUES %s;
""", df_parking[[
    'aparcamiento_id', 'fecha', 'hora', 'porcentaje_ocupacion', 'distrito_id'
]].values.tolist())
print("🅿️ Datos cargados en fact_parking_ocupacion correctamente")

# ✅ Cierre
conn.commit()
cur.close()
conn.close()