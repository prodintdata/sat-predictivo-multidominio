import os
import subprocess
import sys
import time

def ejecutar_script(nombre_script, ruta_absoluta):
    """Ejecuta un script de Python en un subproceso usando el intérprete actual."""
    print(f"\n[Pipeline] Ejecutando: {nombre_script}...")
    inicio = time.time()
    
    # Se ejecuta usando el mismo intérprete de Python activo (el venv actual)
    resultado = subprocess.run([sys.executable, ruta_absoluta], capture_output=False, text=True)
    
    duracion = time.time() - inicio
    if resultado.returncode == 0:
        print(f"[OK] {nombre_script} finalizado con éxito en {duracion:.2f} segundos.")
        return True
    else:
        print(f"[ERROR] {nombre_script} falló con código de salida {resultado.returncode}.")
        return False

def orquestar_pipeline_xuetangx():
    # 1. Rutas del entorno
    ruta_actual = os.path.dirname(os.path.abspath(__file__))
    
    # Mapeo de los scripts en la carpeta Python Files
    carpeta_scripts = os.path.join(ruta_actual, "Python Files")
    
    scripts_pipeline = [
        {"nombre": "Auditoría de Valores Nulos", "archivo": "auditoria_nulos_xuetangx.py"},
        {"nombre": "Clasificador Random Forest", "archivo": "validar_modelo_xuetangx_rf.py"},
        {"nombre": "Clasificador Regresión Logística", "archivo": "validar_modelo_xuetangx_lr.py"},
        {"nombre": "Validador Multimodelo y Reporte Final", "archivo": "validar_modelo_xuetangx_2.py"}
    ]

    print("="*80)
    print("ORQUESTRADOR AUTOMÁTICO - PIPELINE EVALUACIÓN XUETANGX")
    print("="*80)
    print(f"Intérprete Python en uso: {sys.executable}")
    print(f"Directorio base: {ruta_actual}\n")

    exitos = 0
    for idx, script in enumerate(scripts_pipeline, start=1):
        ruta_script = os.path.join(carpeta_scripts, script["archivo"])
        
        # Respaldo por si los scripts están sueltos en la raíz de la carpeta de XuetangX
        if not os.path.exists(ruta_script):
            ruta_script = os.path.join(ruta_actual, script["archivo"])

        if not os.path.exists(ruta_script):
            print(f"[Falta Archivo] No se encontró {script['archivo']} en las rutas analizadas.")
            continue

        print(f"\n[Etapa {idx}/{len(scripts_pipeline)}] {script['nombre']}")
        print("-" * 50)
        
        if ejecutar_script(script["archivo"], ruta_script):
            exitos += 1
        else:
            print("\nSe detuvo la ejecución debido a un fallo crítico.")
            sys.exit(1)

    print("\n" + "="*80)
    print("PIPELINE DE XUETANGX COMPLETADO CON ÉXITO")
    print("="*80)
    print(f" Subprocesos ejecutados correctamente: {exitos}/{len(scripts_pipeline)}")
    print(" Todos los archivos CSV de métricas y predicciones caso a caso han sido actualizados.")
    print("="*80 + "\n")

if __name__ == "__main__":
    orquestar_pipeline_xuetangx()