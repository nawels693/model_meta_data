#!/usr/bin/env python3
"""
Modelo de Metadatos para Computación Cuántica v1.1
Implementación de las clases principales del modelo de metadatos
"""

import json
import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum


class ProvRelationType(str, Enum):
    """Tipos de relaciones PROV"""
    WAS_DERIVED_FROM = "wasDerivedFrom"
    USED = "used"
    WAS_GENERATED_BY = "wasGeneratedBy"
    WAS_INFORMED_BY = "wasInformedBy"


@dataclass
class DeviceMetadata:
    """Metadatos del dispositivo cuántico"""
    device_id: str
    provider: str
    technology: str  # "superconducting", "ion_trap", "simulator", etc.
    backend_name: str
    num_qubits: int
    version: str
    timestamp_metadata: str  # ISO 8601 format
    connectivity: Dict[str, Any] = field(default_factory=dict)
    noise_characteristics: Dict[str, Any] = field(default_factory=dict)
    operational_parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        return asdict(self)


@dataclass
class CircuitMetadata:
    """Metadatos del circuito cuántico"""
    circuit_id: str
    circuit_name: str
    algorithm_type: str
    num_qubits: int
    circuit_depth: int
    num_gates: int
    timestamp_created: str  # ISO 8601 format
    description: str = ""
    author: str = ""
    tags: List[str] = field(default_factory=list)
    algorithm_parameters: Dict[str, Any] = field(default_factory=dict)
    circuit_qasm: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        return asdict(self)


@dataclass
class CalibrationData:
    """Datos de calibración del dispositivo"""
    calibration_id: str
    device_id: str
    timestamp_captured: str  # ISO 8601 format
    valid_until: str  # ISO 8601 format
    calibration_method: str
    calibration_version: str
    qubit_properties: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    gate_fidelities: Dict[str, Any] = field(default_factory=dict)
    crosstalk_matrix: Dict[str, Any] = field(default_factory=dict)
    additional_metrics: Dict[str, Any] = field(default_factory=dict)

    def is_valid_now(self) -> bool:
        """Verifica si la calibración sigue siendo válida"""
        try:
            valid_until_dt = datetime.datetime.fromisoformat(
                self.valid_until.replace('Z', '+00:00')
            )
            now = datetime.datetime.now(datetime.timezone.utc)
            return now < valid_until_dt
        except Exception:
            return False

    def age_seconds(self) -> float:
        """Retorna la edad de la calibración en segundos"""
        try:
            captured_dt = datetime.datetime.fromisoformat(
                self.timestamp_captured.replace('Z', '+00:00')
            )
            now = datetime.datetime.now(datetime.timezone.utc)
            return (now - captured_dt).total_seconds()
        except Exception:
            return 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        return asdict(self)


@dataclass
class CompilationTrace:
    """Traza de compilación del circuito"""
    trace_id: str
    circuit_id: str
    device_id: str
    calibration_id: str
    timestamp_compilation: str  # ISO 8601 format
    compiler_name: str
    compiler_version: str
    compilation_duration_ms: float
    compilation_passes: List[Dict[str, Any]] = field(default_factory=list)
    optimization_metrics: Dict[str, Any] = field(default_factory=dict)
    decisions_made: Dict[str, Any] = field(default_factory=dict)
    final_circuit_qasm: Optional[str] = None
    compilation_errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        return asdict(self)


@dataclass
class ExecutionContext:
    """Contexto de ejecución del circuito"""
    execution_id: str
    trace_id: str
    device_id: str  # MIRROR from CompilationTrace
    calibration_id: str  # MIRROR from CompilationTrace
    timestamp_execution: str  # ISO 8601 format
    timestamp_compilation: str  # MIRROR from CompilationTrace
    num_shots: int
    execution_mode: str  # "qasm_simulator", "statevector_simulator", "qpu", etc.
    computed_from_trace: bool = True
    queue_information: Dict[str, Any] = field(default_factory=dict)
    environmental_context: Dict[str, Any] = field(default_factory=dict)
    freshness_validation: Dict[str, Any] = field(default_factory=dict)
    execution_parameters: Dict[str, Any] = field(default_factory=dict)
    results: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        return asdict(self)


@dataclass
class ProvenanceRecordLean:
    """Registro de proveniencia (versión lean)"""
    provenance_id: str
    timestamp_recorded: str  # ISO 8601 format
    prov_mode: str = "lean"
    relations: List[Dict[str, Any]] = field(default_factory=list)
    workflow_graph: Dict[str, Any] = field(default_factory=dict)
    quality_assessment: Dict[str, Any] = field(default_factory=dict)

    def add_relation(
        self,
        relation_type: str,
        source_id: str,
        target_id: str,
        timestamp: str,
        role: Optional[str] = None
    ):
        """Añade una relación de proveniencia"""
        relation = {
            "relation_type": relation_type,
            "source_id": source_id,
            "target_id": target_id,
            "timestamp": timestamp
        }
        if role:
            relation["role"] = role
        self.relations.append(relation)

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        return asdict(self)


@dataclass
class ExperimentSession:
    """Sesión de experimento (agregación de múltiples ejecuciones)"""
    session_id: str
    algorithm_type: str
    timestamp_started: str  # ISO 8601 format
    circuit_id: str
    device_id: str
    optimizer: str
    max_iterations: int
    shots_default: int
    calibration_policy: str  # "static", "periodic", "jit"
    num_executions: int = 0
    total_shots_used: int = 0
    execution_ids: List[str] = field(default_factory=list)
    session_metrics: Dict[str, Any] = field(default_factory=dict)
    environmental_log: List[Dict[str, Any]] = field(default_factory=list)
    timestamp_ended: Optional[str] = None

    def add_execution(self, execution_id: str, shots: int):
        """Añade una ejecución a la sesión"""
        if execution_id not in self.execution_ids:
            self.execution_ids.append(execution_id)
            self.num_executions += 1
            self.total_shots_used += shots

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        return asdict(self)


@dataclass
class QCMetadataModel:
    """Modelo completo de metadatos QC (contenedor principal)"""
    model_version: str
    timestamp_model_created: str  # ISO 8601 format
    device_metadata: DeviceMetadata
    calibration_data: List[CalibrationData]
    circuit_metadata: CircuitMetadata
    compilation_trace: Union[CompilationTrace, List[CompilationTrace]]
    execution_context: List[ExecutionContext]  # SIEMPRE array (GAP-1 fix)
    provenance_record: ProvenanceRecordLean
    experiment_session: Optional[ExperimentSession] = None
    
    def add_execution_context(self, exec_ctx: ExecutionContext):
        """Agregar ExecutionContext al modelo"""
        if exec_ctx not in self.execution_context:
            self.execution_context.append(exec_ctx)

    def validate_denormalization(self) -> bool:
        """
        Valida que los mirrors (device_id, calibration_id) sean consistentes
        entre CompilationTrace y ExecutionContext
        """
        # Normalizar compilation_trace a lista (execution_context ya es lista)
        traces = self.compilation_trace if isinstance(
            self.compilation_trace, list
        ) else [self.compilation_trace]
        executions = self.execution_context  # Ya es lista (GAP-1 fix)

        # Validar que cada ExecutionContext tiene mirrors consistentes
        for exec_ctx in executions:
            # Encontrar el trace correspondiente
            trace = next(
                (t for t in traces if t.trace_id == exec_ctx.trace_id),
                None
            )
            if trace is None:
                return False

            # Validar mirrors
            if exec_ctx.device_id != trace.device_id:
                return False
            if exec_ctx.calibration_id != trace.calibration_id:
                return False
            if exec_ctx.timestamp_compilation != trace.timestamp_compilation:
                return False

        return True

    def to_complete_json(self, indent: int = 2) -> str:
        """Exporta el modelo completo a JSON"""
        data = {
            "model_version": self.model_version,
            "timestamp_model_created": self.timestamp_model_created,
            "device_metadata": self.device_metadata.to_dict(),
            "calibration_data": [cal.to_dict() for cal in self.calibration_data],
            "circuit_metadata": self.circuit_metadata.to_dict(),
            "compilation_trace": (
                [trace.to_dict() for trace in self.compilation_trace]
                if isinstance(self.compilation_trace, list)
                else self.compilation_trace.to_dict()
            ),
            "execution_context": [
                exec_ctx.to_dict() for exec_ctx in self.execution_context
            ],  # Siempre array (GAP-1 fix)
            "provenance_record": self.provenance_record.to_dict(),
        }

        if self.experiment_session:
            data["experiment_session"] = self.experiment_session.to_dict()

        return json.dumps(data, indent=indent, ensure_ascii=False)

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        return json.loads(self.to_complete_json())

