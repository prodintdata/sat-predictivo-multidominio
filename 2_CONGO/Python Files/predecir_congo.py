import pandas as pd
import numpy as np
import os
from datetime import datetime
from sqlalchemy import create_engine, text
from scipy import stats
from sklearn.tree import DecisionTreeClassifier
from dotenv import load_dotenv

# 1. CONEXIÓN Y RUTAS
ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_raiz = os.path.dirname(ruta_actual) if "CONGO Python Files" in ruta_actual else ruta_actual
load_dotenv(dotenv_path=os.path.join(ruta_raiz, ".env"))

def ejecutar_pipeline_prediccion_congo():
    usuario = os.getenv("DB_USER")
    contrasena = os.getenv("DB_PASSWORD")
    servidor = os.getenv("DB_HOST")
    puerto = os.getenv("DB_PORT")
    base_datos = os.getenv("DB_NAME")
    
    engine = create_engine(f"mysql+pymysql://{usuario}:{contrasena}@{servidor}:{puerto}/{base_datos}")
    print("Conexión establecida con MySQL para Ejecución del SAT-Machine Learning.")

    # ======================================================================
    # PASO 1: EXTRAER Y CALCULAR LAS CARACTERÍSTICAS DE COMPORTAMIENTO DEL KONGO
    # ======================================================================
    print("Procesando historial temporal de la cohorte del Kongo...")
    # Extraemos directamente desde la tabla raw inyectada para calcular las interacciones diarias reales
    query_kongo_stream = "SELECT * FROM tablon_congo_raw" 
    
    # Nota: Como tablon_congo_raw ya consolidó los clicks por estudiante, 
    # traere directamente las hojas originales de clicks interactivos para armar las rachas y OLS de forma fiel.
    # Leere la data directamente desde el Excel del Kongo para procesar su clickstream diario exacto.
    archivo_excel = os.path.join(ruta_raiz, "CONGO csv", "AnonymisezData_oulad_context-Kongo-2024.xlsx")
    df_kongo_stream = pd.read_excel(archivo_excel, sheet_name='VLE_clickStream')
    df_kongo_student = pd.read_excel(archivo_excel, sheet_name='StudentInfo')

    # Ingeniería de Características sobre el Kongo (Ventana temporal homologada)
    df_kongo_stream['semana'] = (df_kongo_stream['date'] // 7) + 1
    df_kongo_semanal = df_kongo_stream.groupby(['guid_student_id', 'semana'])['sum_clics'].sum().reset_index()
    df_kongo_diario = df_kongo_stream.groupby(['guid_student_id'])['date'].nunique().reset_index(name='dias_activos')

    print("Calculando Pendientes OLS, Coeficientes de Variación y Rachas de Inactividad del Kongo...")
    datos_avanzados_kongo = []
    for id_est, grupo_diario in df_kongo_stream.groupby('guid_student_id'):
        dias_activos = sorted(grupo_diario['date'].unique())
        vector_presencia = np.zeros(169)
        # Asegurar límites seguros dentro de la ventana del semestre
        dias_validos = [int(d) for d in dias_activos if 0 <= d <= 168]
        vector_presencia[dias_validos] = 1
        
        rachas_ceros = []
        racha_actual = 0
        for flag in vector_presencia:
            if flag == 0:
                racha_actual += 1
            else:
                if racha_actual > 0: rachas_ceros.append(racha_actual)
                racha_actual = 0
        if racha_actual > 0: rachas_ceros.append(racha_actual)
        max_racha = max(rachas_ceros) if len(rachas_ceros) > 0 else 0
        
        datos_avanzados_kongo.append({
            'guid_student_id': id_est,
            'densidad_conexion': (len(dias_validos) / 169) * 100,
            'max_racha_inactividad': max_racha
        })
    df_av_kongo = pd.DataFrame(datos_avanzados_kongo)

    datos_ols_kongo = []
    for id_est, grupo_sem in df_kongo_semanal.groupby('guid_student_id'):
        if len(grupo_sem) >= 2: # Tolerancia adaptativa para asegurar cálculo en la cohorte Kongo
            slope, intercept, _, _, _ = stats.linregress(grupo_sem['semana'].values, grupo_sem['sum_clics'].values)
        else:
            slope, intercept = 0.0, float(grupo_sem['sum_clics'].sum())
            
        clics = grupo_sem['sum_clics'].values
        mean_clics = np.mean(clics)
        cv = np.std(clics) / mean_clics if mean_clics > 0 else 0
        
        datos_ols_kongo.append({
            'guid_student_id': id_est,
            'beta_0_intercepto': intercept,
            'beta_1_pendiente': slope,
            'coef_variacion': cv
        })
    df_ols_kongo = pd.DataFrame(datos_ols_kongo)
    
    # Combinar características del Kongo
    df_features_kongo = df_ols_kongo.merge(df_av_kongo, on='guid_student_id', how='inner')

    # ======================================================================
    # PASO 2: ENTRENAR EL MODELO MAESTRO USANDO EL COMPORTAMIENTO DE OULAD (FASE 8)
    # ======================================================================
    print("\nExtrayendo datos históricos de OULAD de la Base de Datos para Entrenamiento...")
    query_oulad = """
        SELECT v.id_student, v.date, v.sum_click, i.final_result
        FROM studentvle v
        INNER JOIN studentinfo i ON v.id_student = i.id_student
        WHERE v.date >= 0 AND v.date <= 168
    """
    df_oulad_crudo = pd.read_sql(query_oulad, con=engine)
    
    df_oulad_crudo['semana'] = (df_oulad_crudo['date'] // 7) + 1
    df_oulad_semanal = df_oulad_crudo.groupby(['id_student', 'semana', 'final_result'])['sum_click'].sum().reset_index()
    
    # Replicar Ingeniería de características OULAD de tu script Fase 8
    datos_av_oulad = []
    for id_est, g_diario in df_oulad_crudo.groupby('id_student'):
        dias_activos = sorted(g_diario['date'].unique())
        vec = np.zeros(169)
        dias_v = [int(d) for d in dias_activos if 0 <= d <= 168]
        vec[dias_v] = 1
        rachas = []
        r_act = 0
        for f in vec:
            if f == 0: r_act += 1
            else:
                if r_act > 0: rachas.append(r_act)
                r_act = 0
        if r_act > 0: rachas.append(r_act)
        datos_av_oulad.append({
            'id_student': id_est,
            'densidad_conexion': (len(dias_v) / 169) * 100,
            'max_racha_inactividad': max(rachas) if len(rachas) > 0 else 0
        })
    df_av_oulad = pd.DataFrame(datos_av_oulad)

    datos_ols_oulad = []
    for (id_est, final_res), g_sem in df_oulad_semanal.groupby(['id_student', 'final_result']):
        if len(g_sem) >= 4:
            slope, intercept, _, _, _ = stats.linregress(g_sem['semana'].values, g_sem['sum_click'].values)
            clics = g_sem['sum_click'].values
            mean_c = np.mean(clics)
            cv = np.std(clics) / mean_c if mean_c > 0 else 0
            datos_ols_oulad.append({
                'id_student': id_est, 'final_result': final_res,
                'beta_0_intercepto': intercept, 'beta_1_pendiente': slope, 'coef_variacion': cv
            })
    df_ols_oulad = pd.DataFrame(datos_ols_oulad)
    df_maestro_oulad = df_ols_oulad.merge(df_av_oulad, on='id_student', how='inner')
    
    mapeo_cohortes = {'Pass': 'Exito', 'Distinction': 'Exito', 'Fail': 'Riesgo', 'Withdrawn': 'Desercion'}
    df_maestro_oulad['target_alerta'] = df_maestro_oulad['final_result'].map(mapeo_cohortes).apply(lambda x: 0 if x == 'Exito' else 1)

    # Entrenar Árbol de la Fase 8
    X_train = df_maestro_oulad[['beta_0_intercepto', 'beta_1_pendiente', 'densidad_conexion', 'coef_variacion', 'max_racha_inactividad']]
    y_train = df_maestro_oulad['target_alerta']
    
    print("Entrenando el Clasificador de Alerta Temprana Supervisado...")
    modelo_sat = DecisionTreeClassifier(max_depth=6, min_samples_leaf=50, random_state=42, criterion='gini')
    modelo_sat.fit(X_train, y_train)

    # ======================================================================
    # PASO 3: INFERENCIA PREDICTIVA SOBRE LOS ESTUDIANTES DEL KONGO
    # ======================================================================
    print("\nEjecutando predicción predictiva sobre la cohorte Kongo...")
    X_kongo = df_features_kongo[['beta_0_intercepto', 'beta_1_pendiente', 'densidad_conexion', 'coef_variacion', 'max_racha_inactividad']]
    
    df_features_kongo['prediccion_target'] = modelo_sat.predict(X_kongo)
    df_features_kongo['probabilidad_riesgo'] = modelo_sat.predict_proba(X_kongo)[:, 1]
    df_features_kongo['estatus_alerta'] = df_features_kongo['prediccion_target'].apply(lambda x: "ALERTA: Riesgo/Deserción" if x == 1 else "Estable / Probable Éxito")

    # Integrar datos demográficos nativos para enriquecer el reporte final en MySQL
    df_reporte_final = df_features_kongo.merge(df_kongo_student[['guid_student_id', 'gender', 'highest_education']], on='guid_student_id', how='left')

    # ======================================================================
    # PASO 4: CARGA DE RESULTADOS A MYSQL
    # ======================================================================
    nombre_tabla_salida = "predicciones_congo_sat"
    with engine.begin() as con:
        con.execute(text(f"DROP TABLE IF EXISTS {nombre_tabla_salida};"))
        
    print(f"Guardando reporte predictivo final en MySQL bajo la tabla '{nombre_tabla_salida}'...")
    df_reporte_final.to_sql(nombre_tabla_salida, con=engine, if_exists="replace", index=False)
    
    # Resumen Ejecutivo por Consola
    total_alumnos = df_reporte_final.shape[0]
    alertas = int(df_reporte_final['prediccion_target'].sum())
    estables = total_alumnos - alertas
    
    print("\n======================================================================")
    print("PIPELINE PREDICTIVO COMPLETADO CON ÉXITO")
    print("======================================================================")
    print(f"Total Estudiantes Evaluados (Kongo) : {total_alumnos}")
    print(f"Estudiantes Pronosticados Estables : {estables} ({ (estables/total_alumnos)*100:.2f}%)")
    print(f"Alertas Emitidas (Riesgo Crítico)   : {alertas} ({ (alertas/total_alumnos)*100:.2f}%)")
    print(f"Resultados consolidados físicamente en la tabla MySQL: '{nombre_tabla_salida}'")
    print("======================================================================")

if __name__ == "__main__":
    ejecutar_pipeline_prediccion_congo()