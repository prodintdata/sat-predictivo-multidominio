import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

def ejecutar_auditoria_nulos_xuetangx():
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
    
    # Control de seguridad: Si no lee el puerto, asignamos el predeterminado de MySQL
    if not puerto:
        print("[Advertencia] No se detectó DB_PORT en el archivo .env. Usando puerto por defecto: 3306")
        puerto = "3306"
    
    engine = create_engine(f"mysql+pymysql://{usuario}:{contrasena}@{servidor}:{int(puerto)}/{base_datos}")

    features_cols = ['beta_0_intercepto', 'beta_1_pendiente', 'densidad_conexion', 'coef_variacion', 'max_racha_inactividad']

    print("\n" + "="*80)
    print("AUDITORÍA DE VALORES NULOS - ECOSISTEMA XUETANGX")
    print("="*80)

    print("[Auditoría] Cargando tablón analítico de XuetangX desde MySQL...")
    try:
        df_xu_raw = pd.read_sql("SELECT * FROM tablon_validacion_xuetangx", con=engine)
        total_xu = len(df_xu_raw)
        
        filas_con_nulos = df_xu_raw[features_cols + ['dropped_out']].isna().any(axis=1).sum()
        pct_xu = (filas_con_nulos / total_xu) * 100 if total_xu > 0 else 0
        
        print(f"   -> XuetangX Total Registros:       {total_xu:,}")
        print(f"   -> XuetangX Filas con algún Nulo:  {filas_con_nulos:,} ({pct_xu:.2f}%)")
        
        print("\n      Desglose específico por característica cinética:")
        for col in features_cols + ['dropped_out']:
            nulos_col = df_xu_raw[col].isna().sum()
            print(f"         - {col.ljust(25)}: {nulos_col:,} nulos")
            
        df_reporte = pd.DataFrame([{
            'Ecosistema_Universitario': 'XuetangX (Validación)',
            'Total_Registros_Brutos': total_xu,
            'Cantidad_Valores_Nulos': filas_con_nulos,
            'Porcentaje_Nulos': round(pct_xu, 4),
            'Estado_Gobernanza': 'Filtrado Requerido (Casos sin interacciones para OLS)'
        }])
        
        # Guardar el CSV exactamente en la misma carpeta donde está el script ejecutable
        ruta_csv = os.path.join(ruta_script, "auditoria_nulos_xuetangx.csv")
        df_reporte.to_csv(ruta_csv, index=False)
        print(f"\n[OK] Reporte exportado con éxito en: {ruta_csv}\n")
        
    except Exception as e:
        print(f"Error al auditar el tablón de XuetangX: {e}")

if __name__ == "__main__":
    ejecutar_auditoria_nulos_xuetangx()