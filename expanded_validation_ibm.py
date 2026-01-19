#!/usr/bin/env python3
"""
Script de Validación Expandida para Tesis - Arquitectura Híbrida de Metadatos
Cumple con los requerimientos de corrección:
1. Diversidad de circuitos (QFT, Grover, QV)
2. Repetición estadística (5 repeticiones enventanadas)
3. Captura profunda de metadatos (T1, T2, errores en tiempo real)
4. Reporte estadístico
"""

import os
import json
import uuid
import datetime
import time
import numpy as np
from typing import List, Dict, Any, Tuple
from scipy import stats

# Qiskit Imports
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFT, GroverOperator
from qiskit.quantum_info import Statevector
from qiskit.circuit.random import random_circuit
from qiskit_ibm_runtime import QiskitRuntimeService, Session, SamplerV2 as Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

# Importar modelo propio
from model.qc_metadata_model import (
    QCMetadataModel, DeviceMetadata, CircuitMetadata, CalibrationData,
    CompilationTrace, ExecutionContext, ProvenanceRecordLean, ExperimentSession
)

# Configuración Global
REPETITIONS = 5  # Requerimiento: 5 repeticiones por circuito
OPTIMIZATION_LEVEL = 3  # Requerimiento: Forzar compilador

def get_timestamp_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

# --- 1. Generación de Circuitos (Benchmarks) ---

def create_qft_benchmark(num_qubits: int) -> QuantumCircuit:
    """Genera un circuito QFT para probar conectividad."""
    qc = QuantumCircuit(num_qubits)
    # Estado inicial aleatorio simple (superposición) para que haga algo
    for i in range(num_qubits):
        qc.h(i)
    qc.compose(QFT(num_qubits), inplace=True)
    qc.measure_all()
    qc.name = f"QFT_{num_qubits}q"
    return qc

def create_grover_benchmark(num_qubits: int) -> QuantumCircuit:
    """Genera un circuito Grover simple."""
    # Oráculo simple: marca el estado |11...1>
    oracle = QuantumCircuit(num_qubits)
    oracle.cz(0, num_qubits-1) # Difusor simplificado para demo
    
    problem = GroverOperator(oracle)
    qc = QuantumCircuit(num_qubits)
    qc.h(range(num_qubits))
    qc.compose(problem, inplace=True)
    qc.measure_all()
    qc.name = f"Grover_{num_qubits}q"
    return qc

def create_qv_benchmark(num_qubits: int, depth: int) -> QuantumCircuit:
    """Genera un circuito de Volumen Cuántico para estrés."""
    qc = random_circuit(num_qubits, depth, measure=True)
    qc.name = f"QuantumVolume_{num_qubits}q_d{depth}"
    return qc

# --- 2. Lógica de Captura de Metadatos ---

def capture_device_metadata(backend) -> DeviceMetadata:
    """Extrae metadatos estáticos del backend."""
    conf = backend.configuration()
    return DeviceMetadata(
        device_id=backend.name,
        provider="ibm-quantum",
        technology="superconducting",
        backend_name=backend.name,
        num_qubits=conf.n_qubits,
        version=conf.backend_version,
        timestamp_metadata=get_timestamp_iso(),
        connectivity={"coupling_map": conf.coupling_map},
        noise_characteristics={}, # Se llenará dinámicamente en CalibrationData
        operational_parameters={"max_shots": conf.max_shots}
    )

def capture_calibration_snapshot(backend) -> CalibrationData:
    """
    CRÍTICO: Captura T1, T2 y errores del momento exacto usando backend.properties().
    Requerimiento específico de la corrección.
    """
    props = backend.properties()
    if not props:
        print(f"Advertencia: No se pudieron cargar propiedades para {backend.name}")
        return None

    last_update = props.last_update_date.isoformat() if props.last_update_date else get_timestamp_iso()
    
    qubit_props = {}
    for i in range(backend.num_qubits):
        try:
            t1 = props.t1(i)
            t2 = props.t2(i)
            readout_error = props.readout_error(i)
            qubit_props[i] = {
                "T1": t1,
                "T2": t2,
                "readout_error": readout_error,
                "frequency": props.frequency(i)
            }
        except Exception:
            pass # Qubit puede estar inactivo

    return CalibrationData(
        calibration_id=str(uuid.uuid4()),
        device_id=backend.name,
        timestamp_captured=get_timestamp_iso(),
        valid_until=(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)).isoformat(),
        calibration_method="ibm_backend_properties",
        calibration_version="1.0",
        qubit_properties=qubit_props
    )

# --- 3. Ejecución y Validación ---

def run_experiment_batch(service, backend_name: str):
    """Ejecuta la batería de experimentos completa."""
    
    try:
        backend = service.backend(backend_name)
    except Exception as e:
        print(f"Error al obtener backend {backend_name}: {e}")
        return

    print(f"\n=== Iniciando Validación en {backend.name} ===")
    device_meta = capture_device_metadata(backend)
    
    # Definir la batería de circuitos
    benchmarks = [
        create_qft_benchmark(3),
        create_qft_benchmark(4),
        # create_qft_benchmark(5), # Comentado para ahorrar tiempo en demo, descomentar si necesario
        create_grover_benchmark(2),
        create_qv_benchmark(3, depth=5)
    ]

    results_summary = {b.name: [] for b in benchmarks}

    # Sesión global de experimento para agrupar
    session_id = str(uuid.uuid4())
    
    for circuit_orig in benchmarks:
        print(f"\n>> Procesando Benchmark: {circuit_orig.name}")
        
        for rep in range(REPETITIONS):
            print(f"   Repetición {rep+1}/{REPETITIONS}...", end="", flush=True)
            
            # 1. Transpilación
            start_transpile = time.time()
            pm = generate_preset_pass_manager(backend=backend, optimization_level=OPTIMIZATION_LEVEL)
            isa_circuit = pm.run(circuit_orig)
            transpile_dur = (time.time() - start_transpile) * 1000
            
            # Metadatos del circuito y compilación
            circ_meta = CircuitMetadata(
                circuit_id=str(uuid.uuid4()),
                circuit_name=circuit_orig.name,
                algorithm_type=circuit_orig.name.split('_')[0],
                num_qubits=circuit_orig.num_qubits,
                circuit_depth=circuit_orig.depth(),
                num_gates=sum(circuit_orig.count_ops().values()),
                timestamp_created=get_timestamp_iso()
            )
            
            trace_id = str(uuid.uuid4())
            cal_data = capture_calibration_snapshot(backend) # Captura propiedades EN ESTE INSTANTE
            
            comp_trace = CompilationTrace(
                trace_id=trace_id,
                circuit_id=circ_meta.circuit_id,
                device_id=backend.name,
                calibration_id=cal_data.calibration_id,
                timestamp_compilation=get_timestamp_iso(),
                compiler_name="qiskit",
                compiler_version="1.0", # Ajustar según versión real
                compilation_duration_ms=transpile_dur,
                optimization_metrics={
                    "depth_original": circuit_orig.depth(),
                    "depth_transpiled": isa_circuit.depth(),
                    "n_qubits_used": isa_circuit.num_qubits
                }
            )

            # 2. Ejecución
            try:
                # CORRECCIÓN: Usar ejecución directa sin Session (requerido para Open Plan)
                sampler = Sampler(mode=backend)
                job = sampler.run([isa_circuit])
                result = job.result()
                
                # Simulación de cálculo de fidelidad (Placeholder - en real compararías con ideal)
                # Aquí asumimos que si termina sin error, es un éxito operativo,
                # pero guardamos la probabilidad del estado más frecuente como proxy de "calidad"
                pub_result = result[0]
                counts = pub_result.data.meas.get_counts()
                most_freq_bitstring = max(counts, key=counts.get)
                total_shots = sum(counts.values())
                fidelity_proxy = counts[most_freq_bitstring] / total_shots
                
                results_summary[circuit_orig.name].append(fidelity_proxy)
                print(f" OK (Fidelity Proxy: {fidelity_proxy:.4f})")

                # 3. Guardar Metadatos en Modelo
                exec_ctx = ExecutionContext(
                    execution_id=job.job_id(),
                    trace_id=trace_id,
                    device_id=backend.name,
                    calibration_id=cal_data.calibration_id,
                    timestamp_execution=get_timestamp_iso(),
                    timestamp_compilation=comp_trace.timestamp_compilation,
                    num_shots=total_shots,
                    execution_mode="qpu",
                    results={"top_measurement": most_freq_bitstring, "fidelity_proxy": fidelity_proxy}
                )
                
                # Instanciar modelo completo
                full_model = QCMetadataModel(
                    model_version="1.1",
                    timestamp_model_created=get_timestamp_iso(),
                    device_metadata=device_meta,
                    calibration_data=[cal_data],
                    circuit_metadata=circ_meta,
                    compilation_trace=[comp_trace],
                    execution_context=[exec_ctx],
                    provenance_record=ProvenanceRecordLean(
                        provenance_id=str(uuid.uuid4()),
                        timestamp_recorded=get_timestamp_iso()
                    )
                )
                
                # Guardar JSON individual
                filename = f"outputs/metadata_{circuit_orig.name}_rep{rep}_{int(time.time())}.json"
                os.makedirs("outputs", exist_ok=True)
                with open(filename, "w") as f:
                    f.write(full_model.to_complete_json())
                        
            except Exception as e:
                print(f" FALLÓ: {e}")
                
            # Pequeña pausa para no saturar y permitir variación temporal
            time.sleep(2)

    # --- 4. Reporte Final ---
    print("\n" + "="*50)
    print("REPORTE FINAL DE VALIDACIÓN EXPERIMENTAL")
    print("="*50)
    print(f"{'Circuito':<25} | {'Promedio':<10} | {'Std Dev':<10} | {'IC 95%':<15}")
    print("-" * 65)
    
    for name, values in results_summary.items():
        if not values:
            print(f"{name:<25} | {'N/A':<10} | {'N/A':<10} | {'N/A':<15}")
            continue
            
        avg = np.mean(values)
        std = np.std(values)
        sem = std / np.sqrt(len(values)) # Error estándar de la media
        ic = 1.96 * sem # Intervalo de confianza 95%
        
        print(f"{name:<25} | {avg:.4f}     | {std:.4f}     | {avg:.4f} ± {ic:.4f}")
    
    print("="*50)
    print("Los archivos JSON con metadatos completos se han guardado en la carpeta 'outputs/'.")

if __name__ == "__main__":
    # IMPORTANTE: Token hardcodeado para pruebas (reemplazar por gestión segura en prod)
    MY_TOKEN = "TU_API_TOKEN_AQUI"
    
    try:
        service = None
        try:
            # Intentar cargar cuenta guardada
            service = QiskitRuntimeService()
        except Exception:
            pass

        if service is None:
            # Si no cargó, intentar con token hardcodeado
            try:
                service = QiskitRuntimeService(channel="ibm_quantum", token=MY_TOKEN)
            except Exception:
                # Si falla ibm_quantum, intentar ibm_quantum_platform
                service = QiskitRuntimeService(channel="ibm_quantum_platform", token=MY_TOKEN)

        # Intentar buscar el backend menos ocupado con al menos 5 qubits
        print("Buscando backend menos ocupado...")
        backend = service.least_busy(operational=True, simulator=False, min_num_qubits=5)
        run_experiment_batch(service, backend.name)
        
    except Exception as e:
        # Manejo automático de falta de credenciales
        if "Unable to find account" in str(e) or "channel" in str(e):
            print("\n" + "!"*60)
            print(f"ERROR DE AUTENTICACIÓN: {e}")
            print("!"*60)
            print("Necesitas tu API Token. Cópialo de: https://quantum.ibm.com/ (arriba a la derecha)")
            
            token = input("\n>> Por favor, pega tu API Token aquí y presiona Enter: ").strip()
            
            if token:
                try:
                    print("Guardando cuenta en disco...")
                    try:
                         QiskitRuntimeService.save_account(channel="ibm_quantum", token=token, overwrite=True)
                    except Exception:
                         QiskitRuntimeService.save_account(channel="ibm_quantum_platform", token=token, overwrite=True)
                    
                    print("Cuenta guardada correctamente. Reintentando conexión...")
                    service = QiskitRuntimeService()
                    
                    print("Buscando backend menos ocupado...")
                    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=5)
                    run_experiment_batch(service, backend.name)
                except Exception as save_error:
                    print(f"Error al autenticar con ese token: {save_error}")
            else:
                print("No se ingresó token. Cancelando ejecución en hardware real.")
        else:
            print("Error en la inicialización del servicio:")
            print(e)
            print("\nPara probar sin conexión, cambia 'run_experiment_batch' para usar un simulador local.")
