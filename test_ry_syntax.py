#!/usr/bin/env python3
"""
Script de prueba para verificar sintaxis de Ry en SpinQ
"""

from spinqit import Circuit, H, CX, Ry

print("Probando diferentes sintaxis para Ry en SpinQ...\n")

# Sintaxis 1: Ry como función que retorna un gate
print("1. Probando: circuit << (Ry(0.5), q[0])")
try:
    circ1 = Circuit()
    q1 = circ1.allocateQubits(2)
    gate_ry = Ry(0.5)
    circ1 << (gate_ry, q1[0])
    print("   [OK] Funciona: Ry(0.5) crea un gate, luego (gate, q[0])\n")
    syntax_ok = "Ry(0.5) crea gate, luego (gate, q[0])"
except Exception as e:
    print(f"   [ERROR] {e}\n")

# Sintaxis 2: Ry directamente
print("2. Probando: circuit << (Ry, q[0]) con parámetro separado")
try:
    circ2 = Circuit()
    q2 = circ2.allocateQubits(2)
    # Intentar pasar parámetro de otra forma
    circ2 << (Ry, q2[0], 0.5)
    print("   [OK] Funciona: (Ry, q[0], 0.5)\n")
    if 'syntax_ok' not in locals():
        syntax_ok = "(Ry, q[0], 0.5)"
except Exception as e:
    print(f"   [ERROR] {e}\n")

# Sintaxis 3: Ry como tupla con parámetro
print("3. Probando: circuit << ((Ry, 0.5), q[0])")
try:
    circ3 = Circuit()
    q3 = circ3.allocateQubits(2)
    circ3 << ((Ry, 0.5), q3[0])
    print("   [OK] Funciona: ((Ry, 0.5), q[0])\n")
    if 'syntax_ok' not in locals():
        syntax_ok = "((Ry, 0.5), q[0])"
except Exception as e:
    print(f"   [ERROR] {e}\n")

if 'syntax_ok' in locals():
    print(f"\n✓ Sintaxis correcta: {syntax_ok}")
else:
    print("\n✗ No se encontró sintaxis válida")

