# Sistema de Alerta Temprana (SAT) - Analítica Predictiva Multidominio

Este repositorio contiene la arquitectura de software, los algoritmos de aprendizaje supervisado y las herramientas de gobernanza de datos diseñadas para el despliegue del Sistema de Alerta Temprana (SAT) orientado a la detección preventiva del riesgo de deserción estudiantil.

---

## NOTA IMPORTANTE PARA EL AUDITOR / EVALUADOR

Para facilitar la configuración, el uso correcto del sistema y la reproducción exacta de los experimentos analíticos, **es obligatorio revisar primero el documento guía adjunto en la raíz del proyecto**:

**`Indicaciones del Repositorio sat-predictivo-multidominio.docx`**

### ¿Qué encontrará en ese documento?
*   **Requisitos del Sistema:** Configuración del entorno virtual de Python y dependencias necesarias.
*   **Gestión de Variables de Entorno:** Estructura requerida para el archivo de credenciales seguras `.env`.
*   **Estructura de Directorios:** Explicación del orden y jerarquía de los submódulos del proyecto.
*   **Guía de Ejecución:** El paso a paso detallado con los comandos de consola para ejecutar el pipeline completo y las suites de pruebas unitarias.
*   **Enlaces de Descarga:** Dirección y acceso a los repositorios de datos masivos (Big Data Educativo) requeridos para alimentar los modelos analíticos.

---

## Requisitos Rápidos de Infraestructura

Asegúrese de mantener la consistencia en el directorio local manteniendo los submódulos principales intactos tal como vienen estructurados en el despliegue, y asegure la conectividad local a su motor de base de datos antes de disparar los comandos descritos en el manual de indicaciones.

Para cualquier duda técnica sobre las fases del pipeline o la interpretación de las matrices de confusión y curvas ROC generadas en la carpeta de entregables, remítase íntegramente a las secciones correspondientes del archivo `.docx`.
