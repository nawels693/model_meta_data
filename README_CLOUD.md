# Captura de Metadatos desde Proveedores en la Nube

Este documento explica cómo usar el sistema de captura de metadatos con proveedores de computación cuántica en la nube como IBM Quantum y AWS Braket.

## 📋 Descripción

El sistema ahora soporta la captura de metadatos desde:
- **IBM Quantum Cloud**: Simuladores y QPUs reales de IBM
- **AWS Braket**: Simuladores y QPUs de AWS (Rigetti, IonQ, OQC, etc.)

## 🚀 Instalación

### Requisitos Adicionales

Para usar IBM Quantum Cloud:
```bash
pip install qiskit-ibm-runtime
```

Para usar AWS Braket:
```bash
pip install amazon-braket-sdk boto3
```

O instala todas las dependencias:
```bash
pip install -r requirements.txt
```

## 🔑 Configuración de Credenciales

### IBM Quantum

1. Obtén un token de API de IBM Quantum:
   - Ve a https://quantum-computing.ibm.com/
   - Inicia sesión o crea una cuenta
   - Ve a "Account" → "API token"
   - Copia tu token

2. Configura el token:
   ```bash
   # Opción 1: Variable de entorno (recomendado)
   export QISKIT_IBM_TOKEN="tu_token_aqui"
   
   # Opción 2: Modificar el script directamente
   # Edita poc_ibm_cloud.py y actualiza IBM_TOKEN
   ```

3. (Opcional) Configura la instancia:
   ```bash
   export QISKIT_IBM_INSTANCE="ibm-q/open/main"
   ```

### AWS Braket

1. Configura las credenciales de AWS:
   ```bash
   # Opción 1: Usar AWS CLI (recomendado)
   aws configure
   
   # Opción 2: Variables de entorno
   export AWS_ACCESS_KEY_ID="tu_access_key"
   export AWS_SECRET_ACCESS_KEY="tu_secret_key"
   export AWS_REGION="us-east-1"
   ```

2. (Opcional) Configura un perfil específico:
   ```bash
   export AWS_PROFILE="mi_perfil"
   ```

## 📝 Uso

### Ejecutar con IBM Quantum Cloud

```bash
python poc_ibm_cloud.py
```

El script:
1. Se conecta a IBM Quantum Cloud
2. Obtiene metadatos del dispositivo seleccionado
3. Obtiene datos de calibración
4. Compila el circuito
5. Ejecuta el circuito en el backend
6. Captura todos los metadatos
7. Exporta a JSON

### Ejecutar con AWS Braket

```bash
python poc_aws_braket.py
```

El script:
1. Se conecta a AWS Braket
2. Obtiene metadatos del dispositivo seleccionado
3. Convierte el circuito de Qiskit a Braket
4. Ejecuta el circuito en el dispositivo
5. Captura todos los metadatos
6. Exporta a JSON

## 🔧 Configuración de Backends

### IBM Quantum

Backends disponibles:
- **Simuladores**:
  - `ibmq_qasm_simulator`: Simulador QASM
  - `ibmq_qasm_simulator_stabilizer`: Simulador estabilizador
- **QPUs reales**:
  - `ibm_brisbane`: 127 qubits
  - `ibm_kyoto`: 127 qubits
  - `ibm_osaka`: 127 qubits
  - (Más disponibles en IBM Quantum)

Para cambiar el backend, edita `poc_ibm_cloud.py`:
```python
BACKEND_NAME = "ibm_brisbane"  # Cambiar aquí
```

### AWS Braket

Device ARNs disponibles:
- **Simuladores**:
  - `arn:aws:braket:::device/quantum-simulator/amazon/sv1`: State Vector
  - `arn:aws:braket:::device/quantum-simulator/amazon/tn1`: Tensor Network
- **QPUs reales**:
  - `arn:aws:braket:us-west-1::device/qpu/rigetti/Aspen-M-3`: Rigetti
  - `arn:aws:braket:us-east-1::device/qpu/ionq/Harmony`: IonQ
  - `arn:aws:braket:eu-west-2::device/qpu/oqc/Lucy`: OQC

Para cambiar el dispositivo, edita `poc_aws_braket.py`:
```python
DEVICE_ARN = "arn:aws:braket:::device/quantum-simulator/amazon/sv1"  # Cambiar aquí
```

## 📊 Salidas

Los scripts generan archivos JSON en el directorio `outputs/` con el siguiente formato:
- `metadata_ibm_cloud_{timestamp}.json`: Para IBM Quantum
- `metadata_aws_braket_{timestamp}.json`: Para AWS Braket

Cada archivo contiene:
- `device_metadata`: Metadatos del dispositivo (capturados desde la nube)
- `calibration_data`: Datos de calibración (capturados desde la nube)
- `circuit_metadata`: Metadatos del circuito
- `compilation_trace`: Traza de compilación
- `execution_context`: Contexto de ejecución (con resultados reales)
- `provenance_record`: Registro de proveniencia

## 🎯 Diferencias con los PoCs Locales

### Metadatos Reales
- Los metadatos del dispositivo se obtienen directamente de la API del proveedor
- Los datos de calibración son reales (para QPUs) o simulados (para simuladores)
- Los resultados de ejecución son reales

### Calibración
- **IBM Quantum**: La calibración se obtiene desde las propiedades del backend
- **AWS Braket**: Para simuladores, la calibración es dummy; para QPUs, se puede obtener información limitada

### Ejecución
- **IBM Quantum**: Usa QiskitRuntimeService para ejecutar
- **AWS Braket**: Convierte el circuito de Qiskit a Braket y ejecuta

## ⚠️ Notas Importantes

1. **Costos**: Los QPUs reales pueden tener costos asociados. Verifica los precios antes de ejecutar.

2. **Colas**: Los QPUs reales pueden tener colas de espera. El tiempo de ejecución puede variar.

3. **Disponibilidad**: Los QPUs reales pueden no estar disponibles en todo momento.

4. **Límites**: Algunos backends tienen límites en el número de shots o qubits.

5. **Credenciales**: Nunca subas tus credenciales a repositorios públicos.

## 🔍 Troubleshooting

### Error: "Token no válido" (IBM Quantum)
- Verifica que tu token sea correcto
- Asegúrate de que el token no haya expirado
- Verifica que tengas acceso a la instancia especificada

### Error: "Credenciales de AWS no encontradas" (AWS Braket)
- Verifica que tengas configuradas las credenciales de AWS
- Ejecuta `aws configure` para configurar las credenciales
- Verifica que tengas permisos para usar AWS Braket

### Error: "Backend no disponible"
- Verifica que el backend esté disponible
- Algunos backends solo están disponibles en ciertas regiones
- Verifica que tengas acceso al backend

### Error: "Timeout en ejecución"
- Los QPUs reales pueden tardar más tiempo
- Verifica la cola del backend
- Aumenta el timeout si es necesario

## 📚 Referencias

- [IBM Quantum Documentation](https://docs.quantum.ibm.com/)
- [AWS Braket Documentation](https://docs.aws.amazon.com/braket/)
- [Qiskit Documentation](https://qiskit.org/documentation/)
- [Braket SDK Documentation](https://github.com/aws/amazon-braket-sdk-python)

## 👤 Autor

Nawel Huenchuleo

## 📄 Licencia

Este proyecto es parte de una investigación académica.

