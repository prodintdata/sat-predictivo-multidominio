import os
import numpy as np
import pandas as pd
from scipy import stats
from sqlalchemy import create_engine
from dotenv import load_dotenv

def construir_tablon_xuetangx():
    # 1. CARGAR CONFIGURACIÓN
    ruta_script = os.path.dirname(os.path.abspath(__file__))
    dir_raiz = os.path.dirname(ruta_script)
    
    load_dotenv(dotenv_path=os.path.join(dir_raiz, ".env"))

    usuario = os.getenv("DB_USER")
    contrasena = os.getenv("DB_PASSWORD")
    servidor = os.getenv("DB_HOST")
    puerto = os.getenv("DB_PORT")
    base_datos = os.getenv("DB_NAME")
    
    engine = create_engine(f"mysql+pymysql://{usuario}:{contrasena}@{servidor}:{puerto}/{base_datos}")

    print(f"Directorio de scripts: {ruta_script}")
    print(f"Directorio raíz detectado para datos: {dir_raiz}")

    # 2. CARGA DE METADATOS DE ENTRENAMIENTO
    print("Accediendo a la subcarpeta 'train' en el directorio raíz...")
    df_enrollment = pd.read_csv(os.path.join(dir_raiz, "train", "enrollment_train.csv"), names=['enrollment_id', 'username', 'course_id'], header=None)
    df_truth = pd.read_csv(os.path.join(dir_raiz, "train", "truth_train.csv"), names=['enrollment_id', 'dropped_out'], header=None)

    # 3. PROCESAMIENTO POR CHUNKS DE LOG_TRAIN.CSV
    path_log = os.path.join(dir_raiz, "train", "log_train.csv")
    print(f"Leyendo registros cinéticos desde: {path_log}")
    
    # Almacenaremos los timestamps puros por estudiante
    timestamps_estudiantes = {}
    chunk_size = 200000
    limite_lineas = 1000000
    lineas_leidas = 0
    
    for chunk in pd.read_csv(path_log, chunksize=chunk_size):
        chunk['time'] = pd.to_datetime(chunk['time']).dt.tz_localize(None)
        
        for en_id, g_log in chunk.groupby('enrollment_id'):
            if en_id not in timestamps_estudiantes:
                timestamps_estudiantes[en_id] = []
            timestamps_estudiantes[en_id].extend(g_log['time'].tolist())
                
        lineas_leidas += chunk_size
        print(f"   -> {lineas_leidas:,} líneas analizadas...")
        if lineas_leidas >= limite_lineas:
            break

    # 4. EXTRACCIÓN DE LAS 5 VARIABLES CINÉTICAS HOMOLOGADAS
    print("Calculando indicadores cinéticos fundamentales por estudiante...")
    datos_calculados = []
    
    for en_id, lista_tiempos in timestamps_estudiantes.items():
        if len(lista_tiempos) < 2:
            continue
            
        # El día 0 del alumno es su propia primera interacción registrada
        lista_tiempos = sorted(lista_tiempos)
        primer_clic = lista_tiempos[0]
        
        # Calculamos los días relativos en base a su propia línea de tiempo
        dias_relativos = [(t - primer_clic).days for t in lista_tiempos]
        
        # Filtramos la ventana de control estándar (primeros 30 días de actividad del alumno)
        dias_validos = [d for d in dias_relativos if 0 <= d <= 30]
        if len(dias_validos) < 2:
            continue
            
        semanas = [(d // 7) + 1 for d in dias_validos]
        df_sem = pd.Series(semanas).value_counts().reset_index()
        df_sem.columns = ['semana', 'clics']
        
        slope, intercept = 0.0, float(df_sem['clics'].iloc[0])
        mean_c = df_sem['clics'].mean()
        cv = df_sem['clics'].std() / mean_c if (len(df_sem) > 1 and mean_c > 0) else 0.0
        
        if len(df_sem) >= 2:
            slope, intercept, _, _, _ = stats.linregress(df_sem['semana'].values, df_sem['clics'].values)
            
        vec_diario = np.zeros(31)
        for d in dias_validos:
            if d <= 30: 
                vec_diario[d] = 1
                
        rachas, r_act = [], 0
        for f in vec_diario:
            if f == 0: 
                r_act += 1
            else:
                if r_act > 0: rachas.append(r_act)
                r_act = 0
        if r_act > 0: rachas.append(r_act)
        
        densidad = (vec_diario.sum() / 31) * 100
        max_racha = max(rachas) if len(rachas) > 0 else 0
        
        datos_calculados.append({
            'enrollment_id': int(en_id),
            'beta_0_intercepto': float(intercept),
            'beta_1_pendiente': float(slope),
            'densidad_conexion': float(densidad),
            'coef_variacion': float(cv),
            'max_racha_inactividad': float(max_racha)
        })

    # Convertir a DataFrame asegurando consistencia
    if len(datos_calculados) == 0:
        print("Error crítico: El tablón dinámico sigue vacío. Verifica las estructuras de las marcas de tiempo.")
        df_tablon_xuetangx = pd.DataFrame(columns=['enrollment_id', 'beta_0_intercepto', 'beta_1_pendiente', 'densidad_conexion', 'coef_variacion', 'max_racha_inactividad'])
    else:
        df_tablon_xuetangx = pd.DataFrame(datos_calculados)
    
    # 5. INTEGRAR TARGET REAL DE DESERCIÓN
    print("Incorporando etiquetas reales")
    df_final_tablon = df_tablon_xuetangx.merge(df_truth, on='enrollment_id', how='inner')
    
    # 6. INYECCIÓN DIRECTA EN MYSQL
    if not df_final_tablon.empty:
        print(f"Inyectando {len(df_final_tablon):,} registros procesados en la tabla 'tablon_validacion_xuetangx'...")
        df_final_tablon.to_sql(name='tablon_validacion_xuetangx', con=engine, if_exists='replace', index=False)
        print("¡Tablón creado y guardado con éxito en MySQL bajo el nombre 'tablon_validacion_xuetangx'!")
    else:
        print("Error: El tablón final quedó vacío tras el cruce con truth_train.csv.")

if __name__ == "__main__":
    construir_tablon_xuetangx()