import os
import numpy as np
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine
from scipy.stats import kstest, levene
from scipy.spatial.distance import pdist, squareform
from sklearn.manifold import MDS
import matplotlib.pyplot as plt
import seaborn as sns
from skbio.stats.distance import permanova, permdisp
from skbio import DistanceMatrix  

def ejecutar_permanova_congo():
    # ==============================================================================
    # 1. CONEXIÓN A LA BASE DE DATOS Y EXTRACCIÓN DEL TABLÓN PREDICTIVO
    # ==============================================================================
    ruta_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_raiz = os.path.dirname(ruta_actual) if "CONGO Python Files" in ruta_actual else ruta_actual
    load_dotenv(dotenv_path=os.path.join(ruta_raiz, ".env"))

    usuario = os.getenv("DB_USER")
    contrasena = os.getenv("DB_PASSWORD")
    servidor = os.getenv("DB_HOST")
    puerto = os.getenv("DB_PORT")
    base_datos = os.getenv("DB_NAME")
    
    engine = create_engine(f"mysql+pymysql://{usuario}:{contrasena}@{servidor}:{puerto}/{base_datos}")
    tabla_origen = "predicciones_congo_sat"
    
    print(f"Conexión exitosa. Extrayendo matriz conductual desde '{tabla_origen}'...")
    df_congo = pd.read_sql(f"SELECT * FROM {tabla_origen}", con=engine)
    print(f"Población del Congo recuperada para validación: {df_congo.shape[0]} estudiantes.")

    # Variables del espacio multidimensional (Las 5 dimensiones cinéticas)
    variables_y = ['beta_0_intercepto', 'beta_1_pendiente', 'densidad_conexion', 'coef_variacion', 'max_racha_inactividad']
    columna_grupo = 'estatus_alerta' 

    # Configuración de rutas para los entregables gráficos
    sns.set_theme(style="whitegrid")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    carpeta_graficos = os.path.join(ruta_raiz, "GRAFICOS")
    if not os.path.exists(carpeta_graficos):
        os.makedirs(carpeta_graficos)

    # ==============================================================================
    # 2. AUDITORÍA ESTADÍSTICA DE SUPUESTOS PARAMÉTRICOS
    # ==============================================================================
    print("\n" + "=" * 75)
    print(" FASE 1: AUDITORÍA DE SUPUESTOS PARAMÉTRICOS (CONGO) ")
    print("=" * 75)

    print("\n[A] Evaluando Normalidad en el Congo (Test Kolmogorov-Smirnov):")
    for var in variables_y:
        datos_estandarizados = (df_congo[var] - df_congo[var].mean()) / df_congo[var].std()
        stat, p_val = kstest(datos_estandarizados, 'norm')
        status = "RECHAZADA (No es Normal)" if p_val < 0.01 else "ACEPTADA (Es Normal)"
        print(f"  * {var:<25} -> p-value: {p_val:.5e} | Distribución Normal: {status}")

    print("\n[B] Evaluando Homogeneidad de Varianzas (Test de Levene):")
    grupos_unicos = df_congo[columna_grupo].unique()
    for var in variables_y:
        listas_grupos = [df_congo[df_congo[columna_grupo] == g][var] for g in grupos_unicos]
        stat, p_val = levene(*listas_grupos)
        status = "RECHAZADA (Heterocedástico)" if p_val < 0.01 else "ACEPTADA (Homocedástico)"
        print(f"  * {var:<25} -> p-value: {p_val:.5e} | Varianzas Iguales: {status}")

    # ==============================================================================
    # 3. CONTRASTE MULTIVARIANTE GLOBAL (PERMANOVA)
    # ==============================================================================
    print("\n" + "=" * 75)
    print(" FASE 2: CONTRASTE MULTIVARIANTE GLOBAL (PERMANOVA CONGO) ")
    print("=" * 75)

    X = df_congo[variables_y].values
    grupos_lista = df_congo[columna_grupo].astype(str).tolist()
    lista_ids = df_congo['guid_student_id'].astype(str).tolist()

    print("Calculando matriz de distancias Euclidianas")
    dist_raw = squareform(pdist(X, metric='euclidean'))
    matriz_distancias = DistanceMatrix(dist_raw, ids=lista_ids)

    print("Corriendo 9,999 permutaciones aleatorias no paramétricas...")
    res_global = permanova(matriz_distancias, grupos_lista, permutations=9999)

    print("\n=== RESULTADOS DEL CONTRASTE GLOBAL ===")
    print(f" Estadístico de Separación (Pseudo-F) : {res_global['test statistic']:.4f}")
    print(f" Valor de Significancia (p-value)    : {res_global['p-value']:.5e}")
    print(f" Número de Permutaciones Ejecutadas   : {res_global['number of permutations']}")

    # ==============================================================================
    # 4. AUDITORÍA DE LA DISPERSIÓN MULTIVARIANTE (PERMDISP)
    # ==============================================================================
    print("\n" + "=" * 75)
    print(" FASE CORRELATIVA: AUDITORÍA DE DISPERSIÓN MULTIVARIANTE (PERMDISP) ")
    print("=" * 75)
    
    res_permdisp = permdisp(matriz_distancias, grupos_lista, permutations=9999)
    print(f" Estadístico F de PERMDISP            : {res_permdisp['test statistic']:.4f}")
    print(f" Valor de Significancia (p-value)    : {res_permdisp['p-value']:.5e}")

    # ==============================================================================
    # 5. GENERACIÓN DEL MAPA DE ORDENACIÓN MULTIDIMENSIONAL (MDS)
    # ==============================================================================
    print("\n" + "=" * 75)
    print(" FASE 3: GENERANDO VISUALIZACIÓN DE ESPACIO DE DISTANCIAS (MDS) ")
    print("=" * 75)
    
    print("Reduciendo las 5 dimensiones a un plano 2D para inspección visual...")
    mds = MDS(n_components=2, dissimilarity='precomputed', random_state=42, n_jobs=-1)
    componentes_2d = mds.fit_transform(dist_raw)

    df_grafico = pd.DataFrame(componentes_2d, columns=['Dimensión 1', 'Dimensión 2'])
    df_grafico['Estatus'] = grupos_lista

   # Paleta de colores ejecutiva para el Congo
    paleta_colores = {'Estable / Probable Éxito': '#2ca02c', 'ALERTA: Riesgo/Deserción': '#d62728'}

    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        x='Dimensión 1', y='Dimensión 2', hue='Estatus', 
        palette=paleta_colores, data=df_grafico, alpha=0.7, s=60, edgecolor='black', linewidth=0.7
    )

    # Calcular y posicionar los centroides geométricos de los perfiles
    for estatus in df_grafico['Estatus'].unique():
        centroide = df_grafico[df_grafico['Estatus'] == estatus][['Dimensión 1', 'Dimensión 2']].mean()
        plt.scatter(
            centroide['Dimensión 1'], centroide['Dimensión 2'], 
            marker='X', s=300, color=paleta_colores[estatus], edgecolor='black', linewidth=1.5,
            label=f'Centroide: {estatus}'
        )

    plt.title("Mapa de Ordenación Multidimensional (MDS) - Cohorte Kongo\nValidación Geométrica del Perfil Conductual del SAT", fontsize=12, pad=15)
    plt.xlabel("Dimensión Principal 1", fontsize=11)
    plt.ylabel("Dimensión Principal 2", fontsize=11)
    
    plt.legend(title="Grupos de Diagnóstico", loc='lower left', frameon=True, shadow=True)
    plt.tight_layout()

    nombre_grafico = f"permanova_congo_mds_{timestamp}.png"
    ruta_guardado = os.path.join(carpeta_graficos, nombre_grafico)
    plt.savefig(ruta_guardado, dpi=300)
    plt.close()
    print(f"¡Gráfico MDS optimizado exportado con éxito en: {ruta_guardado}!")
    print("=======================================================================")

if __name__ == "__main__":
    ejecutar_permanova_congo()