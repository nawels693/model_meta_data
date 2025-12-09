# Script de prueba para verificar sintaxis de SpinQ
# Ejecutar en Anaconda PowerShell con (spinq_env) activo

from spinqit import Circuit, H, CX, Ry

# Probar diferentes sintaxis para CX
circ = Circuit()
q = circ.allocateQubits(2)

# Sintaxis 1: Tupla de qubits
try:
    circ1 = Circuit()
    q1 = circ1.allocateQubits(2)
    circ1 << (H, q1[0])
    circ1 << (CX, (q1[0], q1[1]))
    print("[OK] Sintaxis 1 funciona: (CX, (q[0], q[1]))")
except Exception as e:
    print(f"[ERROR] Sintaxis 1 falló: {e}")

# Sintaxis 2: Lista de qubits
try:
    circ2 = Circuit()
    q2 = circ2.allocateQubits(2)
    circ2 << (H, q2[0])
    circ2 << (CX, [q2[0], q2[1]])
    print("[OK] Sintaxis 2 funciona: (CX, [q[0], q[1]])")
except Exception as e:
    print(f"[ERROR] Sintaxis 2 falló: {e}")

# Sintaxis 3: CX como función
try:
    circ3 = Circuit()
    q3 = circ3.allocateQubits(2)
    circ3 << (H, q3[0])
    circ3 << CX(q3[0], q3[1])
    print("[OK] Sintaxis 3 funciona: CX(q[0], q[1])")
except Exception as e:
    print(f"[ERROR] Sintaxis 3 falló: {e}")

# Sintaxis 4: Dos argumentos separados
try:
    circ4 = Circuit()
    q4 = circ4.allocateQubits(2)
    circ4 << (H, q4[0])
    circ4 << (CX, q4[0], q4[1])
    print("[OK] Sintaxis 4 funciona: (CX, q[0], q[1])")
except Exception as e:
    print(f"[ERROR] Sintaxis 4 falló: {e}")

