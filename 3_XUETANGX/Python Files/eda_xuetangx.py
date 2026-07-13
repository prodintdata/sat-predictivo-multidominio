import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from scipy import stats
from sqlalchemy import create_engine
from dotenv import load_dotenv

def ejecutar_eda_xuetangx():
    # 1. DIRECCIONAMIENTO DE RUTAS (SUBIENDO UN NIVEL DESDE PYTHON FILES)
    ruta_script = os.path.dirname(os.path.abspath(__file__))
    dir_raiz = os.path.dirname(ruta_script)
    
    load_dotenv(dotenv_path=os.path.join(dir_raiz, ".env"))

    usuario = os.getenv("DB_USER")
    contrasena = os.getenv("DB_PASSWORD")
    servidor = os.getenv("DB_HOST")
    puerto = os.getenv("DB_PORT")
    base_datos = os.getenv("DB_NAME")
    
    engine = create_engine(f"mysql+pymysql://{usuario}:{contrasena}@{servidor}:{puerto}/{base_datos}")
    
    # Asegurar la ruta de la carpeta Graficos
    dir_graficos = os.path.join(dir_raiz, "Graficos")
    if not os.path.exists(dir_graficos):
        os.makedirs(dir_graficos)

    # 2. EXTRACCIÓN DEL TABLÓN DE VALIDACIÓN DESDE MYSQL
    print("Descargando datos consolidados desde la tabla 'tablon_validacion_xuetangx'...")
    query = "SELECT * FROM tablon_validacion_xuetangx"
    df = pd.read_sql(query, con=engine)
    
    if df.empty:
        print("Error: La tabla está vacía en MySQL.")
        return

    # Definir las 5 variables cinéticas fundamentales
    variables = [
        'beta_0_intercepto', 
        'beta_1_pendiente', 
        'densidad_conexion', 
        'coef_variacion', 
        'max_racha_inactividad'
    ]

    # 3. CÁLCULO DE ESTADÍSTICOS DESCRIPTIVOS COMPLETO
    print("\nGenerando matriz de estadísticos descriptivos")
    resumen_datos = []
    
    for var in variables:
        datos_var = df[var].dropna()
        
        # Extracción de métricas
        media = datos_var.mean()
        mediana = datos_var.median()
        sesgo = stats.skew(datos_var)
        curtosis = stats.kurtosis(datos_var)  # Curtosis de Fisher (exceso, normal = 0)
        q1 = datos_var.quantile(0.25)
        q2 = datos_var.quantile(0.50)
        q3 = datos_var.quantile(0.75)
        
        resumen_datos.append({
            'Variable': var,
            'Media': media,
            'Mediana': mediana,
            'Sesgo (Skewness)': sesgo,
            'Curtosis': curtosis,
            'Q1 (25%)': q1,
            'Q2 (50%)': q2,
            'Q3 (75%)': q3
        })
        
    df_resumen = pd.DataFrame(resumen_datos).set_index('Variable')
    
    # Mostrar el reporte formateado en consola para tu marco metodológico
    print("\n" + "="*90)
    print("REPORTE ESTADÍSTICO DE ANÁLISIS EXPLORATORIO DE DATOS (EDA) - XUETANGX INTERNACIONAL")
    print("="*90)
    print(df_resumen.to_string(formatters={
        'Media': '{:,.4f}'.format,
        'Mediana': '{:,.4f}'.format,
        'Sesgo (Skewness)': '{:,.4f}'.format,
        'Curtosis': '{:,.4f}'.format,
        'Q1 (25%)': '{:,.4f}'.format,
        'Q2 (50%)': '{:,.4f}'.format,
        'Q3 (75%)': '{:,.4f}'.format
    }))
    print("="*90)

    # 4. GENERACIÓN DE COMPONENTES GRÁFICOS CON TIMESTAMP
    timestamp = datetime.now().strftime("%Y%m%dd_%H%M%S")
    print(f"\nGenerando y exportando visualizaciones")
    
    # Configuración de estilo visual elegante para el sínodo
    sns.set_theme(style="whitegrid")
    
    for var in variables:
        # Creamos una figura compuesta: un panel de 1 fila x 3 columnas para cada variable cinética
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        fig.suptitle(f"Análisis Distribucional Avanzado: {var.upper()}", fontsize=16, fontweight='bold', y=1.02)
        
        # Gráfico 1: Histograma con curva KDE
        sns.histplot(df[var], kde=True, ax=axes[0], color="royalblue", bins=30)
        axes[0].set_title("Histograma de Frecuencia con KDE", fontsize=12)
        axes[0].set_xlabel("Valor Muestral")
        axes[0].set_ylabel("Frecuencia Absoluta")
        
        # Gráfico 2: Boxplot (Diagrama de Caja y Bigotes)
        sns.boxplot(y=df[var], ax=axes[1], color="mediumseagreen", width=0.4)
        axes[1].set_title("Boxplot (Detección de Outliers)", fontsize=12)
        axes[1].set_ylabel("Valor Muestral")
        
        # Gráfico 3: Violinplot (Densidad de Probabilidad Kernel)
        sns.violinplot(y=df[var], ax=axes[2], color="gold", width=0.6)
        axes[2].set_title("Violinplot (Densidad de Probabilidad)", fontsize=12)
        axes[2].set_ylabel("Valor Muestral")
        
        plt.tight_layout()
        
        # Construcción del nombre oficial del archivo solicitado
        nombre_archivo = f"{timestamp}_eda_{var}.png"
        ruta_salida = os.path.join(dir_graficos, nombre_archivo)
        
        plt.savefig(ruta_salida, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Guardado exitosamente: Graficos/{nombre_archivo}")
        
    print("\n¡Proceso EDA finalizado de forma exitosa!")

if __name__ == "__main__":
    ejecutar_eda_xuetangx()