import os
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score, 
                             roc_auc_score, mean_squared_error, r2_score, confusion_matrix)
from sqlalchemy import create_engine
from dotenv import load_dotenv

def ejecutar_auditoria_completa():
    # 1. CONFIGURACIÓN DE ENTORNO
    ruta_script = os.path.dirname(os.path.abspath(__file__))
    dir_raiz = os.path.dirname(ruta_script)
    
    load_dotenv(dotenv_path=os.path.join(dir_raiz, ".env"))
    
    usuario = os.getenv("DB_USER")
    contrasena = os.getenv("DB_PASSWORD")
    servidor = os.getenv("DB_HOST")
    puerto = os.getenv("DB_PORT")
    base_datos = os.getenv("DB_NAME")
    
    engine = create_engine(f"mysql+pymysql://{usuario}:{contrasena}@{servidor}:{puerto}/{base_datos}")

    # 2. ENTRENAMIENTO NATIVO CON EL MOTOR ÓPTIMO (REGRESIÓN LOGÍSTICA)
    print("\n[Auditoría] Cargando datos de entrenamiento para ajuste del motor...")
    df_train = pd.read_sql("SELECT * FROM tablon_validacion_xuetangx", con=engine)
    
    features_cols = ['beta_0_intercepto', 'beta_1_pendiente', 'densidad_conexion', 'coef_variacion', 'max_racha_inactividad']
    df_train_clean = df_train.dropna(subset=features_cols + ['dropped_out']).copy()
    
    X_train = df_train_clean[features_cols]
    y_train = df_train_clean['dropped_out'].values
    
    modelo_lr = LogisticRegression(max_iter=1000, random_state=42)
    modelo_lr.fit(X_train, y_train)

    # 3. PROCESAMIENTO DEL CONJUNTO DE TEST (VALIDACIÓN CIEGA)
    print("[Auditoría] Extrayendo logs de XuetangX Test (1M de líneas)...")
    df_truth_test = pd.read_csv(os.path.join(dir_raiz, "test", "truth_test.csv"), names=['enrollment_id', 'dropped_out'], header=None)
    path_log_test = os.path.join(dir_raiz, "test", "log_test.csv")
    
    timestamps_estudiantes = {}
    chunk_size = 200000
    lineas_leidas = 0
    
    for chunk in pd.read_csv(path_log_test, chunksize=chunk_size):
        chunk['time'] = pd.to_datetime(chunk['time']).dt.tz_localize(None)
        for en_id, g_log in chunk.groupby('enrollment_id'):
            if en_id not in timestamps_estudiantes:
                timestamps_estudiantes[en_id] = []
            timestamps_estudiantes[en_id].extend(g_log['time'].tolist())
        lineas_leidas += chunk_size
        if lineas_leidas >= 1000000: break

    # 4. EXTRACCIÓN CINÉTICA DE CARACTERÍSTICAS
    datos_test = []
    for en_id, lista_tiempos in timestamps_estudiantes.items():
        if len(lista_tiempos) < 2: continue
        lista_tiempos = sorted(lista_tiempos)
        primer_clic = lista_tiempos[0]
        dias_validos = [(t - primer_clic).days for t in lista_tiempos if 0 <= (t - primer_clic).days <= 30]
        if len(dias_validos) < 2: continue
            
        semanas = [(d // 7) + 1 for d in dias_validos]
        df_sem = pd.Series(semanas).value_counts().reset_index()
        df_sem.columns = ['semana', 'clics']
        
        slope, intercept = 0.0, float(df_sem['clics'].iloc[0])
        mean_c = df_sem['clics'].mean()
        cv = df_sem['clics'].std() / mean_c if (len(df_sem) > 1 and mean_c > 0) else 0.0
        if len(df_sem) >= 2:
            slope, intercept, _, _, _ = stats.linregress(df_sem['semana'].values, df_sem['clics'].values)
            
        vec_diario = np.zeros(31)
        for d in dias_validos: vec_diario[d] = 1
                
        rachas, r_act = [], 0
        for f in vec_diario:
            if f == 0: r_act += 1
            else:
                if r_act > 0: rachas.append(r_act)
                r_act = 0
        if r_act > 0: rachas.append(r_act)
        
        datos_test.append({
            'enrollment_id': int(en_id), 'beta_0_intercepto': float(intercept), 'beta_1_pendiente': float(slope),
            'densidad_conexion': float((vec_diario.sum() / 31) * 100), 'coef_variacion': float(cv),
            'max_racha_inactividad': float(max(rachas) if len(rachas) > 0 else 0)
        })

    df_eval_final = pd.DataFrame(datos_test).merge(df_truth_test, on='enrollment_id', how='inner')
    
    # 5. INFERENCIA Y DETALLE CASO A CASO
    X_test = df_eval_final[features_cols]
    y_test = df_eval_final['dropped_out'].values
    
    y_pred = modelo_lr.predict(X_test)
    y_prob = modelo_lr.predict_proba(X_test)[:, 1]

    # 6. EXPORTACIÓN DEL ARCHIVO CSV CASO A CASO
    df_salida_caso = pd.DataFrame({
        'enrollment_id': df_eval_final['enrollment_id'],
        'y_test_real': y_test,
        'y_pred_modelo': y_pred,
        'probabilidad_desercion': y_prob
    })
    
    ruta_csv_salida = os.path.join(dir_raiz, "test", "predicciones_caso_a_caso_auditoria.csv")
    df_salida_caso.to_csv(ruta_csv_salida, index=False)
    print(f"\n[OK] Archivo caso a caso exportado con éxito en: {ruta_csv_salida}")

    # ======================================================================
    # 7. CÁLCULOS MATRICIALES MANUALES Y RELATIVOS (REQUERIMIENTO PROFESOR)
    # ======================================================================
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
    
    # Cálculo manual paso a paso de métricas basales
    precision_manual = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall_manual = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1_manual = 2 * (precision_manual * recall_manual) / (precision_manual + recall_manual) if (precision_manual + recall_manual) > 0 else 0

    # Métricas Relativas avanzadas solicitadas por la rúbrica
    p_macro = precision_score(y_test, y_pred, average='macro')
    r_macro = recall_score(y_test, y_pred, average='macro')
    f1_mac = f1_score(y_test, y_pred, average='macro')
    acc = accuracy_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_prob)
    
    # Indicadores de varianza y error de regresión
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # ======================================================================
    # EXPORTACIÓN DE CSV DE MÉTRICAS GENERALES COMPLETO
    # ======================================================================
    df_metricas_generales = pd.DataFrame([{
        'Algoritmo': 'Regresión Logística Nativa',
        'Entorno_Validacion': 'XuetangX Test',
        'Verdaderos_Negativos_TN': tn,
        'Falsos_Positivos_FP': fp,
        'Falsos_Negativos_FN': fn,
        'Verdaderos_Positivos_TP': tp,
        'Precision_Manual': round(precision_manual, 4),
        'Recall_Manual': round(recall_manual, 4),
        'F1_Score_Manual_Basal': round(f1_manual, 4),
        'precision_macro': round(p_macro, 4),
        'recall_macro': round(r_macro, 4),
        'f1_macro': round(f1_mac, 4),
        'accuracy': round(acc, 4),
        'roc_auc': round(roc_auc, 4),
        'mse': round(mse, 4),
        'r2_score': round(r2, 4)
    }])
    
    ruta_csv_metricas = os.path.join(dir_raiz, "test", "metricas_generales_xuetangx.csv")
    df_metricas_generales.to_csv(ruta_csv_metricas, index=False)
    print(f"[OK] Archivo de métricas generales exportado en: {ruta_csv_metricas}")

    # 8. IMPRESIÓN DEL REPORTE FORMAL DE AUDITORÍA
    print("\n" + "="*80)
    print("REPORTE DE AUDITORÍA TÉCNICA Y DESGLOSE MÉTRICO AVANZADO - XUETANGX")
    print("="*80)
    print(f" Matriz de Confusión Desnuda:")
    print(f"    -> TN: {tn}  |  FP: {fp}")
    print(f"    -> FN: {fn}  |  TP: {tp}\n")
    print(f" Cálculo Manual Basal Step-by-Step:")
    print(f"    -> Precisión Calculada Manual: {precision_manual*100:.2f}%")
    print(f"    -> Recall Calculada Manual: {recall_manual*100:.2f}%")
    print(f"    -> F1-Score Calculado Manual (Basal): {f1_manual*100:.2f}%\n")
    print(f" Métricas Relativas y Enfoques Macro solicitados:")
    print(f"    -> ['precision_macro']: {p_macro:.4f}")
    print(f"    -> ['recall_macro']:    {r_macro:.4f}")
    print(f"    -> ['f1_macro']:        {f1_mac:.4f}")
    print(f"    -> ['accuracy']:        {acc*100:.2f}%")
    print(f"    -> ['roc_auc']:         {roc_auc:.4f}\n")
    print(f" Métricas de Varianza y Error de Regresión en Targets Binarios:")
    print(f"    -> MSE (Mean Squared Error):  {mse:.4f}")
    print(f"    -> R2 Score (Coef. Determ.):   {r2:.4f}")
    print("="*80 + "\n")

if __name__ == "__main__":
    ejecutar_auditoria_completa()