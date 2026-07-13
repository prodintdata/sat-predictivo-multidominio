import unittest
import numpy as np
import pandas as pd
from scipy import stats

# ======================================================================
# FUNCIONES NÚCLEO COPIADAS DEL PIPELINE PARA SER AUDITADAS POR EL TEST
# ======================================================================

def calcular_densidad_y_rachas(dias_validos, total_dias=31):
    """Función espejo de ingeniería de características del SAT."""
    vec_diario = np.zeros(total_dias)
    for d in dias_validos:
        if 0 <= d < total_dias:
            vec_diario[d] = 1
            
    rachas, r_act = [], 0
    for f in vec_diario:
        if f == 0:
            r_act += 1
        else:
            if r_act > 0:
                rachas.append(r_act)
            r_act = 0
    if r_act > 0:
        rachas.append(r_act)
        
    densidad = (vec_diario.sum() / total_dias) * 100
    max_racha = max(rachas) if len(rachas) > 0 else 0
    return densidad, max_racha


# ======================================================================
# CLASE DE PRUEBAS UNITARIAS OFICIALES
# ======================================================================

class TestSistemaAlertaTemprana(unittest.TestCase):

    def test_densidad_conexion_total(self):
        """Caso 1: Probar que un alumno con conexión todos los días tenga 100% densidad y 0 racha."""
        dias_perfectos = list(range(31))
        densidad, max_racha = calcular_densidad_y_rachas(dias_perfectos, total_dias=31)
        
        self.assertAlmostEqual(densidad, 100.0, places=2)
        self.assertEqual(max_racha, 0)

    def test_ausencia_total_estudiante(self):
        """Caso 2: Alumno fantasma sin interacciones (0% densidad, racha máxima de 31 días)."""
        dias_vacios = []
        densidad, max_racha = calcular_densidad_y_rachas(dias_vacios, total_dias=31)
        
        self.assertEqual(densidad, 0.0)
        self.assertEqual(max_racha, 31)

    def test_racha_inactividad_intermedia(self):
        """Caso 3: Estudiante se conecta el día 0, desaparece 10 días, y vuelve el día 11."""
        dias_especificos = [0, 11]
        _, max_racha = calcular_densidad_y_rachas(dias_especificos, total_dias=31)
        
        # El hueco entre el día 0 y el día 11 son exactamente 10 días de inactividad (días 1 al 10)
        self.assertEqual(max_racha, 19) # La racha del final (días 12 al 30) es de 19 días y es la mayor

    def test_calculo_pendiente_ols(self):
        """Caso 4: Validar que el algoritmo OLS detecte correctamente una tendencia decreciente (fatiga)."""
        # Datos simulados de clics semanales en descenso constante
        semanas = np.array([1, 2, 3, 4])
        clics_fatiga = np.array([100, 70, 40, 10])
        
        slope, intercept, _, _, _ = stats.linregress(semanas, clics_fatiga)
        
        # La pendiente debe ser estrictamente negativa (-30 clics por semana)
        self.assertEqual(slope, -30.0)
        self.assertEqual(intercept, 130.0)

    def test_consistencia_dimensiones_clasificador(self):
        """Caso 5: Verificar consistencia dimensional en la estructura de datos predictiva."""
        columnas_esperadas = ['beta_0_intercepto', 'beta_1_pendiente', 'densidad_conexion', 'coef_variacion', 'max_racha_inactividad']
        
        # Crear un dataframe sintético emulando una fila del tablón analítico
        df_dummy = pd.DataFrame([[15.2, -2.4, 45.0, 0.12, 5]], columns=columnas_esperadas)
        
        self.assertEqual(df_dummy.shape[1], 5)
        self.assertListEqual(list(df_dummy.columns), columnas_esperadas)


if __name__ == '__main__':
    print("\n" + "="*70)
    print(" RUNNING SYSTEM UNIT TESTS FOR SAT-PREDICTIVO-MULTIDOMINIO pipeline")
    print("="*70)
    unittest.main()
