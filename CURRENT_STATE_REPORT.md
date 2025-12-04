# Reporte de Estado del Proyecto: Modelo de Metadatos para Computación Cuántica (QCMetadata v1.1)

## 1. Información General del Proyecto
**Título:** Propuesta de un modelo de metadatos para la gestión de la compilación de circuitos cuánticos en plataformas NISQ.
**Versión del Modelo:** 1.1.0
**Fecha de Reporte:** 26 de Noviembre, 2025
**Repositorio:** [https://github.com/nawels693/model_meta_data](https://github.com/nawels693/model_meta_data)

## 2. Alineación con Objetivos de Tesis

| Objetivo Específico | Implementación en Código |
|---------------------|--------------------------|
| **Diseñar modelo conceptual** | Clases definidas en `model/qc_metadata_model.py` (`DeviceMetadata`, `CircuitMetadata`, `CalibrationData`, `CompilationTrace`, `ExecutionContext`, `ProvenanceRecordLean`). |
| **Implementar prototipo funcional** | Scripts `poc_ibm_cloud.py` y `thesis_experiments.py` que integran Qiskit y backend IBM. |
| **Validación de esquemas** | Integración de `jsonschema` para validar contra `model/schema_qc_metadata_v1.1.json` antes de exportar. |

## 3. Especificación Técnica del Modelo

El modelo sigue una arquitectura de captura de metadatos en 4 fases:

### A. Fase de Diseño (`CircuitMetadata`)
Captura la intención lógica del algoritmo antes de ser compilado.
*   **Atributos Clave:** `circuit_id`, `algorithm_type` (vqe, qaoa), `algorithm_parameters` (ansatz, optimizer), `circuit_qasm` (código abstracto).

### B. Fase de Compilación (`CompilationTrace`)
Es el núcleo de la "Gestión de Compilación". Rastrea cómo el software transforma el circuito lógico en físico.
*   **Atributos Clave:** `compilation_duration_ms`, `compiler_version`, `optimization_metrics` (reducción de profundidad/puertas).
*   **Detalle Fino:** Lista `compilation_passes` que detalla cada paso del transpilador (ej: `Unroll3qOrMore`, `Optimize1qGates`), incluyendo duración y orden.

### C. Fase de Ejecución (`ExecutionContext` y `DeviceMetadata` + `CalibrationData`)
Captura el contexto físico y temporal del momento exacto de la ejecución (crítico para NISQ).
*   **DeviceMetadata:** Describe el hardware (`num_qubits`, `topology`, `noise_characteristics`).
*   **CalibrationData:** Describe la "salud" momentánea del hardware (`t1`, `t2`, `readout_error`, `gate_fidelities`). Incluye `timestamp_captured` y `valid_until` para calcular la frescura de los datos.
*   **ExecutionContext:** Vincula una ejecución específica (`execution_id`) con una traza de compilación (`trace_id`) y los resultados (`counts`). Ahora soporta múltiples ejecuciones por modelo (Array).

### D. Fase de Análisis (`ProvenanceRecordLean`)
Implementa el estándar W3C PROV para garantizar reproducibilidad.
*   **Relaciones:** `wasDerivedFrom` (Circuito compilado derivado de diseño), `used` (Compilación usó calibración X), `wasGeneratedBy` (Resultado generado por ejecución Y).

## 4. Estructura del Código (`/`)

*   **`model/`**:
    *   `qc_metadata_model.py`: Definición de las Data Classes (Python) del modelo. Implementa lógica de validación y serialización JSON.
    *   `schema_qc_metadata_v1.1.json`: Esquema JSON formal para validación estricta.
*   **`cloud_providers.py`**:
    *   Implementa el patrón *Adapter* para abstraer las diferencias entre proveedores (IBM Quantum, AWS Braket, Simuladores).
    *   Maneja la autenticación, obtención de backends, extracción de datos de calibración y ejecución segura (con fallback a simulación local).
*   **`poc_ibm_cloud.py`**:
    *   Script principal de demostración ("Proof of Concept"). Conecta el flujo completo: conecta a IBM, extrae calibración real, compila un circuito VQE, ejecuta (o simula si no hay permisos) y genera el JSON final.
*   **`thesis_experiments.py`**:
    *   Script de generación de evidencia científica. Ejecuta bucles controlados variando parámetros (ej: niveles de optimización 0-3) para generar datasets comparativos (`optimization_analysis.csv`).
*   **`helpers.py`**:
    *   Funciones de utilidad para timestamps ISO-8601, extracción de pases de compilación y construcción de circuitos de prueba.

## 5. Estado Actual y Mejoras Recientes

Se han resuelto varias brechas ("GAPs") identificadas durante el desarrollo:
1.  **[GAP-1] Cardinalidad de Ejecución:** `ExecutionContext` ahora es siempre una lista, permitiendo que un solo modelo capture múltiples "shots" o ejecuciones repetidas.
2.  **[GAP-2] Simulación Realista:** Se completaron los datos de `CalibrationData` con valores dummy realistas cuando se usa un simulador, permitiendo probar el modelo sin gastar créditos de nube.
3.  **[GAP-3] Detalle de Compilación:** Se implementó `extract_compilation_passes` para desglosar la "caja negra" de la transpilación en pasos auditables.
4.  **Compatibilidad Qiskit 1.x:** Se actualizó todo el código para soportar las nuevas primitivas `SamplerV2` y el manejo de sesiones de IBM Runtime, manteniendo retrocompatibilidad con `qiskit-aer`.

## 6. Componentes Auxiliares: Implementación vs. Diagrama

**Nota importante:** Los componentes auxiliares del diagrama (`ProvenanceRelation`, `CompilationPass`) están implementados en el código, pero **no como clases separadas**, sino como **estructuras de datos anidadas** (diccionarios dentro de listas):

*   **`ProvenanceRelation`:** Implementado como `Dict` dentro de `ProvenanceRecordLean.relations: List[Dict[str, Any]]`. Se crea mediante el método `add_relation()`.
*   **`CompilationPass`:** Implementado como `Dict` dentro de `CompilationTrace.compilation_passes: List[Dict[str, Any]]`. Se genera mediante la función `extract_compilation_passes()` en `helpers.py`.
*   **`ProvenanceRecordLean` → `provenance_record`:** Mapeo directo. La clase `ProvenanceRecordLean` se asigna al atributo `provenance_record` en `QCMetadataModel`.

**Razón de diseño:** Esta implementación permite serialización JSON directa y mayor flexibilidad sin overhead de clases adicionales. El modelo conceptual del diagrama sigue siendo válido.

Ver detalles completos en `COMPONENTES_AUXILIARES_CLARIFICACION.md`.

## 7. Próximos Pasos Sugeridos para Tesis
1.  Analizar los datos generados en `outputs/thesis_experiments/optimization_analysis.csv`.
2.  Realizar un experimento de comparación "Simulador vs. Hardware Real" (usando `poc_ibm_cloud.py`).
3.  Redactar el capítulo de validación utilizando los gráficos derivados de estos experimentos.

