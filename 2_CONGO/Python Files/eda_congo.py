import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from dotenv import load_dotenv

# 1. RUTAS
ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_raiz = os.path.dirname(ruta_actual) if "CONGO Python Files" in ruta_actual else ruta_actual
load_dotenv(dotenv_path=os.path.join(ruta_raiz, ".env"))

def calcular_estadisticos_avanzados(df, columnas):
    resumen = df[columnas].describe().loc[['mean', 'min', 'max', 'std']]
    sesgo = df[columnas].skew()
    curtosis = df[columnas].kurt()
    
    df_resumen = resumen.T
    df_resumen['sesgo (skewness)'] = sesgo
    df_resumen['curtosis (kurtosis)'] = curtosis
    return df_resumen

def generar_histograma_clicks(df):
    """
    Genera y guarda el histograma de frecuencias con marca de tiempo 
    dentro de la carpeta dedicada 'GRAFICOS'
    """
    carpeta_graficos = os.path.join(ruta_raiz, "GRAFICOS")
    if not os.path.exists(carpeta_graficos):
        os.makedirs(carpeta_graficos)
        print(f"Carpeta creada automáticamente en: {carpeta_graficos}")

    print("\nGenerando histograma de frecuencias para 'total_clicks_plataforma'...")
    plt.figure(figsize=(9, 5))
    
    # Graficar histograma con línea de densidad (KDE)
    sns.histplot(df['total_clicks_plataforma'], kde=True, color='teal', bins=20, edgecolor='black')
    
    # Personalización del gráfico
    plt.title('Distribución de Frecuencias: Total Clicks Plataforma (Cohorte Kongo)', fontsize=14, pad=15)
    plt.xlabel('Cantidad Total de Clicks', fontsize=11)
    plt.ylabel('Frecuencia (Número de Estudiantes)', fontsize=11)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Generar timestamp con formato seguro (AñoMesDia_HoraMinutoSegundo)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"histograma_clicks_congo_{timestamp}.png"
    ruta_guardado = os.path.join(carpeta_graficos, nombre_archivo)
    
    plt.savefig(ruta_guardado, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"¡Gráfico exportado con éxito en: {ruta_guardado}!")

def analizar_eda_congo():
    # 2. CONEXIÓN A MYSQL
    usuario = os.getenv("DB_USER")
    contrasena = os.getenv("DB_PASSWORD")
    servidor = os.getenv("DB_HOST")
    puerto = os.getenv("DB_PORT")
    base_datos = os.getenv("DB_NAME")
    
    engine = create_engine(f"mysql+pymysql://{usuario}:{contrasena}@{servidor}:{puerto}/{base_datos}")
    print("Conexión establecida con MySQL para Fase 8 EDA (Versión Productiva con Historial).")

    # 3. CARGAR DATOS HOMOLOGADOS DEL CONGO
    df_congo = pd.read_sql("SELECT * FROM tablon_investigacion_congo", con=engine)
    print(f"Datos cargados: {df_congo.shape[0]} estudiantes y {df_congo.shape[1]} variables.")

    print("\n=======================================================================")
    print("DIAGNÓSTICO ESTADÍSTICO AVANZADO - COHORTE KONGO (EDA FASE 8)")
    print("=======================================================================")

    # A. Análisis de Rendimiento Académico Base
    print("\n[Métricas Académicas Homologadas]")
    columnas_academicas = ['nota_promedio', 'total_evaluaciones_entregadas']
    resumen_academico = calcular_estadisticos_avanzados(df_congo, columnas_academicas)
    print(resumen_academico.to_string())

    # B. Análisis de Comportamiento Digital Activo
    print("\n[Métricas de Interacción Digital]")
    columnas_clicks_reales = ['clicks_forumng', 'clicks_oucontent', 'clicks_page', 'clicks_resource', 'clicks_url', 'total_clicks_plataforma']
    resumen_digital = calcular_estadisticos_avanzados(df_congo, columnas_clicks_reales)
    print(resumen_digital.to_string())

    # C. Generar el Histograma solicitado con Timestamp
    generar_histograma_clicks(df_congo)

    # D. Verificación de Distribución de Categorías Críticas
    print("\n[Distribución de Categorías Críticas]")
    print(df_congo['final_result'].value_counts(normalize=True) * 100)

    print("\n=======================================================================")
    print("                      ANALISIS COMPLETADO                                ")
    print("=======================================================================")

if __name__ == "__main__":
    analizar_eda_congo()