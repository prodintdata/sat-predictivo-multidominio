import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# 1. RUTAS
ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_raiz = os.path.dirname(ruta_actual) if "CONGO Python Files" in ruta_actual else ruta_actual
load_dotenv(dotenv_path=os.path.join(ruta_raiz, ".env"))

def crear_tablon_congo_raw():
    # 2. CONEXIÓN A MYSQL
    usuario = os.getenv("DB_USER")
    contrasena = os.getenv("DB_PASSWORD")
    servidor = os.getenv("DB_HOST")
    puerto = os.getenv("DB_PORT")
    base_datos = os.getenv("DB_NAME")
    
    engine = create_engine(f"mysql+pymysql://{usuario}:{contrasena}@{servidor}:{puerto}/{base_datos}")
    print("Conexión establecida con MySQL.")

    # 3. RUTAS DE ARCHIVOS
    archivo_excel = os.path.join(ruta_raiz, "CONGO csv", "AnonymisezData_oulad_context-Kongo-2024.xlsx")
    print(f"Cargando el archivo Excel desde: {archivo_excel}")

    # 4. EXTRACCIÓN EN BRUTO DESDE EL EXCEL
    df_student = pd.read_excel(archivo_excel, sheet_name='StudentInfo')
    df_assess_detail = pd.read_excel(archivo_excel, sheet_name='Assesss_detail')
    df_vle_stream = pd.read_excel(archivo_excel, sheet_name='VLE_clickStream')
    df_vle_modules = pd.read_excel(archivo_excel, sheet_name='Vle_modules')

    print(f"Hojas leídas: StudentInfo ({df_student.shape[0]} filas), Assesss_detail ({df_assess_detail.shape[0]} filas), VLE_clickStream ({df_vle_stream.shape[0]} filas)")

    # 5. PROCESAMIENTO EN BRUTO (Consolidación sin alterar nombres ni mapeos ordinales)
    print("Consolidando interacciones de clicks en bruto...")
    df_vle_joined = pd.merge(df_vle_stream, df_vle_modules[['guid_site_id', 'activity_type']], on='guid_site_id', how='left')
    
    df_clicks_raw = df_vle_joined.pivot_table(
        index='guid_student_id',
        columns='activity_type',
        values='sum_clics',
        aggfunc='sum',
        fill_value=0
    ).reset_index()

    print("Consolidando calificaciones académicas en bruto...")
    df_assess_raw = df_assess_detail.groupby('guid_student_id').agg(
        score_promedio_raw=('score', 'mean'),
        total_entregas_raw=('guid_assess_id', 'count')
    ).reset_index()

    print("Uniendo datos demográficos con métricas interactivas en bruto...")
    tablon_raw = pd.merge(df_student, df_clicks_raw, on='guid_student_id', how='left')
    tablon_raw = pd.merge(tablon_raw, df_assess_raw, on='guid_student_id', how='left')

    # 6. SANITIZACIÓN DE NULOS SELECTIVA (Solución para Pandas 3.0 Strict Dtypes)
    print("Sanitizando nulos en variables numéricas y categóricas...")
    columnas_numericas = tablon_raw.select_dtypes(include=['number']).columns
    tablon_raw[columnas_numericas] = tablon_raw[columnas_numericas].fillna(0)

    columnas_texto = tablon_raw.select_dtypes(include=['object', 'string']).columns
    tablon_raw[columnas_texto] = tablon_raw[columnas_texto].fillna("Unknown")

    # 7. PERSISTENCIA EN MYSQL (Carga del tablon_congo_raw)
    nombre_tabla = "tablon_congo_raw"
    with engine.begin() as con:
        con.execute(text(f"DROP TABLE IF EXISTS {nombre_tabla};"))
        
    print(f"Guardando el tablón en bruto en MySQL bajo el nombre '{nombre_tabla}'...")
    tablon_raw.to_sql(nombre_tabla, con=engine, if_exists="replace", index=False)
    print(f" '{nombre_tabla}' creado con {tablon_raw.shape[0]} filas y {tablon_raw.shape[1]} columnas.")

if __name__ == "__main__":
    crear_tablon_congo_raw()