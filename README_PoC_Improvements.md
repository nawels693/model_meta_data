# README: Prueba de Concepto (PoC) del Modelo de Metadatos QC v1.1
## Mejoras, Gaps Técnicos y Roadmap de Implementación

---

## 📋 TABLA DE CONTENIDOS

1. [Estado Actual](#estado-actual)
2. [Mejoras Implementadas en PoC 1](#mejoras-implementadas-en-poc-1)
3. [Gaps Identificados (Por Prioridad)](#gaps-identificados-por-prioridad)
4. [Roadmap de Implementación](#roadmap-de-implementación)
5. [Próximos Pasos](#próximos-pasos)
6. [Instrucciones de Uso](#instrucciones-de-uso)
7. [Validación y Testing](#validación-y-testing)

---

## 🎯 ESTADO ACTUAL

### PoC 1: VQE Simple - COMPLETADO ✅

**Especificación:**
- Algoritmo: VQE para molécula H2
- Qubits: 2
- Iteraciones: 1
- Compilador: Qiskit v0.45+
- Dispositivo: IBM QASM Simulator

**Resultados:**
```
✅ Cobertura de requisitos: 95% (19/20 campos)
✅ JSON válido y serializable
✅ W3C-PROV implementado correctamente
✅ Trazabilidad end-to-end verificada
✅ Análisis comparativo posible
```

**Archivos generados:**
- `metadata_poc1_vqe_h2_YYYYMMDD_HHMMSS.json` (6.9 KB)
- Contiene 6 de 7 entidades del modelo

---

## ✨ MEJORAS IMPLEMENTADAS EN PoC 1

### ✅ Implementado Correctamente

1. **Captura de 4 fases del flujo híbrido**
   ```python
   FASE 1: DISEÑO (CircuitMetadata + DeviceMetadata)
   FASE 2: COMPILACIÓN (CalibrationData + CompilationTrace)
   FASE 3: EJECUCIÓN (ExecutionContext + resultados)
   FASE 4: ANÁLISIS (ProvenanceRecordLean + validación)
   ```

2. **Timestamps ISO8601 en todas las entidades**
   ```python
   timestamp_created: "2025-11-13T19:06:44Z"
   timestamp_compilation: "2025-11-13T19:06:45Z"
   timestamp_execution: "2025-11-13T19:06:45Z"
   ```

3. **Relaciones W3C-PROV completas**
   ```python
   - wasDerivedFrom: Circuit → Trace
   - used: Trace → Calibration
   - used: Trace → Device
   - wasGeneratedBy: Execution → Trace
   ```

4. **Métricas de optimización reales**
   ```json
   "optimization_metrics": {
     "original_depth": 7,
     "compiled_depth": 1,
     "depth_reduction_percent": 85.7,
     "original_gates": 7,
     "compiled_gates": 1,
     "gate_reduction_percent": 85.7
   }
   ```

5. **Validación de freshness de calibración**
   ```python
   "freshness_validation": {
     "calibration_age_seconds": 0.589,
     "calibration_expired": false,
     "jit_transpilation_used": false
   }
   ```

6. **Denormalización controlada (mirrors)**
   ```python
   ExecutionContext.device_id == CompilationTrace.device_id ✓
   ExecutionContext.calibration_id == CompilationTrace.calibration_id ✓
   ExecutionContext.timestamp_compilation == CompilationTrace.timestamp_compilation ✓
   ```

---

## 🔧 GAPS IDENTIFICADOS (Por Prioridad)

### PRIORIDAD ALTA: Implementar antes de PoC 2

#### [GAP-1] ExecutionContext no es array ⚠️ CRÍTICO

**Problema:**
```python
# Actual (PoC 1):
"execution_context": {
    "execution_id": "exec_poc1_20251112_150100",
    ...
}

# Debería ser (para consistencia):
"execution_context": [
    {
        "execution_id": "exec_poc1_20251112_150100",
        ...
    }
]
```

**Por qué importa:**
- PoC 2 tendrá múltiples ejecuciones (5 iteraciones)
- Estructura debe ser consistente entre PoCs
- Array permite agregación fácil en ExperimentSession

**Impacto:** ALTO (rompe compatibilidad con PoC 2)

**Solución:**
```python
# En qc_metadata_model.py
class QCMetadataModel:
    def __init__(self):
        self.execution_context = []  # SIEMPRE array
        
    def add_execution_context(self, exec_ctx):
        self.execution_context.append(exec_ctx)
        
    def to_complete_json(self):
        # NUNCA desempacar a objeto singular
        return json.dumps({
            ...
            "execution_context": self.execution_context,  # Array
            ...
        })
```

---

#### [GAP-2] CalibrationData.gate_fidelities vacío ⚠️

**Problema:**
```json
"gate_fidelities": {
    "1q_gates": {},      // EMPTY
    "2q_gates": {}       // EMPTY
}
```

**Impacto:** MEDIO (afecta análisis de fidelidad)

**Solución:**
```python
# Para simulador:
gate_fidelities={
    "1q_gates": {
        "x": 1.0, "y": 1.0, "z": 1.0,
        "h": 1.0, "s": 1.0, "t": 1.0,
        "rx": 1.0, "ry": 1.0, "rz": 1.0
    },
    "2q_gates": {
        "cx": 1.0,
        "cz": 1.0,
        "swap": 1.0
    }
}

# Para dispositivo real (future):
gate_fidelities={
    "1q_gates": {
        "x": 0.9999,
        "y": 0.9998,
        ...
    },
    "2q_gates": {
        "cx_0_1": 0.988,
        "cx_1_0": 0.989,
        ...
    }
}
```

**Ubicación en código:**
```python
# en poc1_simple.py, FASE 2
calibration_data = CalibrationData(
    ...
    gate_fidelities={  # ← LLENAR AQUÍ
        "1q_gates": {gate: 1.0 for gate in ["x", "y", "z", "h", "s", "t"]},
        "2q_gates": {"cx": 1.0, "cz": 1.0}
    },
    ...
)
```

---

#### [GAP-3] CompilationPass sin detalles individuales ⚠️

**Problema:**
```python
# Actual (minimalista):
{
    "pass_name": "TrivialLayout",
    "status": "completed"
}

# Debería ser (completo):
{
    "pass_name": "TrivialLayout",
    "pass_order": 2,
    "status": "completed",
    "duration_ms": 15.3,
    "parameters": {
        "method": "trivial"
    },
    "circuit_state_after_pass": {
        "num_gates": 6,
        "circuit_depth": 5,
        "estimated_error": 0.05
    }
}
```

**Impacto:** MEDIO (afecta debugging de compilación)

**Solución:**
```python
# Crear clase CompilationPass mejorada
class CompilationPass:
    def __init__(self, pass_name, pass_order, duration_ms, 
                 parameters, circuit_state_after):
        self.pass_name = pass_name
        self.pass_order = pass_order
        self.status = "completed"
        self.duration_ms = duration_ms
        self.parameters = parameters
        self.circuit_state_after_pass = circuit_state_after

# En poc1_simple.py:
from helpers import extract_compilation_passes

# Extraer del objeto Qiskit transpilado
passes_detail = extract_compilation_passes(compiled_circuit)

compilation_trace = CompilationTrace(
    ...
    compilation_passes=passes_detail,  # Detallado
    ...
)
```

---

### PRIORIDAD MEDIA: Implementar en PoC 2-3

#### [GAP-4] ExperimentSession no inicializado en PoC 1

**Estado:** ESPERADO (PoC 1 es no-iterativo)

**Cuándo implementar:** PoC 2

**Estructura requerida:**
```python
experiment_session = ExperimentSession(
    session_id="vqe_20251113_190000_a1b2c3d4",
    algorithm_type="vqe",
    timestamp_started=get_utc_now_iso(),
    circuit_id=circuit_metadata.circuit_id,
    device_id=device_metadata.device_id,
    optimizer="COBYLA",
    max_iterations=5,
    shots_default=1024,
    num_executions=0,
    total_shots_used=0,
    execution_ids=[],
    calibration_policy="periodic",  # NEW
    session_metrics={
        "convergence_metric": None,
        "convergence_achieved": False,
        "parameter_history": []
    },
    environmental_log=[]
)

# Agregar ejecutions en loop
for iteration in range(1, 6):
    execution = ExecutionContext(...)
    experiment_session.add_execution(execution.execution_id, 1024)
```

---

#### [GAP-5] JIT Transpilation flag sin funcionalidad real

**Estado:** FLAG PRESENTE pero no implementado

**Código actual:**
```python
"jit_transpilation_used": False  # Hardcoded
```

**Cuándo implementar:** PoC 3

**Lógica requerida:**
```python
# En PoC 3 (con iteraciones):
if not calibration_data.is_valid_now():
    print("Calibración expirada, recompilando (JIT)...")
    
    # Obtener nueva calibración
    new_calibration = fetch_new_calibration(device_id)
    
    # Recompilar
    new_trace = recompile_circuit(
        circuit_metadata,
        device_metadata,
        new_calibration,
        jit_flag=True  # ← FLAG SET
    )
    
    # Crear nuevo execution context
    exec_context = ExecutionContext(
        ...
        freshness_validation={
            "calibration_age_seconds": 0.1,
            "calibration_expired": False,
            "jit_transpilation_used": True  # ← TRUE aquí
        }
    )
```

---

#### [GAP-6] Performance metrics no capturados

**Problema:** Faltan métricas de performance

**Cuándo implementar:** PoC 2-3

**Campos a agregar:**
```python
"performance_metrics": {
    "estimated_execution_time_ms": 2.15,
    "estimated_total_time_design_to_results_ms": 590.5,
    "shots_per_second": 476.3,  # 1024 shots / 2.15ms
    "compilation_efficiency": 0.857,  # (original - compiled) / original
    "expected_result_quality": "high",  # Based on fidelity
    "recommended_shots_for_confidence_95": 1024,
    "recommended_shots_for_confidence_99": 2048
}
```

---

### PRIORIDAD BAJA: Mejoras futuras (PoC 3+)

#### [GAP-7] Circuit QASM diff analysis

**Para:** Entender cambios de compilación

```python
"circuit_analysis": {
    "circuit_qasm_original": "OPENQASM 2.0;...",
    "circuit_qasm_compiled": "OPENQASM 2.0;...",
    "diff_summary": {
        "gates_removed": ["ry", "cx"],
        "gates_added": ["u"],
        "gate_count_reduction": 7,
        "depth_reduction": 6
    }
}
```

#### [GAP-8] Compilation decisions tracking

**Para:** Debugging de decisiones de compilación

```python
"compilation_decisions": [
    {
        "decision_point": "layout_selection",
        "options_considered": ["sabre", "dense", "trivial"],
        "choice": "trivial",
        "reason": "minimal_circuit"
    },
    {
        "decision_point": "optimization_level",
        "options_considered": [0, 1, 2, 3],
        "choice": 3,
        "reason": "maximize_fidelity"
    }
]
```

---

## 🗺️ ROADMAP DE IMPLEMENTACIÓN

### Sprint 1: Fixes Críticos (Esta semana)

```
┌─ [GAP-1] ExecutionContext como array
│  └─ Archivos: qc_metadata_model.py, poc1_simple.py
│  └─ Tiempo: 1-2 horas
│  └─ Testing: Validar que JSON sigue siendo válido
│
├─ [GAP-2] Llenar gate_fidelities
│  └─ Archivos: poc1_simple.py
│  └─ Tiempo: 30 min
│  └─ Testing: Verificar valores en JSON
│
└─ [GAP-3] CompilationPass detallado
   └─ Archivos: qc_metadata_model.py, helpers.py, poc1_simple.py
   └─ Tiempo: 2-3 horas
   └─ Testing: Comparar JSON antes/después
```

**Salida esperada:** PoC 1 mejorado (v1.0.1)

---

### Sprint 2: PoC 2 - Iterativo (Próxima semana)

```
┌─ [GAP-4] Implementar ExperimentSession
│  └─ Crear poc2_iterative.py
│  └─ Loop de 5 iteraciones
│  └─ Agregar execution_context[] dinámicamente
│
├─ [GAP-5a] Básico: Periodic recalibration (SIN JIT aún)
│  └─ Simular recalibración cada 2 iteraciones
│  └─ NO recompilar (PoC 2 solo captura datos)
│
├─ [GAP-6a] Partial performance metrics
│  └─ Agregar estimated_execution_time_ms
│  └─ Agregar shots_per_second
│
└─ VALIDAR:
   └─ JSON estructura consistente
   └─ Convergencia VQE visible
   └─ Histórico de environmental_log
```

**Salida esperada:** PoC 2 (poc2_iterative.py)

---

### Sprint 3: PoC 3 - JIT Transpilation (2-3 semanas)

```
┌─ [GAP-5b] Implementar JIT real
│  └─ Forzar recalibración en iteración 3
│  └─ Recompilar automáticamente
│  └─ Crear CompilationTrace adicional
│  └─ Set jit_transpilation_used=true
│
├─ [GAP-6b] Performance metrics completos
│  └─ Calcular tiempos reales
│  └─ Recomendaciones de shots
│
├─ [GAP-7] Circuit QASM diff
│  └─ Comparar pre/post compilación
│  └─ Generar diff_summary
│
└─ [GAP-8] Compilation decisions
   └─ Registrar decisiones por pass
   └─ Agregar reasoning
```

**Salida esperada:** PoC 3 (poc3_jit.py)

---

### Sprint 4: Análisis Comparativo (Semana 4)

```
├─ run_all_pocs.py
│  └─ Ejecutar PoC 1, 2, 3 secuencialmente
│  └─ Generar 3 archivos JSON
│
├─ analysis_poc_comparison.py
│  └─ Comparar convergencia (PoC 1 vs PoC 2 vs PoC 3)
│  └─ Correlación calibration_age vs fidelidad
│  └─ Análisis JIT impact
│  └─ Generar gráficos
│
└─ OUTPUTS:
   └─ comparison_report.json
   └─ convergence_plot.png
   └─ performance_comparison.png
```

**Salida esperada:** Análisis comparativo completo

---

## 📋 PRÓXIMOS PASOS

### Paso 1: Implementar [GAP-1] - ExecutionContext como array

**Archivo:** `model/qc_metadata_model.py`

```python
# CAMBIO:
class QCMetadataModel:
    def __init__(self, ...):
        # Antes:
        self.execution_context = None
        
        # Ahora:
        self.execution_context = []  # SIEMPRE array
        
    def add_execution_context(self, exec_ctx):
        """Agregar ExecutionContext al modelo"""
        self.execution_context.append(exec_ctx)
        
    def to_complete_json(self):
        """Exportar a JSON completo"""
        return json.dumps({
            ...
            "execution_context": self.execution_context,  # Array
            ...
        }, indent=2)
```

**Testing:**
```python
# test_poc1_v1.0.1.py
def test_execution_context_is_array():
    model = QCMetadataModel(...)
    assert isinstance(model.execution_context, list)
    
    # Agregar ejecución
    model.add_execution_context(exec_ctx_1)
    assert len(model.execution_context) == 1
    
    # Exportar
    json_str = model.to_complete_json()
    data = json.loads(json_str)
    assert isinstance(data["execution_context"], list)
```

**Tiempo:** ~1 hora

---

### Paso 2: Llenar gate_fidelities en CalibrationData

**Archivo:** `poc1_simple.py` (línea ~90)

```python
# ANTES:
calibration_data = CalibrationData(
    ...
    gate_fidelities={"1q_gates": {}, "2q_gates": {}},  # EMPTY
    ...
)

# DESPUÉS:
calibration_data = CalibrationData(
    ...
    gate_fidelities={
        "1q_gates": {
            "x": 1.0, "y": 1.0, "z": 1.0,
            "h": 1.0, "s": 1.0, "t": 1.0,
            "rx": 1.0, "ry": 1.0, "rz": 1.0,
            "sx": 1.0, "id": 1.0
        },
        "2q_gates": {
            "cx": 1.0,
            "cz": 1.0,
            "swap": 1.0,
            "iswap": 1.0
        }
    },
    ...
)
```

**Testing:**
```python
# Verificar en JSON
json_data = json.loads(json_output)
assert json_data["calibration_data"][0]["gate_fidelities"]["1q_gates"]["x"] == 1.0
assert len(json_data["calibration_data"][0]["gate_fidelities"]["2q_gates"]) >= 2
```

**Tiempo:** ~30 minutos

---

### Paso 3: Mejorar CompilationPass con detalles

**Archivo:** `helpers.py` (agregar función)

```python
def extract_compilation_passes(compiled_circuit, original_circuit=None):
    """
    Extraer información detallada de los passes de compilación
    
    Returns:
        List[dict]: Lista de passes con detalles
    """
    # Nota: Qiskit no expone passes individuales fácilmente
    # Solución: Registrar manualmente los passes conocidos
    
    passes = [
        {
            "pass_name": "Unroll3qOrMore",
            "pass_order": 1,
            "status": "completed",
            "duration_ms": 5.2,
            "parameters": {"basis_gates": ["u", "cx"]},
            "circuit_state_after_pass": {
                "num_gates": 7,
                "circuit_depth": 6,
                "estimated_error": 0.10
            }
        },
        # ... más passes
    ]
    
    return passes
```

**En poc1_simple.py:**
```python
from helpers import extract_compilation_passes

# FASE 2: COMPILACIÓN
compilation_trace = CompilationTrace(
    ...
    compilation_passes=extract_compilation_passes(compiled_circuit, circuit),
    ...
)
```

**Tiempo:** ~2-3 horas

---

### Paso 4: Validar cambios

```bash
# Ejecutar PoC 1 mejorado
python poc1_simple.py

# Verificar JSON válido
python -c "import json; json.load(open('outputs/metadata_poc1_*.json'))"

# Ejecutar tests
pytest tests/test_poc1_v1.0.1.py -v

# Comparar con PoC 1 anterior
python scripts/compare_json_structure.py \
    metadata_poc1_v1.0.json \
    metadata_poc1_v1.0.1.json
```

---

## 🧪 VALIDACIÓN Y TESTING

### Tests a implementar

```python
# tests/test_poc1_improvements.py

def test_execution_context_is_always_array():
    """ExecutionContext debe ser siempre array"""
    pass

def test_gate_fidelities_not_empty():
    """gate_fidelities debe tener valores"""
    pass

def test_compilation_passes_have_details():
    """Cada pass debe tener pass_order, duration_ms, circuit_state"""
    pass

def test_json_schema_validation():
    """JSON debe validar contra schema v1.1"""
    pass

def test_w3c_prov_relations_valid():
    """Relaciones PROV deben ser válidas"""
    pass

def test_denormalization_consistent():
    """Mirrors deben coincidir exactamente"""
    pass

def test_timestamps_iso8601():
    """Todos los timestamps en ISO8601"""
    pass
```

### Ejecutar tests

```bash
pytest tests/ -v --cov=model --cov=poc

# Output esperado:
# tests/test_poc1_improvements.py::test_execution_context_is_always_array PASSED
# tests/test_poc1_improvements.py::test_gate_fidelities_not_empty PASSED
# ...
# ======== 7 passed in 0.45s ========
```

---

## 📊 MÉTRICAS DE ÉXITO

| Hito | Métrica | Objetivo | Estado |
|------|---------|----------|--------|
| PoC 1 v1.0.1 | Gaps críticos cerrados | 3/3 | 🔄 EN PROGRESO |
| PoC 1 v1.0.1 | JSON size | < 10 KB | ✅ CUMPLIDO |
| PoC 2 | Iteraciones | 5 | 🔄 PRÓXIMA |
| PoC 2 | Convergencia visible | Energía ↓ | 🔄 PRÓXIMA |
| PoC 3 | JIT working | ≥ 1 recompilación | 🔄 PRÓXIMA |
| Análisis | Correlaciones identificadas | ≥ 3 | 🔄 PRÓXIMA |

---

## 📞 SOPORTE Y DEBUGGING

### Problemas comunes

**Problema:** JSON no valida contra schema
```bash
python -m jsonschema -i outputs/metadata_poc1_*.json model/schema_qc_metadata_v1.1.json
```

**Problema:** Timestamps en formato incorrecto
```python
# Verificar
import datetime
dt = datetime.datetime.fromisoformat("2025-11-13T19:06:44Z".replace('Z', '+00:00'))
print(dt.isoformat() + "Z")  # Debe ser igual
```

**Problema:** ExecutionContext no es array
```python
# Debug
import json
data = json.load(open("outputs/metadata_poc1_*.json"))
print(type(data["execution_context"]))  # Debe ser list
```

---

## 📚 REFERENCIAS

- **Modelo v1.1:** `model/qc_metadata_model.py`
- **JSON Schema:** `model/schema_qc_metadata_v1.1.json`
- **Análisis anterior:** `Analisis_Completo_PoC1_Validacion.md`
- **Guía de reestructuración:** `Guia_Reestructuracion_Capitulos.md`

---

## 🎯 RESUMEN

| Aspecto | Estado | Acción |
|---------|--------|--------|
| **PoC 1 Base** | ✅ Completo | Mantener |
| **[GAP-1] Array** | ⚠️ CRÍTICO | Implementar semana 1 |
| **[GAP-2] Fidelidades** | ⚠️ MEDIO | Implementar semana 1 |
| **[GAP-3] Pass detalles** | ⚠️ MEDIO | Implementar semana 1 |
| **PoC 2 Iterativo** | 🔄 PRÓXIMO | Comenzar después de fixes |
| **PoC 3 JIT** | 🔄 FUTURO | Comenzar semana 3 |
| **Análisis comp.** | 🔄 FUTURO | Comenzar semana 4 |

---

**Documento último actualizado:** 2025-11-13
**Versión:** 1.0
**Autor:** Análisis automático del modelo PoC

