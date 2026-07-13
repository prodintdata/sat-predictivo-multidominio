import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# 1. RUTAS
ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_raiz = os.path.dirname(ruta_actual) if "CONGO Python Files" in ruta_actual else ruta_actual
load_dotenv(dotenv_path=os.path.join(ruta_raiz, ".env"))

def comparar_columnas_tablones():
    # 2. CONEXIÓN A MYSQL
    usuario = os.getenv("DB_USER")
    contrasena = os.getenv("DB_PASSWORD")
    servidor = os.getenv("DB_HOST")
    puerto = os.getenv("DB_PORT")
    base_datos = os.getenv("DB_NAME")
    
    engine = create_engine(f"mysql+pymysql://{usuario}:{contrasena}@{servidor}:{puerto}/{base_datos}")
    print("Conexión establecida con MySQL para auditoría de esquemas.\n")

    # 3. EXTRACCIÓN DE COLUMNAS (Leemos 0 filas para máxima velocidad)
    try:
        columnas_oulad = pd.read_sql("SELECT * FROM tablon_investigacion_oulad LIMIT 0", con=engine).columns.tolist()
    except Exception as e:
        print(f"Error al leer 'tablon_investigacion_oulad': {e}")
        return

    try:
        columnas_congo = pd.read_sql("SELECT * FROM tablon_congo_raw LIMIT 0", con=engine).columns.tolist()
    except Exception as e:
        print(f"Error al leer 'tablon_congo_raw': {e}")
        return

    # 4. ANÁLISIS DE INTERSECCIÓN Y DIFERENCIAS (Teoría de Conjuntos)
    set_oulad = set(columnas_oulad)
    set_congo = set(columnas_congo)

    identicas = sorted(list(set_oulad.intersection(set_congo)))
    solo_oulad = sorted(list(set_oulad.difference(set_congo)))
    solo_congo = sorted(list(set_congo.difference(set_oulad)))

    # 5. REPORTE EN CONSOLA
    print("=======================================================================")
    print("REPORTES DE COMPATIBILIDAD DE VARIABLES (OULAD vs CONGO)")
    print("=======================================================================")
    print(f"Variables en OULAD Original: {len(columnas_oulad)}")
    print(f"Variables en Congo Raw:      {len(columnas_congo)}")
    print("-----------------------------------------------------------------------")
    
    print(f"\nvariables idénticas en ambas tablas ({len(identicas)}):")
    print(identicas if identicas else "Ninguna coincide exactamente en nombre.")

    print(f"\nVariables en OULAD que FALTAN en Congo ({len(solo_oulad)}):")
    print("Estas variables deben ser creadas:")
    for col in solo_oulad:
        print(f" - {col}")

    print(f"\nVariables en Congo que NO EXISTEN en OULAD ({len(solo_congo)}):")
    print("Estas variables reflejan el esquema nativo del experimento del Congo:")
    for col in solo_congo:
        print(f" - {col}")

if __name__ == "__main__":
    comparar_columnas_tablones()