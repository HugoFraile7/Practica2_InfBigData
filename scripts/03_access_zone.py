from utils import (
    download_dataframe_from_minio,
    upload_dataframe_to_minio,
    log_data_transformation
)
import pandas as pd
from scipy.spatial import cKDTree


def process_trafico_for_congestion_analysis():
    """Prepara el dataset de tráfico para análisis de congestión por hora."""
    print("\n⚡ Procesando dataset de tráfico para análisis de congestión...")

    trafico_df = download_dataframe_from_minio(
        'clean-zone', 'trafico/trafico-horario.parquet', format='parquet'
    )

    trafico_df['fecha_hora'] = pd.to_datetime(trafico_df['fecha_hora'], errors='coerce')
    trafico_df['hora'] = trafico_df['fecha_hora'].dt.time


    nivel_congestion_mapping = {
        'Baja': 1,
        'Moderada': 2,
        'Alta': 3,
        'Muy Alta': 4
    }
    trafico_df['nivel_congestion'] = trafico_df['nivel_congestion'].map(nivel_congestion_mapping)

    aggregated = trafico_df.groupby('hora').agg({
        'total_vehiculos': 'sum',
        'coches': 'sum',
        'motos': 'sum',
        'camiones': 'sum',
        'buses': 'sum',
        'velocidad_media_kmh': 'mean',
        'nivel_congestion': 'mean'
    }).reset_index()

    return aggregated



## Cambiar fecha hora
def process_bicimad_for_dw():
    """Prepara el dataset de BiciMAD para el DWH manteniendo las columnas de fecha."""
    print("\n🚴 Procesando dataset de BiciMAD para data warehouse...")

    bicimad_df = download_dataframe_from_minio(
        'clean-zone', 'bicimad/bicimad-usos.parquet', format='parquet'
    )

    # Elimina solo la columna 'id', conserva fechas
    bicimad_df = bicimad_df.drop(columns=['id'], errors='ignore')

    return bicimad_df


def process_parking_with_distritos():
    """Devuelve el dataset de parkings unido a distritos, listo para el DW."""
    print("\n🅿️ Procesando dataset de aparcamientos para data warehouse...")

    df_parking = download_dataframe_from_minio(
        'clean-zone', 'parking/merged-parkings.parquet', format='parquet'
    )
    df_distrito = download_dataframe_from_minio(
        'clean-zone', 'demografia/distritos.parquet', format='parquet'
    )
    df_parking['dia_semana'] = df_parking['fecha'].dt.day_name()
    df_parking.drop(columns=['plazas_ocupadas','plazas_libres'],inplace=True)

    # Coordenadas de los distritos
    distritos_coords = df_distrito[['latitud', 'longitud']].to_numpy()
    distritos_tree = cKDTree(distritos_coords)

    # Coordenadas de los aparcamientos únicos
    aparcamiento_coords = df_parking[['latitud', 'longitud']].to_numpy()

    # Buscar el índice del distrito más cercano
    distancias, indices = distritos_tree.query(aparcamiento_coords)

    # Obtener los distrito_id correspondientes
    distrito_ids = df_distrito.iloc[indices]['id'].values

    # Asignar la columna
    df_parking['distrito_id'] = distrito_ids
    return df_parking
def process_estaciones_for_dw():
    """Prepara el dataset de estaciones eliminando solo la columna ID."""
    print("\n📍 Procesando dataset de estaciones...")
    estaciones_df = download_dataframe_from_minio(
                                                    bucket_name='clean-zone',
                                                    object_name='movilidad/estaciones_transporte.parquet',
                                                    format='parquet') 
                                                
    estaciones_df = estaciones_df.drop(columns=['id'], errors='ignore')
    return estaciones_df


def main():
    # Procesamiento tráfico
    processed_trafico = process_trafico_for_congestion_analysis()
    upload_dataframe_to_minio(
        processed_trafico,
        'access-zone',
        'trafico/trafico_congestion_por_hora.parquet',
        format='parquet',
        metadata={
            'description': 'Congestión agregada por hora en Madrid',
            'purpose': 'Análisis científico del tráfico urbano por hora',
            'source': 'clean-zone/trafico-horario.parquet',
            'aggregation': 'sum/mean por hora del día'
        }
    )
    log_data_transformation(
        'clean-zone', 'trafico/trafico-horario.parquet',
        'access-zone', 'trafico/trafico.parquet',
        'Agregación horaria del tráfico para análisis de congestión'
    )
    print("\n✅ Dataset procesado y cargado en access-zone: trafico_congestion_por_hora.parquet")

    # Procesamiento bicimad
    processed_bicimad = process_bicimad_for_dw()
    upload_dataframe_to_minio(
        processed_bicimad,
        'access-zone',
        'bicimad/bicimad-usos.parquet',
        format='parquet',
        metadata={
            'description': 'Datos de uso de BiciMAD sin columnas ID ni fechas',
            'purpose': 'Carga en Data Warehouse',
            'source': 'clean-zone/bicimad-usos.parquet',
            'transformation': 'Eliminación de columnas: id, fecha_hora_inicio, fecha_hora_fin'
        }
    )
    log_data_transformation(
        'clean-zone', 'bicimad/bicimad-usos.parquet',
        'access-zone', 'bicimad/bicimad-usos.parquet',
        'Eliminación de columnas para carga en Data Warehouse'
    )
    print("\n✅ Dataset BiciMAD limpio subido a access-zone: bicimad-usos.parquet")

    # Procesamiento parkings
    processed_parking = process_parking_with_distritos()
    upload_dataframe_to_minio(
        processed_parking,
        'access-zone',
        'parking/parkings.parquet',
        format='parquet',
        metadata={
            'description': 'Datos de parkings con información de distrito añadida',
            'purpose': 'Carga en Data Warehouse',
            'source': 'clean-zone/parking/merged-parkings.parquet',
            'transformation': 'Asignación de distrito por latitud/longitud redondeadas'
        }
    )
    log_data_transformation(
        'clean-zone', 'parking/merged-parkings.parquet',
        'access-zone', 'parking/merged-parkings.parquet',
        'Join entre parkings y distritos por coordenadas redondeadas'
    )
    print("\n✅ Dataset Parkings limpio subido a access-zone: merged-parkings.parquet")


if __name__ == "__main__":
    main()