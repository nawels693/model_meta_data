# Diagrama de Implementación Real: QCMetadata Model v1.1

## Diagrama basado en el código actual (`model/qc_metadata_model.py`)

Este diagrama refleja **exactamente** cómo están implementadas las clases en el código, incluyendo tipos de datos reales y estructuras anidadas.

```mermaid
classDiagram
    %% ============================================================
    %% FASE 1: DISEÑO
    %% ============================================================
    
    class DeviceMetadata {
        +str device_id
        +str provider
        +str technology
        +str backend_name
        +int num_qubits
        +str version
        +str timestamp_metadata
        +Dict[str, Any] connectivity
        +Dict[str, Any] noise_characteristics
        +Dict[str, Any] operational_parameters
        +to_dict() Dict[str, Any]
    }
    
    class CircuitMetadata {
        +str circuit_id
        +str circuit_name
        +str algorithm_type
        +int num_qubits
        +int circuit_depth
        +int num_gates
        +str timestamp_created
        +str description
        +str author
        +List[str] tags
        +Dict[str, Any] algorithm_parameters
        +Optional[str] circuit_qasm
        +to_dict() Dict[str, Any]
    }
    
    %% ============================================================
    %% FASE 2: COMPILACIÓN
    %% ============================================================
    
    class CalibrationData {
        +str calibration_id
        +str device_id
        +str timestamp_captured
        +str valid_until
        +str calibration_method
        +str calibration_version
        +Dict[int, Dict[str, Any]] qubit_properties
        +Dict[str, Any] gate_fidelities
        +Dict[str, Any] crosstalk_matrix
        +Dict[str, Any] additional_metrics
        +is_valid_now() bool
        +age_seconds() float
        +to_dict() Dict[str, Any]
    }
    
    class CompilationTrace {
        +str trace_id
        +str circuit_id
        +str device_id
        +str calibration_id
        +str timestamp_compilation
        +str compiler_name
        +str compiler_version
        +float compilation_duration_ms
        +List[Dict[str, Any]] compilation_passes
        +Dict[str, Any] optimization_metrics
        +Dict[str, Any] decisions_made
        +Optional[str] final_circuit_qasm
        +List[str] compilation_errors
        +to_dict() Dict[str, Any]
    }
    
    %% NOTA: CompilationPass NO es una clase, es Dict dentro de compilation_passes
    note for CompilationTrace "compilation_passes contiene\nList[Dict] donde cada Dict tiene:\n- pass_name: str\n- pass_order: int\n- status: str\n- duration_ms: float\n- parameters: Dict\n- circuit_state_after_pass: Dict"
    
    %% ============================================================
    %% FASE 3: EJECUCIÓN
    %% ============================================================
    
    class ExecutionContext {
        +str execution_id
        +str trace_id
        +str device_id
        +str calibration_id
        +str timestamp_execution
        +str timestamp_compilation
        +int num_shots
        +str execution_mode
        +bool computed_from_trace
        +Dict[str, Any] queue_information
        +Dict[str, Any] environmental_context
        +Dict[str, Any] freshness_validation
        +Dict[str, Any] execution_parameters
        +Optional[Dict[str, Any]] results
        +to_dict() Dict[str, Any]
    }
    
    note for ExecutionContext "device_id y calibration_id son\nMIRRORS validados contra\nCompilationTrace"
    
    class ExperimentSession {
        +str session_id
        +str algorithm_type
        +str timestamp_started
        +str circuit_id
        +str device_id
        +str optimizer
        +int max_iterations
        +int shots_default
        +str calibration_policy
        +int num_executions
        +int total_shots_used
        +List[str] execution_ids
        +Dict[str, Any] session_metrics
        +List[Dict[str, Any]] environmental_log
        +Optional[str] timestamp_ended
        +add_execution(str, int) void
        +to_dict() Dict[str, Any]
    }
    
    %% ============================================================
    %% FASE 4: ANÁLISIS
    %% ============================================================
    
    class ProvenanceRecordLean {
        +str provenance_id
        +str timestamp_recorded
        +str prov_mode
        +List[Dict[str, Any]] relations
        +Dict[str, Any] workflow_graph
        +Dict[str, Any] quality_assessment
        +add_relation(str, str, str, str, Optional[str]) void
        +to_dict() Dict[str, Any]
    }
    
    %% NOTA: ProvenanceRelation NO es una clase, es Dict dentro de relations
    note for ProvenanceRecordLean "relations contiene List[Dict]\ndonde cada Dict tiene:\n- relation_type: str\n- source_id: str\n- target_id: str\n- timestamp: str\n- role: Optional[str]"
    
    %% ============================================================
    %% CONTENEDOR PRINCIPAL
    %% ============================================================
    
    class QCMetadataModel {
        +str model_version
        +str timestamp_model_created
        +DeviceMetadata device_metadata
        +List[CalibrationData] calibration_data
        +CircuitMetadata circuit_metadata
        +Union[CompilationTrace, List[CompilationTrace]] compilation_trace
        +List[ExecutionContext] execution_context
        +ProvenanceRecordLean provenance_record
        +Optional[ExperimentSession] experiment_session
        +add_execution_context(ExecutionContext) void
        +validate_denormalization() bool
        +to_complete_json(int) str
        +to_dict() Dict[str, Any]
    }
    
    %% ============================================================
    %% ENUM AUXILIAR
    %% ============================================================
    
    class ProvRelationType {
        <<enumeration>>
        WAS_DERIVED_FROM
        USED
        WAS_GENERATED_BY
        WAS_INFORMED_BY
    }
    
    %% ============================================================
    %% RELACIONES
    %% ============================================================
    
    QCMetadataModel "1" --> "1" DeviceMetadata : contiene
    QCMetadataModel "1" --> "*" CalibrationData : contiene
    QCMetadataModel "1" --> "1" CircuitMetadata : contiene
    QCMetadataModel "1" --> "1..*" CompilationTrace : contiene
    QCMetadataModel "1" --> "*" ExecutionContext : contiene (SIEMPRE List)
    QCMetadataModel "1" --> "1" ProvenanceRecordLean : contiene (provenance_record)
    QCMetadataModel "0..1" --> "1" ExperimentSession : contiene
    
    CompilationTrace "1" --> "1" CircuitMetadata : referencia (circuit_id)
    CompilationTrace "1" --> "1" DeviceMetadata : referencia (device_id)
    CompilationTrace "1" --> "1" CalibrationData : referencia (calibration_id)
    
    ExecutionContext "1" --> "1" CompilationTrace : referencia (trace_id)
    ExecutionContext "1" --> "1" DeviceMetadata : MIRROR (device_id)
    ExecutionContext "1" --> "1" CalibrationData : MIRROR (calibration_id)
    
    ExperimentSession "*" --> "1" CircuitMetadata : referencia (circuit_id)
    ExperimentSession "*" --> "1" DeviceMetadata : referencia (device_id)
    ExperimentSession "1" --> "*" ExecutionContext : agrupa (execution_ids)
    
    ProvenanceRecordLean ..> ProvRelationType : usa valores
    
    %% Relaciones conceptuales (no directas en código)
    CircuitMetadata ..> DeviceMetadata : targets/referencias
    CompilationTrace ..> CalibrationData : usa (calibration_id)
```

## Notas Importantes sobre la Implementación

### 1. Componentes Auxiliares como Estructuras de Datos

**`CompilationPass`** (del diagrama conceptual):
- **NO existe como clase** en el código
- **SÍ existe como `Dict[str, Any]`** dentro de `CompilationTrace.compilation_passes: List[Dict[str, Any]]`
- Se genera mediante `extract_compilation_passes()` en `helpers.py`
- Estructura típica de cada Dict:
  ```python
  {
      "pass_name": "Unroll3qOrMore",
      "pass_order": 1,
      "status": "completed",
      "duration_ms": 123.45,
      "parameters": {"basis_gates": ["u", "cx"]},
      "circuit_state_after_pass": {"num_gates": 10, "circuit_depth": 5}
  }
  ```

**`ProvenanceRelation`** (del diagrama conceptual):
- **NO existe como clase** en el código
- **SÍ existe como `Dict[str, Any]`** dentro de `ProvenanceRecordLean.relations: List[Dict[str, Any]]`
- Se crea mediante `add_relation()` en `ProvenanceRecordLean`
- Estructura típica de cada Dict:
  ```python
  {
      "relation_type": "wasDerivedFrom",
      "source_id": "trace_123",
      "target_id": "circuit_456",
      "timestamp": "2025-11-19T15:23:07Z",
      "role": "compilation_input"  # opcional
  }
  ```

### 2. Tipos de Datos Específicos

- **`execution_context`**: **SIEMPRE** `List[ExecutionContext]` (nunca un solo objeto) - GAP-1 fix
- **`compilation_trace`**: `Union[CompilationTrace, List[CompilationTrace]]` (puede ser uno o varios)
- **`calibration_data`**: `List[CalibrationData]` (siempre lista, puede tener múltiples snapshots)
- **`experiment_session`**: `Optional[ExperimentSession]` (puede ser None)

### 3. Métodos Clave

- **`ProvenanceRecordLean.add_relation()`**: Crea y añade un Dict a `relations`
- **`QCMetadataModel.validate_denormalization()`**: Valida que los MIRRORS en `ExecutionContext` coincidan con `CompilationTrace`
- **`CalibrationData.is_valid_now()`**: Verifica si `valid_until` ha expirado
- **`QCMetadataModel.to_complete_json()`**: Serializa todo el modelo a JSON con validación

### 4. Diferencias con el Diagrama Conceptual

| Aspecto | Diagrama Conceptual | Implementación Real |
|---------|-------------------|---------------------|
| `ProvenanceRelation` | Clase separada | `Dict` dentro de `relations` |
| `CompilationPass` | Clase separada | `Dict` dentro de `compilation_passes` |
| `execution_context` | Puede ser objeto único | **SIEMPRE** `List[ExecutionContext]` |
| `provenance_record` | `ProvenanceRecordLean` | Mapeo directo ✅ |

## Archivos Relacionados

- **Implementación:** `model/qc_metadata_model.py`
- **Esquema JSON:** `model/schema_qc_metadata_v1.1.json`
- **Generación de passes:** `helpers.py::extract_compilation_passes()`
- **Uso en PoC:** `poc_ibm_cloud.py`, `thesis_experiments.py`

