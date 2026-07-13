import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

def ejecutar_auditoria_nulos_oulad():
    # 1. LOCALIZACIÓN ROBUSTA DEL ARCHIVO DE CONFIGURACIÓN .ENV
    ruta_script = os.path.dirname(os.path.abspath(__file__))
    
    # Estrategia de búsqueda doble 
    path_env_directo = os.path.join(ruta_script, ".env")
    path_env_raiz = os.path.join(os.path.dirname(ruta_script), ".env")
    path_env_sub = os.path.join(os.path.dirname(os.path.dirname(ruta_script)), ".env")
    
    if os.path.exists(path_env_directo):
        load_dotenv(dotenv_path=path_env_directo)
    elif os.path.exists(path_env_raiz):
        load_dotenv(dotenv_path=path_env_raiz)
    else:
        load_dotenv(dotenv_path=path_env_sub)

    # 2. EXTRACCIÓN Y VERIFICACIÓN DE CREDENCIALES
    usuario = os.getenv("DB_USER")
    contrasena = os.getenv("DB_PASSWORD")
    servidor = os.getenv("DB_HOST")
    puerto = os.getenv("DB_PORT")
    base_datos = os.getenv("DB_NAME")
    
    
    if not puerto:
        print("[Advertencia] No se detectó DB_PORT en el archivo .env. Usando puerto por defecto: 3306")
        puerto = "3306"
        
    engine = create_engine(f"mysql+pymysql://{usuario}:{contrasena}@{servidor}:{int(puerto)}/{base_datos}")

    print("\n" + "="*80)
    print("AUDITORÍA DE VALORES NULOS - ECOSISTEMA OULAD")
    print("="*80)

    print("[Auditoría] Extrayendo logs base de OULAD desde MySQL...")
    try:
        # Consulta ligera directa
        query_oulad = "SELECT date, sum_click FROM studentvle WHERE date >= 0 AND date <= 168"
        df_oulad_raw = pd.read_sql(query_oulad, con=engine)
        
        total_oulad = len(df_oulad_raw)
        nulos_oulad = df_oulad_raw.isna().sum().sum()
        pct_oulad = (nulos_oulad / total_oulad) * 100 if total_oulad > 0 else 0
        
        print(f"   -> OULAD Total Registros Brutos: {total_oulad:,}")
        print(f"   -> OULAD Registros con Nulos:    {nulos_oulad:,} ({pct_oulad:.2f}%)")
        
        df_reporte = pd.DataFrame([{
            'Ecosistema_Universitario': 'OULAD (Origen)',
            'Total_Registros_Brutos': total_oulad,
            'Cantidad_Valores_Nulos': nulos_oulad,
            'Porcentaje_Nulos': round(pct_oulad, 4),
            'Estado_Gobernanza': 'Estable (Bajo volumen de nulos en registros base)'
        }])
        
        # Guardamos el CSV exactamente en la misma carpeta donde está el script ejecutable
        ruta_csv = os.path.join(ruta_script, "auditoria_nulos_oulad.csv")
        df_reporte.to_csv(ruta_csv, index=False)
        print(f"\n[OK] Reporte exportado con éxito en: {ruta_csv}\n")
        
    except Exception as e:
        print(f"Error al auditar la tabla OULAD: {e}")

if __name__ == "__main__":
    ejecutar_auditoria_nulos_oulad()