import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# 1. AJUSTE DE RUTAS ROBUSTO
ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_raiz = os.path.dirname(ruta_actual) if "CONGO Python Files" in ruta_actual else ruta_actual
load_dotenv(dotenv_path=os.path.join(ruta_raiz, ".env"))

def transformar_y_homologar_congo():
    # 2. CONEXIÓN A MYSQL
    usuario = os.getenv("DB_USER")
    contrasena = os.getenv("DB_PASSWORD")
    servidor = os.getenv("DB_HOST")
    puerto = os.getenv("DB_PORT")
    base_datos = os.getenv("DB_NAME")
    
    engine = create_engine(f"mysql+pymysql://{usuario}:{contrasena}@{servidor}:{puerto}/{base_datos}")
    print("Conexión establecida con MySQL para la transformación homóloga.")

    # 3. LEER EL TABLÓN EN BRUTO DEL CONGO
    df_raw = pd.read_sql("SELECT * FROM tablon_congo_raw", con=engine)
    print(f"Cargado 'tablon_congo_raw' con {df_raw.shape[0]} registros.")

    # 4. PASO A PASO DE INGENIERÍA DE DATOS

    # A. Renombrar llaves y métricas base que SÍ existen garantizadas
    print("Renombrando variables nativas a nomenclatura OULAD...")
    df_raw.rename(columns={
        'guid_student_id': 'id_student',
        'score_promedio_raw': 'nota_promedio',
        'total_entregas_raw': 'total_evaluaciones_entregadas',
        'forumng': 'clicks_forumng',
        'oucontent': 'clicks_oucontent',
        'page': 'clicks_page',
        'resource': 'clicks_resource',
        'url': 'clicks_url'
    }, inplace=True)

    # B. Crear aproximaciones lógicas para métricas académicas faltantes
    df_raw['nota_maxima'] = df_raw['nota_promedio']
    df_raw['nota_minima'] = df_raw['nota_promedio']
    df_raw['porcentaje_entregas_a_tiempo'] = 100.0 # Valor estandarizado base

    # C. Calcular mapeos ordinales homologados
    print("Calculando transformaciones ordinales...")
    mapeo_educacion = {
        'No Formal quals': 0, 'Lower Than A Level': 1,
        'A Level or Equivalent': 2, 'HE Qualification': 3,
        'Post Graduate Qualification': 4
    }
    mapeo_edad = {'0-35': 0, '35-55': 1, '55<=': 2}
    mapeo_imd = {
        'Unknown': 0, '0-10%': 1, '10-20%': 2, '20-30%': 3, '30-40%': 4, 
        '40-50%': 5, '50-60%': 6, '60-70%': 7, '70-80%': 8, '80-90%': 9, '90-100%': 10
    }
    mapeo_resultado = {'Withdrawn': 0, 'Fail': 1, 'Pass': 2, 'Distinction': 3}
    mapeo_genero = {'M': 0, 'F': 1}
    mapeo_discapacidad = {'N': 0, 'Y': 1}

    df_raw['education_ordinal'] = df_raw['highest_education'].map(mapeo_educacion).fillna(0).astype(int)
    df_raw['age_band_ordinal'] = df_raw['age_band'].map(mapeo_edad).fillna(0).astype(int)
    df_raw['imd_band_ordinal'] = df_raw['imd_band'].str.strip().map(mapeo_imd).fillna(0).astype(int)
    df_raw['final_result_ordinal'] = df_raw['final_result'].map(mapeo_resultado).fillna(0).astype(int)
    df_raw['gender_encoded'] = df_raw['gender'].map(mapeo_genero).fillna(0).astype(int)
    df_raw['disability_encoded'] = df_raw['disability'].map(mapeo_discapacidad).fillna(0).astype(int)

    # D. Calcular el volumen total de clicks interactivos reales presentes
    columnas_clicks_reales = [c for c in df_raw.columns if c.startswith('clicks_')]
    df_raw['total_clicks_plataforma'] = df_raw[columnas_clicks_reales].sum(axis=1)

    # E. Traer la estructura maestra del OULAD original para inyectar lo faltante de forma dinámica
    print("Alineando e inyectando variables faltantes dinámicamente...")
    columnas_oulad_master = pd.read_sql("SELECT * FROM tablon_investigacion_oulad LIMIT 0", con=engine).columns.tolist()
    
    # Recorrer las 44 columnas deseadas. Si no existen en el dataframe actual, se crean con 0
    for col in columnas_oulad_master:
        if col not in df_raw.columns:
            df_raw[col] = 0

    # F. Reordenar de forma exacta según el patrón maestro de OULAD
    df_congo_final = df_raw[columnas_oulad_master]

    # 5. GUARDAR TABLÓN HOMOLOGADO EN MYSQL
    nombre_tabla_destino = "tablon_investigacion_congo"
    with engine.begin() as con:
        con.execute(text(f"DROP TABLE IF EXISTS {nombre_tabla_destino};"))
        
    print(f"Guardando tablón definitivo en MySQL: '{nombre_tabla_destino}'...")
    df_congo_final.to_sql(nombre_tabla_destino, con=engine, if_exists="replace", index=False)
    print(f"'{nombre_tabla_destino}' creado con {df_congo_final.shape[0]} filas y {df_congo_final.shape[1]} columnas.")

if __name__ == "__main__":
    transformar_y_homologar_congo()