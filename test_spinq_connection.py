#!/usr/bin/env python3
"""
Script de prueba de conexión a SpinQ NMR Quantum Computer
Verifica que podemos conectarnos antes de ejecutar el PoC completo
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from spinqit import get_nmr, get_compiler, Circuit, NMRConfig
from spinqit import H

# Datos de conexión (según la imagen CASTOR)
SPINQ_IP = "172.27.52.229"
SPINQ_PORT = 8989
SPINQ_USERNAME = "SpinQ001"  # Ajustar si es diferente
SPINQ_PASSWORD = "123456"    # Ajustar si es diferente

print("="*60)
print("PRUEBA DE CONEXIÓN A SPINQ NMR QUANTUM COMPUTER")
print("="*60)
print(f"\nConfiguración:")
print(f"  IP: {SPINQ_IP}")
print(f"  Puerto: {SPINQ_PORT}")
print(f"  Usuario: {SPINQ_USERNAME}")
print(f"  Contraseña: {'*' * len(SPINQ_PASSWORD)}")

# 1. Verificar que spinqit funciona
print("\n[PASO 1] Verificando que spinqit está instalado...")
try:
    from spinqit import get_nmr, get_compiler, Circuit, NMRConfig, H
    print("  [OK] spinqit importado correctamente")
except ImportError as e:
    print(f"  [ERROR] No se puede importar spinqit: {e}")
    sys.exit(1)

# 2. Inicializar el motor y compilador
print("\n[PASO 2] Inicializando motor NMR y compilador...")
try:
    engine = get_nmr()
    comp = get_compiler("native")
    print("  [OK] Motor y compilador inicializados")
except Exception as e:
    print(f"  [ERROR] Error al inicializar: {e}")
    sys.exit(1)

# 3. Crear un circuito simple de prueba
print("\n[PASO 3] Creando circuito de prueba simple...")
try:
    circ = Circuit()
    q = circ.allocateQubits(2)
    circ << (H, q[0])
    circ << (H, q[1])
    print("  [OK] Circuito creado (2 qubits, 2 compuertas H)")
except Exception as e:
    print(f"  [ERROR] Error al crear circuito: {e}")
    sys.exit(1)

# 4. Compilar el circuito
print("\n[PASO 4] Compilando circuito...")
try:
    exe = comp.compile(circ, 0)
    print("  [OK] Circuito compilado")
except Exception as e:
    print(f"  [ERROR] Error al compilar: {e}")
    sys.exit(1)

# 5. Configurar conexión
print("\n[PASO 5] Configurando conexión al dispositivo...")
try:
    config = NMRConfig()
    config.configure_shots(10)  # Solo 10 shots para prueba rápida
    config.configure_ip(SPINQ_IP)
    config.configure_port(SPINQ_PORT)
    config.configure_account(SPINQ_USERNAME, SPINQ_PASSWORD)
    config.configure_task("Test-Connection", "Test-Connection")
    print("  [OK] Configuración de conexión completada")
except Exception as e:
    print(f"  [ERROR] Error al configurar conexión: {e}")
    sys.exit(1)

# 6. Intentar ejecutar (prueba de conexión)
print("\n[PASO 6] Intentando conectar y ejecutar en el dispositivo...")
print("  (Esto puede tardar unos segundos...)")
try:
    result = engine.execute(exe, config)
    print("  [OK] ¡Conexión exitosa!")
    print(f"\n  Resultados:")
    if hasattr(result, 'probabilities'):
        probs = result.probabilities
        print(f"    Probabilidades: {probs}")
    else:
        print(f"    Resultado: {result}")
    
    print("\n" + "="*60)
    print("✓ CONEXIÓN EXITOSA - El dispositivo está funcionando")
    print("="*60)
    print("\nPuedes ejecutar el PoC completo con:")
    print("  python poc_spinq.py")
    
except Exception as e:
    error_msg = str(e)
    print(f"  [ERROR] Error al ejecutar: {error_msg}")
    
    # Detectar errores específicos
    if "USB" in error_msg or "serial port" in error_msg or "not connected" in error_msg:
        print("\n" + "="*60)
        print("⚠ PROBLEMA EN EL SERVIDOR SPINQ")
        print("="*60)
        print("\n✓ Tu conexión vía IP funciona correctamente")
        print("✗ El servidor SpinQ no puede comunicarse con el hardware cuántico")
        print("\nEste error viene DEL SERVIDOR (no de tu código):")
        print("  - El servidor en 172.27.52.229 está funcionando")
        print("  - Pero el hardware cuántico físico conectado al servidor no está listo")
        print("\nPosibles causas:")
        print("  1. El hardware cuántico no está encendido")
        print("  2. El cable USB/serial entre servidor y hardware no está conectado")
        print("  3. El hardware no ha terminado de inicializarse")
        print("\nSolución:")
        print("  - Verificar en el panel CASTOR del servidor el estado del hardware")
        print("  - Esperar unos minutos después de encender el hardware")
        print("  - Contactar al administrador del servidor si el problema persiste")
        print("\nUna vez que el servidor reporte que el hardware está listo,")
        print("ejecuta este script nuevamente.")
    elif "not ready" in error_msg.lower():
        print("\n⚠ El dispositivo no está listo para recibir tareas")
        print("  - Espera unos segundos y vuelve a intentar")
        print("  - Verifica en el panel CASTOR el estado del dispositivo")
    else:
        print("\n  Posibles causas:")
        print("    - El dispositivo no está encendido")
        print("    - IP o puerto incorrectos")
        print("    - Credenciales incorrectas")
        print("    - Problema de red/firewall")
        print("    - El dispositivo está ocupado")
    
    import traceback
    traceback.print_exc()
    sys.exit(1)

