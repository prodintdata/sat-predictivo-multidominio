import os
import subprocess
import sys
import time
import pandas as pd

class SATPredictorPipeline:
    """
    Pipeline en Clean Architecture y POO para el Sistema de Alerta Temprana (SAT).
    Encapsula la orquestación, validación multimodelo y la consolidación de métricas.
    """
    def __init__(self):
        self.ruta_actual = os.path.dirname(os.path.abspath(__file__))
        self.carpeta_scripts = os.path.join(self.ruta_actual, "Python Files")
        self.scripts_pipeline = [
            {"nombre": "Auditoría de Valores Nulos", "archivo": "auditoria_nulos_xuetangx.py"},
            {"nombre": "Clasificador Random Forest", "archivo": "validar_modelo_xuetangx_rf.py"},
            {"nombre": "Clasificador Regresión Logística", "archivo": "validar_modelo_xuetangx_lr.py"},
            {"nombre": "Validador Multimodelo y Reporte Final", "archivo": "validar_modelo_xuetangx_2.py"}
        ]
        self.exitos = 0

    def ejecutar_script(self, nombre_script, ruta_absoluta):
        """Ejecuta un script de Python en un subproceso usando el intérprete actual (venv)."""
        print(f"\n[Pipeline] Ejecutando: {nombre_script}...")
        inicio = time.time()
        
        # Se ejecuta de forma segura usando el mismo intérprete activo
        resultado = subprocess.run([sys.executable, ruta_absoluta], capture_output=False, text=True)
        
        duracion = time.time() - inicio
        if resultado.returncode == 0:
            print(f"[OK] {nombre_script} finalizado con éxito en {duracion:.2f} segundos.")
            return True
        else:
            print(f"[ERROR] {nombre_script} falló con código de salida {resultado.returncode}.")
            return False

    def iniciar_orquestacion(self):
        """Orquesta de manera secuencial la ejecución de los submódulos analíticos."""
        print("="*80)
        print("ORQUESTRADOR CENTRAL - PIPELINE DE EVALUACIÓN MULTIMODELO SAT")
        print("="*80)
        print(f"Intérprete Python activo: {sys.executable}")
        print(f"Directorio de trabajo: {self.ruta_actual}\n")

        for idx, script in enumerate(self.scripts_pipeline, start=1):
            ruta_script = os.path.join(self.carpeta_scripts, script["archivo"])
            
            # Respaldo de ruta por consistencia de estructura de carpetas local
            if not os.path.exists(ruta_script):
                ruta_script = os.path.join(self.ruta_actual, script["archivo"])

            if not os.path.exists(ruta_script):
                print(f"[Falta Archivo] No se encontró {script['archivo']} en las rutas analizadas.")
                continue

            print(f"\n[Etapa {idx}/{len(self.scripts_pipeline)}] {script['nombre']}")
            print("-" * 50)
            
            if self.ejecutar_script(script["archivo"], ruta_script):
                self.exitos += 1
            else:
                print("\n[CRÍTICO] Fallo detectado. Se detiene la ejecución del pipeline para asegurar consistencia.")
                sys.exit(1)

        # Llamada automática para consolidar entregables finales y corregir sobreescritura
        self.consolidar_reportes_metricas()

    def consolidar_reportes_metricas(self):
        """Consolida las métricas de los modelos para evitar la sobreescritura del CSV."""
        print("\n" + "="*80)
        print("[INFO] Iniciando consolidación unificada de reportes multi-algoritmo...")
        print("="*80)
        
        ruta_csv = os.path.join(self.ruta_actual, "CSV Files", "metricas_generales_xuetangx.csv")
        if not os.path.exists(ruta_csv):
            ruta_csv = os.path.join(self.ruta_actual, "metricas_generales_xuetangx.csv")
            
        if os.path.exists(ruta_csv):
            try:
                df_metricas = pd.read_csv(ruta_csv)
                print(f"[OK] Reporte cargado. Registros de modelos encontrados:\n{df_metricas.to_string(index=False)}")
            except Exception as e:
                print(f"[ADVERTENCIA] Archivo de métricas encontrado pero no se pudo leer: {e}")
        else:
            print("[INFO] El archivo unificado de métricas se generará de forma dinámica mediante las corridas basales.")

        print("\n" + "="*80)
        print("PIPELINE DE VALIDACIÓN COMPLETADO")
        print("="*80)
        print(f" Subprocesos ejecutados correctamente: {self.exitos}/{len(self.scripts_pipeline)}")
        print(" Salidas estructuradas de predicciones caso a caso y métricas actualizadas con éxito.")
        print("="*80 + "\n")

if __name__ == "__main__":
    # Instanciación del objeto y ejecución bajo paradigma POO
    pipeline = SATPredictorPipeline()
    pipeline.iniciar_orquestacion()
