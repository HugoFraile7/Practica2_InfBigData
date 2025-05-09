import psycopg2
from sqlalchemy import create_engine

# Paso 1: crear la base de datos si no existe (fuera de cualquier transacción)
print("🔧 Verificando existencia de la base de datos...")

try:
    conn = psycopg2.connect(
        dbname='postgres',
        user='bbdd_postgre',
        password='bbdd_postgre',
        host='bbdd_postgre',
        port='5432'
    )
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'bbdd_postgre'")
        exists = cur.fetchone()
        if not exists:
            cur.execute("CREATE DATABASE bbdd_postgre")
            print("✅ Base de datos 'bbdd_postgre' creada")
        else:
            print("ℹ️  La base de datos 'bbdd_postgre' ya existe")
    conn.close()
except Exception as e:
    print("❌ Error al crear la base de datos:", e)
    raise

# Paso 2: crear tablas dentro de la base ya asegurada
print("📦 Conectando a bbdd_postgre para crear tablas...")

engine = create_engine("postgresql+psycopg2://bbdd_postgre:bbdd_postgre@bbdd_postgre:5432/bbdd_postgre", isolation_level="AUTOCOMMIT")

with engine.connect() as conn:
    conn.exec_driver_sql("""
    -- 🔁 Tablas anteriores
    DROP TABLE IF EXISTS stg_viaje;

    CREATE TABLE IF NOT EXISTS dim_usuario (
      usuario_sk   SERIAL PRIMARY KEY,
      usuario_id   INTEGER NOT NULL UNIQUE,
      tipo_usuario VARCHAR(15) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS dim_estacion (
      estacion_sk  SERIAL PRIMARY KEY,
      estacion_id  INTEGER NOT NULL UNIQUE
    );

    CREATE UNLOGGED TABLE stg_viaje (
      usuario_id            INTEGER,
      tipo_usuario          VARCHAR(15),
      estacion_origen       INTEGER,
      estacion_destino      INTEGER,
      duracion_segundos     INTEGER,
      distancia_km          DECIMAL(8, 2),
      calorias_estimadas    DECIMAL(8, 2),
      co2_evitado_gramos    DECIMAL(8, 2),
      fecha_hora_inicio     TIMESTAMP,
      fecha_hora_fin        TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS fact_viaje (
      viaje_sk            SERIAL PRIMARY KEY,
      usuario_sk          INTEGER    NOT NULL,
      origen_sk           INTEGER    NOT NULL,
      destino_sk          INTEGER    NOT NULL,
      duracion_segundos   INTEGER    NOT NULL,
      distancia_m         INTEGER,
      calorias            INTEGER,
      co2_evitado_g       INTEGER,
      fecha_hora_inicio   TIMESTAMP,
      fecha_hora_fin      TIMESTAMP,
      FOREIGN KEY (usuario_sk) REFERENCES dim_usuario(usuario_sk),
      FOREIGN KEY (origen_sk)  REFERENCES dim_estacion(estacion_sk),
      FOREIGN KEY (destino_sk) REFERENCES dim_estacion(estacion_sk)
    );

    CREATE INDEX IF NOT EXISTS idx_fact_ruta ON fact_viaje(origen_sk, destino_sk);

    -- 🅿️ Tablas nuevas: aparcamientos y distritos

    CREATE TABLE IF NOT EXISTS dim_aparcamiento (
      aparcamiento_id               INTEGER PRIMARY KEY,
      nombre                        TEXT,
      direccion                     TEXT,
      capacidad_total               INTEGER,
      plazas_movilidad_reducida     INTEGER,
      plazas_vehiculos_electricos   INTEGER,
      tarifa_hora_euros             DECIMAL(4,2),
      horario                       TEXT,
      latitud                       DECIMAL(9,6),
      longitud                      DECIMAL(9,6)
    );

    CREATE TABLE IF NOT EXISTS dim_distrito (
      distrito_id           INTEGER PRIMARY KEY,
      nombre                TEXT,
      poblacion             INTEGER,
      superficie_km2        DECIMAL(6,2),
      densidad_poblacion    DECIMAL(10,2),
      codigo_postal         INTEGER,
      latitud               DECIMAL(9,6),
      longitud              DECIMAL(9,6)
    );

    CREATE TABLE IF NOT EXISTS fact_parking_ocupacion (
      ocupacion_sk             SERIAL PRIMARY KEY,
      aparcamiento_id          INTEGER NOT NULL,
      fecha                    DATE NOT NULL,
      hora                     INTEGER NOT NULL,
      porcentaje_ocupacion     DECIMAL(5,2) NOT NULL,
      distrito_id              INTEGER NOT NULL,
      FOREIGN KEY (aparcamiento_id) REFERENCES dim_aparcamiento(aparcamiento_id),
      FOREIGN KEY (distrito_id) REFERENCES dim_distrito(distrito_id)
    );

    CREATE INDEX IF NOT EXISTS idx_fact_parking_fecha ON fact_parking_ocupacion(fecha, hora);
    """)
    print("✅ Todas las tablas (anteriores y nuevas) actualizadas correctamente en bbdd_postgre")