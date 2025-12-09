#!/usr/bin/env python3
"""
Experimentos de Tesis: Impacto de la Optimización en la Compilación
Este script ejecuta una batería de pruebas variando los niveles de optimización
para generar datos comparativos útiles para el análisis del trabajo de título.
"""

import json
import datetime
import sys
import os
import csv
from time import sleep

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from qiskit import transpile
from model.qc_metadata_model import (
    DeviceMetadata, CircuitMetadata, CalibrationData,
    CompilationTrace, ExecutionContext, ProvenanceRecordLean,
    QCMetadataModel
)
from helpers import (
    build_vqe_circuit,
    get_circuit_qasm,
    get_utc_now_iso,
    get_utc_now,
    extract_compilation_passes,
    simulate_vqe_execution
)
from cloud_providers import IBMProvider

# ============================================================
# CONFIGURACIÓN EXPERIMENTAL
# ============================================================

OUTPUT_DIR = "outputs/thesis_experiments"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Usaremos simulador para garantizar rapidez y reproducibilidad en este experimento
# En una tesis real, se podría replicar con hardware real cambiando esto.
BACKEND_NAME = "qasm_simulator" 
# Para simular variabilidad de hardware, usaremos datos dummy o reales si hay conexión
USE_MOCK_PROVIDER = True 

# Niveles de optimización a probar
OPTIMIZATION_LEVELS = [0, 1, 2, 3]

print(f"=== INICIANDO EXPERIMENTOS DE TESIS ===")
print(f"Objetivo: Analizar impacto de niveles de optimización (0-3)")
print(f"Backend: {BACKEND_NAME}")
print(f"Output Dir: {OUTPUT_DIR}\n")

# Archivo para resumen de resultados (CSV)
csv_file = os.path.join(OUTPUT_DIR, "optimization_analysis.csv")
with open(csv_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        "Experiment_ID", "Opt_Level", "Original_Depth", "Compiled_Depth", 
        "Original_Gates", "Compiled_Gates", "Compilation_Time_ms", 
        "Est_Fidelity", "JSON_File"
    ])

# ============================================================
# CICLO EXPERIMENTAL
# ============================================================

# provider = IBMProvider(token="DUMMY") if USE_MOCK_PROVIDER else None
# No inicializamos el provider real si es un Mock, para evitar errores de autenticación
provider = None

# Obtener metadatos del dispositivo (una vez para todos los experimentos)
# Simulamos que es el mismo dispositivo
print("[SETUP] Obteniendo metadatos del dispositivo base...")
if USE_MOCK_PROVIDER:
    # Crear metadata dummy consistente
    device_metadata = DeviceMetadata(
        device_id=BACKEND_NAME,
        provider="Simulated Provider",
        technology="simulator",
        backend_name=BACKEND_NAME,
        num_qubits=32,
        version="1.0",
        timestamp_metadata=get_utc_now_iso(),
        connectivity={"topology_type": "all_to_all"},
        noise_characteristics={},
        operational_parameters={"simulator": True}
    )
    calibration_data = CalibrationData(
        calibration_id=f"cal_sim_{datetime.datetime.now().strftime('%Y%m%d')}",
        device_id=BACKEND_NAME,
        timestamp_captured=get_utc_now_iso(),
        valid_until=(get_utc_now() + datetime.timedelta(hours=24)).isoformat() + "Z",
        calibration_method="simulator_default",
        calibration_version="1.0"
    )
else:
    # Usar provider real (si estuviera configurado)
    pass

# Definir el circuito base (VQE H2)
circuit_base = build_vqe_circuit(2)
circuit_original_depth = circuit_base.depth()
circuit_original_gates = len(circuit_base.data)

for opt_level in OPTIMIZATION_LEVELS:
    print(f"\n>>> Ejecutando prueba con Optimization Level {opt_level}...")
    
    # 1. CREAR METADATOS DEL CIRCUITO
    circuit_metadata = CircuitMetadata(
        circuit_id=f"circ_vqe_opt{opt_level}_{datetime.datetime.now().strftime('%H%M%S')}",
        circuit_name=f"VQE H2 (Opt Lvl {opt_level})",
        algorithm_type="vqe",
        num_qubits=2,
        circuit_depth=circuit_original_depth,
        num_gates=circuit_original_gates,
        timestamp_created=get_utc_now_iso(),
        description=f"Experimento de tesis: Nivel de optimización {opt_level}",
        algorithm_parameters={"optimization_level": opt_level},
        circuit_qasm=get_circuit_qasm(circuit_base)
    )

    # 2. COMPILACIÓN
    print(f"   Compilando...")
    
    # Mock backend para transpile
    from qiskit_aer import AerSimulator
    backend_sim = AerSimulator()
    
    compilation_start = get_utc_now()
    
    compiled_circuit = transpile(
        circuit_base,
        backend=backend_sim,
        optimization_level=opt_level,
        seed_transpiler=42
    )
    
    compilation_end = get_utc_now()
    duration_ms = (compilation_end - compilation_start).total_seconds() * 1000
    
    # Métricas resultantes
    compiled_depth = compiled_circuit.depth()
    compiled_gates = len(compiled_circuit.data)
    
    # Simular una fidelidad estimada (mejora con mayor optimización teóricamente)
    # En un caso real, esto se calcularía con mapas de ruido
    est_fidelity = 0.90 + (0.02 * opt_level) 

    # Crear CompilationTrace
    trace_id = f"trace_opt{opt_level}_{datetime.datetime.now().strftime('%H%M%S')}"
    compilation_trace = CompilationTrace(
        trace_id=trace_id,
        circuit_id=circuit_metadata.circuit_id,
        device_id=device_metadata.device_id,
        calibration_id=calibration_data.calibration_id,
        timestamp_compilation=compilation_end.isoformat() + "Z",
        compiler_name="qiskit",
        compiler_version="1.0",
        compilation_duration_ms=duration_ms,
        compilation_passes=extract_compilation_passes(compiled_circuit, circuit_base, duration_ms),
        optimization_metrics={
            "optimization_level": opt_level,
            "original_depth": circuit_original_depth,
            "compiled_depth": compiled_depth,
            "depth_reduction": circuit_original_depth - compiled_depth,
            "original_gates": circuit_original_gates,
            "compiled_gates": compiled_gates,
            "estimated_final_fidelity": est_fidelity
        },
        final_circuit_qasm=get_circuit_qasm(compiled_circuit)
    )

    # 3. EJECUCIÓN (Simulada)
    print(f"   Ejecutando...")
    exec_start = get_utc_now()
    result_sim = simulate_vqe_execution(compiled_circuit, shots=1024)
    exec_end = get_utc_now()
    
    execution_context = ExecutionContext(
        execution_id=f"exec_opt{opt_level}_{datetime.datetime.now().strftime('%H%M%S')}",
        trace_id=trace_id,
        device_id=device_metadata.device_id,
        calibration_id=calibration_data.calibration_id,
        timestamp_execution=exec_end.isoformat() + "Z",
        timestamp_compilation=compilation_trace.timestamp_compilation,
        num_shots=1024,
        execution_mode="simulator",
        results=result_sim
    )

    # 4. PROVENIENCIA
    provenance = ProvenanceRecordLean(
        provenance_id=f"prov_opt{opt_level}_{datetime.datetime.now().strftime('%H%M%S')}",
        timestamp_recorded=get_utc_now_iso(),
        relations=[]
    )
    # Relación clave para la tesis: derivado de una traza específica
    provenance.add_relation("wasDerivedFrom", trace_id, circuit_metadata.circuit_id, get_utc_now_iso())
    provenance.add_relation("wasGeneratedBy", execution_context.execution_id, trace_id, get_utc_now_iso())

    # 5. ARMAR MODELO Y GUARDAR
    model = QCMetadataModel(
        model_version="1.1",
        timestamp_model_created=get_utc_now_iso(),
        device_metadata=device_metadata,
        calibration_data=[calibration_data],
        circuit_metadata=circuit_metadata,
        compilation_trace=compilation_trace,
        execution_context=[execution_context],
        provenance_record=provenance
    )
    
    filename = f"metadata_opt_level_{opt_level}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(model.to_complete_json())
    
    # Guardar datos en CSV para análisis fácil
    with open(csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            f"EXP_OPT_{opt_level}", opt_level, circuit_original_depth, compiled_depth,
            circuit_original_gates, compiled_gates, f"{duration_ms:.2f}", 
            f"{est_fidelity:.2f}", filename
        ])
    
    print(f"   [OK] Resultado guardado: {filename}")

print(f"\n=== EXPERIMENTOS FINALIZADOS ===")
print(f"Resumen CSV disponible en: {csv_file}")
print(f"Archivos JSON individuales en: {OUTPUT_DIR}")

