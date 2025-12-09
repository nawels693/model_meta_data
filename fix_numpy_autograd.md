# Solución para el problema de numpy con autograd en spinqit
# autograd requiere numpy < 2.0 (porque usa numpy.msort que fue eliminado)
# Pero matplotlib/scipy requieren numpy >= 1.23
# Solución: numpy 1.26.x (última versión 1.x compatible)

# Ejecutar en Anaconda PowerShell con (spinq_env) activo:

# 1. Desinstalar numpy actual
# pip uninstall numpy -y

# 2. Instalar numpy 1.26.4 (última versión 1.x, compatible con todo)
# pip install numpy==1.26.4

# 3. Verificar
# python -c "import spinqit; print('[OK] spinqit funciona')"

