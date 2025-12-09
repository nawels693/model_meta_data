# Script para corregir el problema de numpy en SpinQ
# Ejecutar en Anaconda PowerShell con (spinq_env) activo

# 1. Desinstalar numpy 1.21.0 (incompatible)
# pip uninstall numpy -y

# 2. Reinstalar numpy compatible (>=1.23, <2.3)
# pip install "numpy>=1.23,<2.3"

# 3. Verificar que funciona
# python -c "import spinqit; print('[OK] spinqit funciona')"

