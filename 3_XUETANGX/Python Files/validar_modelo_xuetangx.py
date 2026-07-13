import os
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler 
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_curve, roc_auc_score, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from sqlalchemy import create_engine
from dotenv import load_dotenv

def ejecutar_prediccion_test():
    # 1. ENTORNO Y RUTAS
    ruta_script = os.path.dirname(os.path.abspath(__file__))
    dir_raiz = os.path.dirname(ruta_script)
    
    load_dotenv(dotenv_path=os.path.join(dir_raiz, ".env"))

    usuario = os.getenv("DB_USER")
    contrasena = os.getenv("DB_PASSWORD")
    servidor = os.getenv("DB_HOST")
    puerto = os.getenv("DB_PORT")
    base_datos = os.getenv("DB_NAME")
    
    engine = create_engine(f"mysql+pymysql://{usuario}:{contrasena}@{servidor}:{puerto}/{base_datos}")
    dir_graficos = os.path.join(dir_raiz, "Graficos")
    os.makedirs(dir_graficos, exist_ok=True)

    # 2. EXTRAER Y ESCALAR DATOS DE OULAD (ENTRENAMIENTO MAESTRO)
    print("\n[ML] Extrayendo datos históricos de OULAD para entrenamiento dinámico...")
    query_oulad = """
        SELECT v.id_student, v.date, v.sum_click, i.final_result
        FROM studentvle v
        INNER JOIN studentinfo i ON v.id_student = i.id_student
        WHERE v.date >= 0 AND v.date <= 168
    """
    df_oulad_crudo = pd.read_sql(query_oulad, con=engine)
    
    df_oulad_crudo['semana'] = (df_oulad_crudo['date'] // 7) + 1
    df_oulad_semanal = df_oulad_crudo.groupby(['id_student', 'semana', 'final_result'])['sum_click'].sum().reset_index()
    
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

    features_cols = ['beta_0_intercepto', 'beta_1_pendiente', 'densidad_conexion', 'coef_variacion', 'max_racha_inactividad']
    X_train_raw = df_maestro_oulad[features_cols]
    y_train = df_maestro_oulad['target_alerta']
    
    scaler_train = StandardScaler()
    X_train_scaled = scaler_train.fit_transform(X_train_raw)

    print("[ML] Entrenando el modelo de Alerta Temprana con especificaciones EDA 8...")
    modelo_sat = DecisionTreeClassifier(max_depth=6, min_samples_leaf=50, random_state=42, criterion='gini')
    modelo_sat.fit(X_train_scaled, y_train)

    # 3. CARGA DE METADATOS EXCLUSIVOS DE 'TEST' (XUETANGX)
    print("\nAccediendo a la subcarpeta 'test' para validación ciega...")
    df_truth_test = pd.read_csv(os.path.join(dir_raiz, "test", "truth_test.csv"), names=['enrollment_id', 'dropped_out'], header=None)

    # 4. PROCESAMIENTO EN TIEMPO REAL (CHUNKS)
    path_log_test = os.path.join(dir_raiz, "test", "log_test.csv")
    timestamps_estudiantes = {}
    chunk_size = 200000
    limite_lineas = 1000000  
    lineas_leidas = 0
    
    for chunk in pd.read_csv(path_log_test, chunksize=chunk_size):
        chunk['time'] = pd.to_datetime(chunk['time']).dt.tz_localize(None)
        for en_id, g_log in chunk.groupby('enrollment_id'):
            if en_id not in timestamps_estudiantes:
                timestamps_estudiantes[en_id] = []
            timestamps_estudiantes[en_id].extend(g_log['time'].tolist())
        lineas_leidas += chunk_size
        if lineas_leidas >= limite_lineas: break

    # 5. EXTRACCIÓN CINÉTICA
    datos_test = []
    for en_id, lista_tiempos in timestamps_estudiantes.items():
        if len(lista_tiempos) < 2: continue
        lista_tiempos = sorted(lista_tiempos)
        primer_clic = lista_tiempos[0]
        dias_relativos = [(t - primer_clic).days for t in lista_tiempos]
        dias_validos = [d for d in dias_relativos if 0 <= d <= 30]
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

    df_features_test = pd.DataFrame(datos_test)
    df_eval_final = df_features_test.merge(df_truth_test, on='enrollment_id', how='inner')

    # 6. NORMALIZAR E INFERIR CON EL MODELO MAESTRO MULTIDOMINIO
    print("\n[ML] Escalando características de XuetangX e infiriendo predicciones...")
    X_test_raw = df_eval_final[features_cols]
    y_real = df_eval_final['dropped_out'].values
    
    scaler_test = StandardScaler()
    X_test_scaled = scaler_test.fit_transform(X_test_raw)
    
    y_pred = modelo_sat.predict(X_test_scaled)
    y_scores = modelo_sat.predict_proba(X_test_scaled)[:, 1]

    df_eval_final['prediccion_sat'] = y_pred
    df_eval_final['score_riesgo'] = y_scores

    # 7. CÁLCULO Y CONSOLIDACIÓN DE MÉTRICAS MATRICIALES REALES
    acc = accuracy_score(y_real, y_pred)
    prec = precision_score(y_real, y_pred, zero_division=0)
    rec = recall_score(y_real, y_pred, zero_division=0)
    f1 = f1_score(y_real, y_pred, zero_division=0)
    auc_value = roc_auc_score(y_real, y_scores)
    cm = confusion_matrix(y_real, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    mse_val = mean_squared_error(y_real, y_scores)
    r2_val = r2_score(y_real, y_scores)

    print("\n" + "="*80)
    print(" REPORTE DE RENDIMIENTO EXCLUSIVO - VALIDACIÓN CRUZADA SAT OPTIMIZADO")
    print("="*80)
    print(f"Accuracy: {acc*100:.2f}% | Precision: {prec*100:.2f}% | Recall: {rec*100:.2f}% | F1: {f1*100:.2f}% | AUC: {auc_value:.4f}")
    print("="*80)
    
    # Lógica de guardado unificado sin sobreescritura destructiva
    ruta_csv_metricas = os.path.join(dir_raiz, "CSV Files", "metricas_generales_xuetangx.csv")
    os.makedirs(os.path.dirname(ruta_csv_metricas), exist_ok=True)
    
    nueva_fila = pd.DataFrame([{
        'Algoritmo': 'Modelo Maestro Multidominio (OULAD->XuetangX)', 'Verdaderos_Negativos_TN': tn, 
        'Falsos_Positivos_FP': fp, 'Falsos_Negativos_FN': fn, 'Verdaderos_Positivos_TP': tp, 
        'Precision_Manual': prec, 'Recall_Manual': rec, 'F1_Score_Manual_Basal': f1, 
        'precision_macro': prec, 'recall_macro': rec, 'f1_macro': f1, 'accuracy': acc, 
        'roc_auc': auc_value, 'mse': mse_val, 'r2_score': r2_val
    }])
    
    if os.path.exists(ruta_csv_metricas):
        df_existente = pd.read_csv(ruta_csv_metricas)
        df_existente = df_existente[df_existente['Algoritmo'] != 'Modelo Maestro Multidominio (OULAD->XuetangX)']
        df_consolidado = pd.concat([df_existente, nueva_fila], ignore_index=True)
    else:
        df_consolidado = nueva_fila
        
    df_consolidado.to_csv(ruta_csv_metricas, index=False)
    print(f"[OK] Métricas del Modelo Maestro consolidadas en: {ruta_csv_metricas}")

    # 8. INYECCIÓN A MYSQL
    print(f"Exportando tabla analítica 'tablon_predicciones_test_xuetangx' a MySQL...")
    df_eval_final.to_sql(name='tablon_predicciones_test_xuetangx', con=engine, if_exists='replace', index=False)

    # 9. GRÁFICOS
    timestamp = datetime.now().strftime("%Y%m%dd_%H%M%S")
    plt.clf() 
    fig1 = plt.figure(figsize=(7, 5), dpi=300)
    sns.set_theme(style="white")
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False,
                xticklabels=['Estable (0)', 'ALERTA (1)'],
                yticklabels=['Realidad: Estable (0)', 'Realidad: Alerta (1)'],
                annot_kws={"size": 14, "weight": "bold"})
    plt.title("Matriz de Confusión Final - Modelo Maestro EDA 8\nValidación Cruzada en Cohorte XuetangX", fontsize=12, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(dir_graficos, f"matriz_confusion_test_{timestamp}.png"), dpi=300, bbox_inches='tight')
    plt.close(fig1)

    plt.clf() 
    fig2 = plt.figure(figsize=(7, 6), dpi=300)
    sns.set_theme(style="whitegrid")
    fpr, tpr, _ = roc_curve(y_real, y_scores)
    plt.plot(fpr, tpr, color='darkorange', lw=2.5, label=f'Curva ROC EDA 8 (AUC = {auc_value:.4f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=1.5, linestyle='--', label='Clasificador Aleatorio (AUC = 0.50)')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('Tasa de Falsos Positivos (1 - Especificidad)')
    plt.ylabel('Tasa de Verdaderos Positivos (Sensibilidad)')
    plt.title('Curva ROC - Validación Cruzada Multidominio\nFronteras de Decisión del EDA 8 en XuetangX', fontsize=12, fontweight='bold', pad=15)
    plt.legend(loc="lower right", frameon=True, shadow=True)
    plt.tight_layout()
    plt.savefig(os.path.join(dir_graficos, f"curva_roc_test_{timestamp}.png"), dpi=300, bbox_inches='tight')
    plt.close(fig2)
    print("Gráficos guardados exitosamente en la carpeta 'Graficos'.\n")

if __name__ == "__main__":
    ejecutar_prediccion_test()
