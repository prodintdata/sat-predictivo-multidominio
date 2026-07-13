import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# 1. RUTAS
ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_raiz = os.path.dirname(ruta_actual) if "CONGO Python Files" in ruta_actual else ruta_actual
load_dotenv(dotenv_path=os.path.join(ruta_raiz, ".env"))

def verificar_esquemas_finales():
    # 2. CONEXIÓN A MYSQL
    usuario = os.getenv("DB_USER")
    contrasena = os.getenv("DB_PASSWORD")
    servidor = os.getenv("DB_HOST")
    puerto = os.getenv("DB_PORT")
    base_datos = os.getenv("DB_NAME")
    
    engine = create_engine(f"mysql+pymysql://{usuario}:{contrasena}@{servidor}:{puerto}/{base_datos}")
    print("Conexión establecida con MySQL para verificación de calidad.")

    # 3. EXTRACCIÓN DE ESQUEMAS FINALES
    try:
        cols_oulad = pd.read_sql("SELECT * FROM tablon_investigacion_oulad LIMIT 0", con=engine).columns.tolist()
        cols_congo = pd.read_sql("SELECT * FROM tablon_investigacion_congo LIMIT 0", con=engine).columns.tolist()
    except Exception as e:
        print(f"Error al leer los tablones finales de la base de datos: {e}")
        return

    print("\n=======================================================================")
    print("REVISION DE ESQUEMAS FINALES ENTRE OULAD Y CONGO")
    print("=======================================================================")
    
    # TEST 1: Cantidad de Variables
    print(f"Cantidad de columnas OULAD Original: {len(cols_oulad)}")
    print(f"Cantidad de columnas CONGO Homologado: {len(cols_congo)}")
    
    if len(cols_oulad) == len(cols_congo):
        print("TEST 1 PASADO: Ambos tablones tienen la misma dimensión de variables.")
    else:
        print("TEST 1 FALLADO: Las dimensiones no coinciden.")

    # TEST 2: Presencia de Nombres (Conjuntos)
    faltantes_en_congo = set(cols_oulad) - set(cols_congo)
    sobrantes_en_congo = set(cols_congo) - set(cols_oulad)

    if len(faltantes_en_congo) == 0 and len(sobrantes_en_congo) == 0:
        print("TEST 2 PASADO: Ambos tablones comparten exactamente los mismos nombres de variables.")
    else:
        print("TEST 2 FALLADO: Hay discrepancias en los nombres.")
        if faltantes_en_congo: print(f"   Faltan en Congo: {faltantes_en_congo}")
        if sobrantes_en_congo: print(f"   Sobran en Congo: {sobrantes_en_congo}")

    # TEST 3: Alineación Secuencial y Posición Exacta
    desalineadas = []
    for i in range(min(len(cols_oulad), len(cols_congo))):
        if cols_oulad[i] != cols_congo[i]:
            desalineadas.append((i, cols_oulad[i], cols_congo[i]))

    if len(desalineadas) == 0 and len(cols_oulad) == len(cols_congo):
        print("TEST 3 PASADO: Orden Secuencial Alineado.")
    else:
        print("TEST 3 FALLADO: Las columnas no están en la misma posición indexada.")
        print("   Primeras posiciones con desalineación encontrada:")
        for pos, col_o, col_c in desalineadas[:3]:
            print(f"   - Posición [{pos}]: Esperaba '{col_o}' pero se encontró '{col_c}'")

    print("=======================================================================")
    if len(cols_oulad) == len(cols_congo) and len(faltantes_en_congo) == 0 and len(desalineadas) == 0:
        print("DATOS ALINEADOS.")
    else:
        print("DATOS NO ALINEADOS: Corregir las inconsistencias de esquema mostradas arriba.")
    print("=======================================================================")

if __name__ == "__main__":
    verificar_esquemas_finales()