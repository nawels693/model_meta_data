#!/usr/bin/env python3
"""
Script para ejecutar todos los PoCs en secuencia
"""

import sys
import subprocess
import os

def run_poc(poc_file):
    """Ejecuta un PoC y retorna True si fue exitoso"""
    print(f"\n{'='*60}")
    print(f"Ejecutando {poc_file}...")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, poc_file],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            check=True
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error ejecutando {poc_file}: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Error inesperado: {e}")
        return False

def main():
    """Ejecuta todos los PoCs en orden"""
    pocs = [
        "poc1_simple.py",
        "poc2_iterative.py",
        "poc3_jit.py"
    ]
    
    results = {}
    
    for poc in pocs:
        if os.path.exists(poc):
            results[poc] = run_poc(poc)
        else:
            print(f"⚠ Archivo {poc} no encontrado, saltando...")
            results[poc] = False
    
    # Resumen
    print(f"\n{'='*60}")
    print("RESUMEN DE EJECUCIÓN")
    print(f"{'='*60}\n")
    
    for poc, success in results.items():
        status = "✓ PASÓ" if success else "✗ FALLÓ"
        print(f"  {poc}: {status}")
    
    all_passed = all(results.values())
    print(f"\n{'='*60}")
    if all_passed:
        print("✓ TODOS LOS PoCs COMPLETADOS EXITOSAMENTE")
    else:
        print("✗ ALGUNOS PoCs FALLARON")
    print(f"{'='*60}\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

