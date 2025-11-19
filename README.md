# PoC - Modelo de Metadatos QC v1.1

Este proyecto implementa tres Pruebas de Concepto (PoC) progresivas para validar el modelo de metadatos v1.1 para computación cuántica híbrida.

## 📋 Descripción

El objetivo es validar que el modelo de metadatos v1.1 captura, integra y gestiona correctamente los metadatos en un flujo real de computación cuántica híbrida.

### PoCs Implementados

1. **PoC 1 (BÁSICA)**: Circuito VQE simple, 1 ejecución
2. **PoC 2 (INTERMEDIA)**: VQE iterativo, 5 iteraciones
3. **PoC 3 (AVANZADA)**: VQE multiobjetivo, con JIT transpilation

## 🚀 Instalación

### Requisitos

- Python 3.9 o superior
- pip

### Pasos

1. Crear ambiente virtual (recomendado):
```bash
python -m venv poc_env
```

2. Activar ambiente virtual:
   - Windows (PowerShell):
     ```powershell
     .\poc_env\Scripts\Activate.ps1
     ```
   - Linux/Mac:
     ```bash
     source poc_env/bin/activate
     ```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## 📁 Estructura del Proyecto

```
poc/
├── model/
│   ├── __init__.py
│   ├── qc_metadata_model.py          # Clases de entidades
│   └── schema_qc_metadata_v1.1.json  # JSON Schema
├── helpers.py                         # Funciones helper
├── poc1_simple.py                     # PoC 1: VQE Simple
├── poc2_iterative.py                  # PoC 2: VQE Iterativo
├── poc3_jit.py                        # PoC 3: VQE con JIT
├── tests/                             # Tests (pendiente)
├── outputs/                           # Archivos JSON generados
├── requirements.txt                   # Dependencias
└── README.md                          # Este archivo
```

## 🎯 Uso

### Ejecutar PoC 1 (Simple)

```bash
python poc1_simple.py
```

Este PoC ejecuta un circuito VQE simple para H2 (2 qubits) una sola vez y genera un archivo JSON con todos los metadatos capturados.

### Ejecutar PoC 2 (Iterativo)

```bash
python poc2_iterative.py
```

Este PoC ejecuta VQE con 5 iteraciones, validando que `ExperimentSession` agrega correctamente las ejecuciones.

### Ejecutar PoC 3 (JIT)

```bash
python poc3_jit.py
```

Este PoC ejecuta VQE con transpilación JIT (just-in-time), recompilando cuando la calibración expira.

## 📊 Salidas

Todos los PoCs generan archivos JSON en el directorio `outputs/` con el siguiente formato:

```
outputs/metadata_poc{N}_vqe_h2_{timestamp}.json
```

Cada archivo contiene:
- `device_metadata`: Metadatos del dispositivo cuántico
- `calibration_data`: Datos de calibración
- `circuit_metadata`: Metadatos del circuito
- `compilation_trace`: Traza de compilación
- `execution_context`: Contexto de ejecución
- `provenance_record`: Registro de proveniencia
- `experiment_session`: Sesión de experimento (PoC 2 y 3)

## ✅ Validaciones

Cada PoC realiza las siguientes validaciones:

- ✓ Creación correcta de todas las entidades de metadatos
- ✓ Validación de denormalización (mirrors consistentes)
- ✓ Validación contra JSON Schema v1.1
- ✓ Integridad de relaciones PROV
- ✓ Captura completa de linaje de datos

## 🔍 Criterios de Éxito

### Nivel 1: PoC 1 (BÁSICA)
- ✓ Todos los metadatos se capturan
- ✓ JSON Schema validation pasa
- ✓ Archivo JSON es válido y recuperable
- ✓ No hay pérdida de información

### Nivel 2: PoC 2 (INTERMEDIA)
- ✓ Todo de Nivel 1
- ✓ ExperimentSession agrega sin duplicación
- ✓ Convergencia se calcula correctamente
- ✓ Tamaño de archivo es razonable (< 1MB para 5 iteraciones)

### Nivel 3: PoC 3 (AVANZADA)
- ✓ Todo de Nivel 2
- ✓ JIT transpilation se dispara correctamente
- ✓ Multiple CompilationTrace se manejan correctamente
- ✓ Denormalización se valida para cada ejecución

## 🛠️ Tecnologías Utilizadas

- **Python 3.9+**: Lenguaje de programación
- **Qiskit**: Framework de computación cuántica de IBM
- **JSON Schema**: Validación de esquemas JSON
- **SQLite**: (Opcional) Para almacenamiento persistente

## 📝 Notas

- Los PoCs usan simuladores de Qiskit por defecto. Para usar QPUs reales de IBM, necesitarás:
  - Cuenta en IBM Quantum
  - Token de API configurado
  - Modificar el código para usar `QiskitRuntimeService`

- Los tiempos de ejecución son simulados y pueden variar en un entorno real.

## 👤 Autor

Nawel Huenchuleo

## 📄 Licencia

Este proyecto es parte de una investigación académica.

---

**¿Preguntas o problemas?** Revisa el plan completo en `Plan_PoC_Completo.md` para más detalles.

