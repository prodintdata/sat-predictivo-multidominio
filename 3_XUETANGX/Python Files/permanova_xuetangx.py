import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import MDS
from scipy import stats
from scipy.spatial.distance import pdist, squareform
from skbio.stats.distance import permanova, DistanceMatrix, permdisp

def ejecutar_permanova_xuetangx():
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
    if not os.path.exists(dir_graficos):
        os.makedirs(dir_graficos)

    # 2. CARGAR TABLÓN
    print("Cargando tablón de validación desde MySQL...")
    query = "SELECT * FROM tablon_validacion_xuetangx"
    df = pd.read_sql(query, con=engine)
    
    if df.empty:
        print("Error: La tabla 'tablon_validacion_xuetangx' está vacía.")
        return

    df['Grupo_SAT'] = df['dropped_out'].map({
        1: 'ALERTA: Riesgo/Deserción',
        0: 'Estable / Probable Éxito'
    })

    features = [
        'beta_0_intercepto', 
        'beta_1_pendiente', 
        'densidad_conexion', 
        'coef_variacion', 
        'max_racha_inactividad'
    ]
    
    df_clean = df.dropna(subset=features + ['dropped_out']).copy()
    
    # Para evitar saturar memoria en MDS y PERMANOVA, submuerreamos de forma controlada a 1,000 registros reales
    if len(df_clean) > 1000:
        print(f"Población total recuperada para validación: {len(df_clean)} estudiantes.")
        print("Cohorte muy grande para visualización MDS. Tomando submuestra de 1,000 estudiantes para el gráfico...")
        df_clean = df_clean.sample(n=1000, random_state=42).copy()
    else:
        print(f"Población total recuperada para validación: {len(df_clean)} estudiantes.")

    X = df_clean[features].values
    grupos = df_clean['Grupo_SAT'].values

    # ===========================================================================
    #  FASE 1: AUDITORÍA DE SUPUESTOS PARAMÉTRICOS (DINÁMICA)
    # ===========================================================================
    print("\n===========================================================================")
    print(" FASE 1: AUDITORÍA DE SUPUESTOS PARAMÉTRICOS ")
    print("===========================================================================")
    
    print("\n[A] Evaluando Normalidad (Test Kolmogorov-Smirnov Real):")
    for col in features:
        # Estandarizamos localmente para validar frente a una normal estándar teórica
        valores_est = (df_clean[col] - df_clean[col].mean()) / df_clean[col].std()
        _, p_val = stats.kstest(valores_est, 'norm')
        txt = "ACEPTADA (Es Normal)" if p_val > 0.05 else "RECHAZADA (No es Normal)"
        print(f"  * {col:<25} -> p-value: {p_val:.5e} | Distribución Normal: {txt}")

    print("\n[B] Evaluando Homogeneidad de Varianzas (Test de Levene Real):")
    grupo_alerta = df_clean[df_clean['Grupo_SAT'] == 'ALERTA: Riesgo/Deserción']
    grupo_estable = df_clean[df_clean['Grupo_SAT'] == 'Estable / Probable Éxito']
    
    for col in features:
        vec_alerta = grupo_alerta[col].values
        vec_estable = grupo_estable[col].values
        _, p_val = stats.levene(vec_alerta, vec_estable)
        txt = "ACEPTADA (Homocedástico)" if p_val > 0.05 else "RECHAZADA (Heterocedástico)"
        print(f"  * {col:<25} -> p-value: {p_val:.5e} | Varianzas Iguales: {txt}")

    # 3. NORMALIZACIÓN ESTÁNDAR
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # ===========================================================================
    #  FASE 2: CONTRASTE MULTIVARIANTE GLOBAL (PERMANOVA REAL)
    # ===========================================================================
    print("\n===========================================================================")
    print(" FASE 2: CONTRASTE MULTIVARIANTE GLOBAL (PERMANOVA) ")
    print("===========================================================================")
    print("Calculando matriz de distancias Euclidianas")
    print("Corriendo 9,999 permutaciones aleatorias no paramétricas...")
    
    dist_matrix_raw = squareform(pdist(X_scaled, metric='euclidean'))
    dm = DistanceMatrix(dist_matrix_raw, ids=df_clean['enrollment_id'].astype(str).tolist())
    
    # Ejecutamos PERMANOVA con 9,999 permutaciones sobre tus datos reales
    resultado_permanova = permanova(dm, grouping=grupos, permutations=9999)
    pseudo_f = resultado_permanova['test statistic']
    p_value = resultado_permanova['p-value']
    
    print("\n=== RESULTADOS DEL CONTRASTE GLOBAL ===")
    print(f" Estadístico de Separación (Pseudo-F) : {pseudo_f:.4f}")
    print(f" Valor de Significancia (p-value)    : {p_value:.5e}")
    print(f" Número de Permutaciones Ejecutadas   : 9999")

    # ===========================================================================
    #  FASE CORRELATIVA: AUDITORÍA DE DISPERSIÓN MULTIVARIANTE (PERMDISP REAL)
    # ===========================================================================
    print("\n===========================================================================")
    print(" FASE CORRELATIVA: AUDITORÍA DE DISPERSIÓN MULTIVARIANTE (PERMDISP) ")
    print("===========================================================================")
    
    resultado_permdisp = permdisp(dm, grouping=grupos, permutations=9999)
    f_permdisp = resultado_permdisp['test statistic']
    p_permdisp = resultado_permdisp['p-value']
    
    print(f" Estadístico F de PERMDISP            : {f_permdisp:.4f}")
    print(f" Valor de Significancia (p-value)    : {p_permdisp:.5e}")

    # ===========================================================================
    #  FASE 3: GENERANDO VISUALIZACIÓN DE ESPACIO DE DISTANCIAS (MDS)
    # ===========================================================================
    print("\n===========================================================================")
    print(" FASE 3: GENERANDO VISUALIZACIÓN DE ESPACIO DE DISTANCIAS (MDS) ")
    print("===========================================================================")
    print("Reduciendo las 5 dimensiones a un plano 2D para inspección visual...")
    
    mds = MDS(n_components=2, dissimilarity='precomputed', random_state=42, normalized_stress='auto')
    coords = mds.fit_transform(dist_matrix_raw)
    
    df_coords = pd.DataFrame(coords, columns=['Dim_1', 'Dim_2'])
    df_coords['Grupo'] = grupos
    centroides = df_coords.groupby('Grupo')[['Dim_1', 'Dim_2']].mean().reset_index()

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(12, 7), dpi=300)

    colores = {
        'ALERTA: Riesgo/Deserción': '#e25c5c',
        'Estable / Probable Éxito': '#5cb85c'
    }
    
    colores_centroide = {
        'ALERTA: Riesgo/Deserción': '#c91616',
        'Estable / Probable Éxito': '#208020'
    }

    for grupo, data in df_coords.groupby('Grupo'):
        plt.scatter(data['Dim_1'], data['Dim_2'], label=grupo, color=colores[grupo], alpha=0.7, edgecolors='black', linewidths=0.5, s=60)

    for idx, row in centroides.iterrows():
        plt.scatter(row['Dim_1'], row['Dim_2'], label=f"Centroide: {row['Grupo']}", color=colores_centroide[row['Grupo']], marker='X', s=350, edgecolors='black', linewidths=1.5, zorder=5)

    plt.title("Mapa de Ordenación Multidimensional (MDS) - Cohorte XuetangX\nValidación Geométrica del Perfil Conductual del SAT", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Dimensión Principal 1", fontsize=11, labelpad=8)
    plt.ylabel("Dimensión Principal 2", fontsize=11, labelpad=8)
    
    anotacion_stats = (
        f"Resultados PERMANOVA (9999 perm.):\n"
        f"Pseudo-F: {pseudo_f:.4f}\n"
        f"p-value: {p_value:.4f}\n"
        f"PERMDISP p-value: {p_permdisp:.4f}"
    )
    plt.gca().text(0.02, 0.02, anotacion_stats, transform=plt.gca().transAxes,
                   fontsize=9, fontweight='semibold', bbox=dict(boxstyle="round,pad=0.5", facecolor="whitesmoke", edgecolor="gray", alpha=0.9))

    plt.legend(title="Grupos de Diagnóstico", loc="lower left", frameon=True, facecolor='white', shadow=True)
    plt.tight_layout()

    timestamp = datetime.now().strftime("%Y%m%dd_%H%M%S")
    nombre_archivo = f"permanova_xuetangx_mds_{timestamp}.png"
    ruta_salida = os.path.join(dir_graficos, nombre_archivo)
    
    plt.savefig(ruta_salida, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"¡Gráfico MDS optimizado exportado con éxito en: {ruta_salida}!")
    print("=======================================================================\n")

if __name__ == "__main__":
    ejecutar_permanova_xuetangx()