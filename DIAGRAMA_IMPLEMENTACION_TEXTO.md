# Diagrama de Implementación Real (Versión Texto)

## Estructura de Clases según `model/qc_metadata_model.py`

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    QCMetadataModel (Contenedor Principal)                │
│  - model_version: str                                                   │
│  - timestamp_model_created: str                                         │
│  - device_metadata: DeviceMetadata                                      │
│  - calibration_data: List[CalibrationData]                              │
│  - circuit_metadata: CircuitMetadata                                    │
│  - compilation_trace: Union[CompilationTrace, List[CompilationTrace]]  │
│  - execution_context: List[ExecutionContext]  ← SIEMPRE List (GAP-1)   │
│  - provenance_record: ProvenanceRecordLean                             │
│  - experiment_session: Optional[ExperimentSession]                     │
│                                                                          │
│  Métodos:                                                                │
│  + add_execution_context(ExecutionContext)                            │
│  + validate_denormalization() -> bool                                  │
│  + to_complete_json(indent) -> str                                     │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              │ contiene
                              │
        ┌─────────────────────┼─────────────────────┬─────────────────────┐
        │                     │                     │                     │
        ▼                     ▼                     ▼                     ▼

┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ DeviceMetadata   │  │ CircuitMetadata  │  │ CalibrationData   │  │ CompilationTrace │
├──────────────────┤  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤
│ device_id: str  │  │ circuit_id: str  │  │ calibration_id   │  │ trace_id: str    │
│ provider: str    │  │ circuit_name     │  │ device_id: str    │  │ circuit_id: str  │
│ technology: str  │  │ algorithm_type   │  │ timestamp_captured│  │ device_id: str   │
│ backend_name     │  │ num_qubits: int  │  │ valid_until: str │  │ calibration_id   │
│ num_qubits: int  │  │ circuit_depth    │  │ calibration_method│  │ timestamp_comp  │
│ version: str     │  │ num_gates: int   │  │ qubit_properties │  │ compiler_name    │
│ timestamp_meta   │  │ timestamp_created│  │ gate_fidelities  │  │ compiler_version │
│ connectivity     │  │ algorithm_params │  │                  │  │ duration_ms      │
│ noise_chars      │  │ circuit_qasm     │  │ Métodos:         │  │                  │
│                  │  │                  │  │ + is_valid_now() │  │ compilation_     │
│                  │  │                  │  │ + age_seconds()  │  │   passes:         │
│                  │  │                  │  │                  │  │   List[Dict]     │
│                  │  │                  │  │                  │  │   ⚠️ NO es clase │
│                  │  │                  │  │                  │  │                  │
└──────────────────┘  └──────────────────┘  └──────────────────┘  └──────────────────┘
        ▲                     ▲                     ▲                     │
        │                     │                     │                     │
        │                     │                     │                     │ referencia
        │                     │                     │                     │
        └─────────────────────┴─────────────────────┴─────────────────────┘
                              │
                              │ referencia
                              │
                              ▼
                    ┌──────────────────┐
                    │ ExecutionContext│
                    ├──────────────────┤
                    │ execution_id     │
                    │ trace_id: str   │
                    │ device_id: str   │ ← MIRROR (validado)
                    │ calibration_id   │ ← MIRROR (validado)
                    │ timestamp_exec   │
                    │ num_shots: int   │
                    │ execution_mode   │
                    │ results: Dict    │
                    └──────────────────┘
                              │
                              │ grouped_by
                              │
                              ▼
                    ┌──────────────────┐
                    │ExperimentSession │
                    ├──────────────────┤
                    │ session_id       │
                    │ algorithm_type   │
                    │ timestamp_started │
                    │ circuit_id        │
                    │ device_id         │
                    │ execution_ids     │
                    │ total_shots_used  │
                    │ session_metrics   │
                    └──────────────────┘
                              │
                              │ contiene
                              │
                              ▼
                    ┌──────────────────┐
                    │ProvenanceRecord  │
                    │     Lean         │
                    ├──────────────────┤
                    │ provenance_id    │
                    │ timestamp_record │
                    │ prov_mode: str   │
                    │                  │
                    │ relations:       │
                    │   List[Dict]     │
                    │   ⚠️ NO es clase │
                    │                  │
                    │ workflow_graph   │
                    │ quality_assess   │
                    │                  │
                    │ Métodos:         │
                    │ + add_relation() │
                    └──────────────────┘
```

## Estructura de Datos Anidados (NO son clases)

### 1. CompilationPass (dentro de `CompilationTrace.compilation_passes`)

```python
# Tipo: List[Dict[str, Any]]
[
    {
        "pass_name": "Unroll3qOrMore",
        "pass_order": 1,
        "status": "completed",
        "duration_ms": 123.45,
        "parameters": {
            "basis_gates": ["u", "cx"],
            "target_basis": "universal"
        },
        "circuit_state_after_pass": {
            "num_gates": 10,
            "circuit_depth": 5,
            "estimated_error": 0.10
        }
    },
    {
        "pass_name": "Optimize1qGates",
        "pass_order": 7,
        ...
    }
]
```

**Generado por:** `helpers.py::extract_compilation_passes()`

### 2. ProvenanceRelation (dentro de `ProvenanceRecordLean.relations`)

```python
# Tipo: List[Dict[str, Any]]
[
    {
        "relation_type": "wasDerivedFrom",
        "source_id": "trace_ibm_cloud_20251119_152307",
        "target_id": "circuit_vqe_h2_ibm_cloud_20251119_152307",
        "timestamp": "2025-11-19T15:23:07.832Z",
        "role": "compilation_input"  # opcional
    },
    {
        "relation_type": "used",
        "source_id": "trace_ibm_cloud_20251119_152307",
        "target_id": "cal_ibm_fez_20251119_150802",
        "timestamp": "2025-11-19T15:23:07.832Z"
    }
]
```

**Creado por:** `ProvenanceRecordLean.add_relation()`

## Flujo de Referencias (Foreign Keys)

```
CircuitMetadata (circuit_id)
    ↑
    │ referencia
    │
CompilationTrace (circuit_id, device_id, calibration_id)
    │
    │ referencia
    │
ExecutionContext (trace_id)
    │
    │ MIRROR (validado)
    │
    ├─→ device_id debe coincidir con CompilationTrace.device_id
    └─→ calibration_id debe coincidir con CompilationTrace.calibration_id
```

## Validación de Denormalización

El método `QCMetadataModel.validate_denormalization()` verifica:

1. Cada `ExecutionContext.trace_id` existe en `compilation_trace`
2. `ExecutionContext.device_id` == `CompilationTrace.device_id`
3. `ExecutionContext.calibration_id` == `CompilationTrace.calibration_id`
4. `ExecutionContext.timestamp_compilation` == `CompilationTrace.timestamp_compilation`

## Diferencias Clave con Diagrama Conceptual

| Componente | Diagrama Conceptual | Implementación Real |
|------------|---------------------|---------------------|
| **ProvenanceRelation** | Clase `<<HELPER>>` | `Dict` en `relations: List[Dict]` |
| **CompilationPass** | Clase `<<HELPER>>` | `Dict` en `compilation_passes: List[Dict]` |
| **execution_context** | Puede ser objeto único | **SIEMPRE** `List[ExecutionContext]` |
| **provenance_record** | `ProvenanceRecordLean` | ✅ Mapeo directo |

## Archivos de Referencia

- **Código:** `model/qc_metadata_model.py`
- **Esquema:** `model/schema_qc_metadata_v1.1.json`
- **Clarificación:** `COMPONENTES_AUXILIARES_CLARIFICACION.md`


