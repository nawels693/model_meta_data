#!/usr/bin/env python3
"""
Script de prueba para encontrar la sintaxis correcta de CX en SpinQ
Ejecutar en Anaconda PowerShell con (spinq_env) activo
"""

from spinqit import Circuit, H, CX, Ry

print("Probando diferentes sintaxis para CX en SpinQ...\n")

# Sintaxis 1: Lista de qubits
print("1. Probando: circuit << (CX, [q[0], q[1]])")
try:
    circ1 = Circuit()
    q1 = circ1.allocateQubits(2)
    circ1 << (H, q1[0])
    circ1 << (CX, [q1[0], q1[1]])
    print("   [OK] Funciona!\n")
    syntax_ok = "[q[0], q[1]]"
except Exception as e:
    print(f"   [ERROR] {e}\n")

# Sintaxis 2: Tupla de qubits
print("2. Probando: circuit << (CX, (q[0], q[1]))")
try:
    circ2 = Circuit()
    q2 = circ2.allocateQubits(2)
    circ2 << (H, q2[0])
    circ2 << (CX, (q2[0], q2[1]))
    print("   [OK] Funciona!\n")
    if 'syntax_ok' not in locals():
        syntax_ok = "(q[0], q[1])"
except Exception as e:
    print(f"   [ERROR] {e}\n")

# Sintaxis 3: Dos argumentos separados
print("3. Probando: circuit << (CX, q[0], q[1])")
try:
    circ3 = Circuit()
    q3 = circ3.allocateQubits(2)
    circ3 << (H, q3[0])
    circ3 << (CX, q3[0], q3[1])
    print("   [OK] Funciona!\n")
    if 'syntax_ok' not in locals():
        syntax_ok = "q[0], q[1]"
except Exception as e:
    print(f"   [ERROR] {e}\n")

# Sintaxis 4: CX como función
print("4. Probando: circuit << CX(q[0], q[1])")
try:
    circ4 = Circuit()
    q4 = circ4.allocateQubits(2)
    circ4 << (H, q4[0])
    circ4 << CX(q4[0], q4[1])
    print("   [OK] Funciona!\n")
    if 'syntax_ok' not in locals():
        syntax_ok = "CX(q[0], q[1])"
except Exception as e:
    print(f"   [ERROR] {e}\n")

# Verificar si hay CNOT en lugar de CX
print("5. Verificando si existe CNOT...")
try:
    from spinqit import CNOT
    print("   [OK] CNOT existe, probando sintaxis...")
    try:
        circ5 = Circuit()
        q5 = circ5.allocateQubits(2)
        circ5 << (H, q5[0])
        circ5 << (CNOT, [q5[0], q5[1]])
        print("   [OK] CNOT funciona con: (CNOT, [q[0], q[1]])\n")
        if 'syntax_ok' not in locals():
            syntax_ok = "CNOT con [q[0], q[1]]"
    except Exception as e:
        print(f"   [ERROR] CNOT falló: {e}\n")
except ImportError:
    print("   [INFO] CNOT no existe\n")

if 'syntax_ok' in locals():
    print(f"\n✓ Sintaxis correcta encontrada: {syntax_ok}")
else:
    print("\n✗ No se encontró sintaxis válida. Revisar documentación de SpinQ.")

