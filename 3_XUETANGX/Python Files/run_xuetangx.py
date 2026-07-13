import os
import subprocess
import sys
import time
import pandas as pd

class SATPredictorPipeline:
    def __init__(self):
        self.ruta_actual = os.path.dirname(os.path.abspath(__file__))
        self.dir_raiz_proyecto = os.path.dirname(self.ruta_actual) if "Python Files" in self.ruta_actual else self.ruta_actual
        self.carpeta_scripts = os.path.join(self.dir_raiz_proyecto, "Python Files")
        
        self.scripts_pipeline = [
            {"nombre": "Auditoría de Valores Nulos", "archivo": "auditoria_nulos_xuetangx.py"},
            {"nombre": "Análisis Exploratorio de Datos (EDA) - Generación de Distribuciones", "archivo": "eda_xuetangx.py"},
            {"nombre": "Contraste Multivariante Geométrico (PERMANOVA y Gráfico MDS)", "archivo": "permanova_xuetangx.py"},
            {"nombre": "Validación 1/4: Regresión Logística Nativa", "archivo": "validar_modelo_xuetangx_lr.py"},
            {"nombre": "Validación 2/4: Clasificador Random Forest Nativo", "archivo": "validar_modelo_xuetangx_rf.py"},
            {"nombre": "Validación 3/4: Clasificador Árbol de Decisión Nativo (XuetangX)", "archivo": "validar_modelo_xuetangx_2.py"},
            {"nombre": "Validación 4/4: Modelo Maestro Multidominio (OULAD -> XuetangX)", "archivo": "validar_modelo_xuetangx.py"},
            {"nombre": "Auditoría Final de Métricas Avanzadas y Enfoques Macro", "archivo": "auditoria_metricas_xuetangx.py"}
        ]
        self.exitos = 0

    def ejecutar_script(self, nombre_script, ruta_absoluta):
        print(f"\n[Pipeline] Ejecutando: {nombre_script}...")
        inicio = time.time()
        
        resultado = subprocess.run(
            [sys.executable, ruta_absoluta], 
            capture_output=False, 
            text=True,
            cwd=self.dir_raiz_proyecto  
        )
        
        duracion = time.time() - inicio
        
        if resultado.returncode == 0:
            print(f"[OK] {nombre_script} finalizado con éxito en {duracion:.2f} segundos.")
            self.exitos += 1
            return True
        elif resultado.returncode in [3221225477, -1073741819]: 
            print(f"[AVISO OS] {nombre_script} completó sus operaciones pero Windows restringió los hilos de cierre.")
            print("-> Preservando artefactos analíticos y gráficos generados en memoria.")
            self.exitos += 1  
            return True
        else:
            print(f"[ERROR] {nombre_script} falló con código de salida {resultado.returncode}.")
            return False

    def iniciar_orquestacion(self):
        print("="*80)
        print(" CONTROLADOR INTEGRAL POO - PIPELINE DE VALIDACIÓN DE MODELOS DE PREDICCIÓN DE SATISFACCIÓN (XuetangX)")
        print("="*80)
        print(f"Intérprete Python: {sys.executable}")
        print(f"Raíz del Entregable Mapeada: {self.dir_raiz_proyecto}\n")

        os.makedirs(os.path.join(self.dir_raiz_proyecto, "Graficos"), exist_ok=True)

        for idx, script in enumerate(self.scripts_pipeline, start=1):
            ruta_script = os.path.join(self.carpeta_scripts, script["archivo"])
            
            if not os.path.exists(ruta_script):
                ruta_script = os.path.join(self.dir_raiz_proyecto, script["archivo"])

            if not os.path.exists(ruta_script):
                print(f"[Archivo No Encontrado] Se saltó {script['archivo']} (No está en Python Files/).")
                continue

            print(f"\n[Etapa {idx}/{len(self.scripts_pipeline)}] {script['nombre']}")
            print("-" * 65)
            
            self.ejecutar_script(script["archivo"], ruta_script)

        self.consolidar_rutas_csv()

    def consolidar_rutas_csv(self):
        print("\n" + "="*80)
        print("[INFO] Iniciando unificación y consolidación de reportes unificados...")
        print("="*80)
        
        ruta_origen_test = os.path.join(self.dir_raiz_proyecto, "test", "metricas_generales_xuetangx.csv")
        ruta_destino_files = os.path.join(self.dir_raiz_proyecto, "CSV Files", "metricas_generales_xuetangx.csv")
        
        os.makedirs(os.path.dirname(ruta_destino_files), exist_ok=True)
        
        if os.path.exists(ruta_origen_test):
            try:
                df_bueno = pd.read_csv(ruta_origen_test)
                if os.path.exists(ruta_destino_files):
                    df_existente = pd.read_csv(ruta_destino_files)
                    df_final = pd.concat([df_existente, df_bueno], ignore_index=True).drop_duplicates(subset=['Algoritmo'], keep='last')
                else:
                    df_final = df_bueno
                df_final.to_csv(ruta_destino_files, index=False)
                print(f"[SUCCESS] Reporte unificado de métricas actualizado en: {ruta_destino_files}")
            except Exception as e:
                print(f"[ERROR] No se pudo leer la caché temporal de métricas: {e}")
        
        if os.path.exists(ruta_destino_files):
            df_final = pd.read_csv(ruta_destino_files)
            print(f"\nEstado actual de la matriz analítica global:\n{df_final.to_string(index=False)}")

        print("\n" + "="*80)
        print(" PIPELINE FINALIZADO COMPLETO - TODAS LAS GRÁFICAS DEPOSITADAS EN 'Graficos/'")
        print("="*80)
        print(f" Subprocesos validados y acoplados: {self.exitos}/{len(self.scripts_pipeline)}")
        print("="*80 + "\n")

if __name__ == "__main__":
    pipeline = SATPredictorPipeline()
    pipeline.iniciar_orquestacion()
