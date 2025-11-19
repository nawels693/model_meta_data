#!/usr/bin/env python3
"""
Archivo de configuración de ejemplo para proveedores en la nube
Copia este archivo a config.py y actualiza con tus credenciales
"""

# ============================================================
# IBM QUANTUM
# ============================================================

# Token de API de IBM Quantum
# Puedes obtenerlo en: https://quantum-computing.ibm.com/
IBM_QUANTUM_TOKEN = "tu_token_aqui"

# Instancia de IBM Quantum (opcional)
# Por ejemplo: "ibm-q/open/main"
IBM_QUANTUM_INSTANCE = None

# Backend por defecto
# Simuladores: "ibmq_qasm_simulator", "ibmq_qasm_simulator_stabilizer"
# QPUs reales: "ibm_brisbane", "ibm_kyoto", "ibm_osaka", etc.
IBM_QUANTUM_BACKEND = "ibmq_qasm_simulator"

# ============================================================
# AWS BRAKET
# ============================================================

# Perfil de AWS (opcional)
# Si no se especifica, se usan las credenciales por defecto de AWS
AWS_PROFILE = None

# Región de AWS
AWS_REGION = "us-east-1"

# Device ARN por defecto
# Simuladores:
#   - "arn:aws:braket:::device/quantum-simulator/amazon/sv1" (State Vector)
#   - "arn:aws:braket:::device/quantum-simulator/amazon/tn1" (Tensor Network)
# QPUs reales:
#   - "arn:aws:braket:us-west-1::device/qpu/rigetti/Aspen-M-3" (Rigetti)
#   - "arn:aws:braket:us-east-1::device/qpu/ionq/Harmony" (IonQ)
#   - "arn:aws:braket:eu-west-2::device/qpu/oqc/Lucy" (OQC)
AWS_BRAKET_DEVICE_ARN = "arn:aws:braket:::device/quantum-simulator/amazon/sv1"

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

# Número de shots por defecto
DEFAULT_SHOTS = 1024

# Nivel de optimización por defecto (para Qiskit)
DEFAULT_OPTIMIZATION_LEVEL = 3

# Directorio de salida
OUTPUT_DIR = "outputs"


