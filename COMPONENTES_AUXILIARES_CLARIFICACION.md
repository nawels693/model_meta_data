# Aclaración: Componentes Auxiliares y Mapeo Diagrama-Código

## Respuesta a tus preguntas

### 1. ¿Están considerados los Componentes Auxiliares en el código?

**Sí, pero con una diferencia importante de implementación:**

#### A. `ProvenanceRelation` (del diagrama)
**En el diagrama:** Clase separada con atributos `relation_type`, `source_id`, `target_id`, `timestamp`, `role`.

**En el código (`model/qc_metadata_model.py`):**
- **NO existe como clase separada**
- **SÍ existe como estructura de datos** dentro de `ProvenanceRecordLean`
- Se implementa como un **diccionario** dentro de la lista `relations: List[Dict[str, Any]]`

**Ejemplo de uso:**
```python
# En poc_ibm_cloud.py línea 240-246
provenance_record.add_relation(
    "wasDerivedFrom",           # relation_type
    compilation_trace.trace_id, # source_id
    circuit_metadata.circuit_id,# target_id
    compilation_trace.timestamp_compilation, # timestamp
    role="compilation_input"     # role (opcional)
)
```

**Estructura interna del diccionario generado:**
```python
{
    "relation_type": "wasDerivedFrom",
    "source_id": "trace_ibm_cloud_20251119_152307",
    "target_id": "circuit_vqe_h2_ibm_cloud_20251119_152307",
    "timestamp": "2025-11-19T15:23:07.832Z",
    "role": "compilation_input"  # opcional
}
```

#### B. `CompilationPass` (del diagrama)
**En el diagrama:** Clase separada con atributos `pass_name`, `pass_order`, `parameters`, `circuit_state_after_pass`.

**En el código (`model/qc_metadata_model.py`):**
- **NO existe como clase separada**
- **SÍ existe como estructura de datos** dentro de `CompilationTrace`
- Se implementa como un **diccionario** dentro de la lista `compilation_passes: List[Dict[str, Any]]`

**Ejemplo de generación (`helpers.py` línea 306-319):**
```python
passes_detail.append({
    "pass_name": "Unroll3qOrMore",
    "pass_order": 1,
    "status": "completed",
    "duration_ms": avg_pass_duration * 1.2,
    "parameters": {
        "basis_gates": ["u", "cx"],
        "target_basis": "universal"
    },
    "circuit_state_after_pass": {
        "num_gates": original_gates,
        "circuit_depth": original_depth,
        "estimated_error": 0.10
    }
})
```

#### C. `QCMetadataModel` (Contenedor)
**SÍ está completamente implementado** como clase principal en `model/qc_metadata_model.py` línea 213-289.

---

### 2. ¿`ProvenanceRecordLean` es `provenance_record`?

**Sí, exactamente.**

**Mapeo:**
- **Clase Python:** `ProvenanceRecordLean` (definida en `model/qc_metadata_model.py` línea 148)
- **Atributo en QCMetadataModel:** `provenance_record: ProvenanceRecordLean` (línea 223)
- **En JSON exportado:** Aparece como `"provenance_record": {...}`

**Ejemplo de uso:**
```python
# Crear instancia
provenance_record = ProvenanceRecordLean(
    provenance_id=f"prov_ibm_cloud_{timestamp}",
    timestamp_recorded=get_utc_now_iso(),
    prov_mode="lean"
)

# Agregar al modelo
model = QCMetadataModel(
    ...
    provenance_record=provenance_record  # <-- aquí se asigna
)
```

---

## Resumen: Implementación vs. Diagrama

| Componente del Diagrama | Estado en Código | Ubicación |
|--------------------------|------------------|-----------|
| `ProvenanceRelation` | ✅ Implementado como `Dict` dentro de `ProvenanceRecordLean.relations` | `model/qc_metadata_model.py` línea 154, método `add_relation()` |
| `CompilationPass` | ✅ Implementado como `Dict` dentro de `CompilationTrace.compilation_passes` | `helpers.py` función `extract_compilation_passes()` |
| `QCMetadataModel` | ✅ Clase completa | `model/qc_metadata_model.py` línea 213 |
| `ProvenanceRecordLean` → `provenance_record` | ✅ Mapeo directo | `model/qc_metadata_model.py` línea 148 (clase) y 223 (atributo) |

---

## ¿Por qué esta diferencia de implementación?

**Razón de diseño:** En Python, cuando una estructura de datos es simple y no requiere métodos complejos, es más eficiente y flexible usar `Dict` en lugar de crear clases separadas. Esto permite:
1. **Serialización JSON directa** sin conversiones adicionales
2. **Menor overhead** de memoria
3. **Flexibilidad** para agregar campos dinámicamente

**El modelo conceptual del diagrama sigue siendo válido:** Los componentes auxiliares existen y funcionan exactamente como se describe, solo que están implementados como estructuras de datos anidadas en lugar de clases independientes.

---

## Verificación en el código

Puedes verificar esto revisando:
1. **`model/qc_metadata_model.py` línea 154:** `relations: List[Dict[str, Any]]`
2. **`model/qc_metadata_model.py` línea 114:** `compilation_passes: List[Dict[str, Any]]`
3. **`helpers.py` línea 270-452:** Función `extract_compilation_passes()` que genera los diccionarios
4. **Cualquier archivo JSON de salida:** Verás `"compilation_passes": [...]` y `"relations": [...]` como arrays de objetos JSON

