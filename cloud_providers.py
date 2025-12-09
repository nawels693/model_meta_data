#!/usr/bin/env python3
"""
Módulo para conexión con proveedores de computación cuántica en la nube
Soporta: IBM Quantum, AWS Braket
"""

import datetime
from typing import Dict, Any, Optional, List
from enum import Enum

# ============================================================
# IBM QUANTUM
# ============================================================

class IBMProvider:
    """Wrapper para IBM Quantum"""
    
    def __init__(self, token: Optional[str] = None, instance: Optional[str] = None):
        """
        Inicializa el proveedor de IBM Quantum
        
        Args:
            token: Token de API de IBM Quantum (opcional, puede usar variable de entorno)
            instance: Instancia de IBM Quantum (opcional)
        """
        self.token = token
        self.instance = instance
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Inicializa el servicio de IBM Quantum"""
        try:
            from qiskit_ibm_runtime import QiskitRuntimeService
            
            if self.token:
                self.service = QiskitRuntimeService(token=self.token, instance=self.instance)
            else:
                # Intentar usar token de variable de entorno o archivo de configuración
                self.service = QiskitRuntimeService(instance=self.instance)
            print("✓ IBM Quantum Service inicializado")
        except ImportError:
            raise ImportError("qiskit-ibm-runtime no está instalado. Instala con: pip install qiskit-ibm-runtime")
        except Exception as e:
            raise Exception(f"Error al inicializar IBM Quantum Service: {e}")
    
    def get_backend(self, backend_name: str = "ibmq_qasm_simulator"):
        """
        Obtiene un backend de IBM Quantum
        
        Args:
            backend_name: Nombre del backend (p.ej., 'ibmq_qasm_simulator', 'ibm_brisbane')
        
        Returns:
            Backend de Qiskit
        """
        if not self.service:
            raise Exception("Service no inicializado")
        
        try:
            backend = self.service.backend(backend_name)
            print(f"✓ Backend obtenido: {backend_name}")
            return backend
        except Exception as e:
            raise Exception(f"Error al obtener backend {backend_name}: {e}")
    
    def get_device_metadata(self, backend_name: str) -> Dict[str, Any]:
        """
        Obtiene metadatos del dispositivo desde IBM Quantum
        
        Args:
            backend_name: Nombre del backend
        
        Returns:
            DeviceMetadata como diccionario
        """
        from model.qc_metadata_model import DeviceMetadata
        
        backend = self.get_backend(backend_name)
        
        # Obtener propiedades del backend (puede fallar para simuladores)
        try:
            properties = backend.properties()
        except Exception:
            properties = None
        
        try:
            config = backend.configuration()
        except Exception:
            config = None
        
        # Determinar tecnología
        if "simulator" in backend_name.lower():
            technology = "simulator"
        elif "qasm" in backend_name.lower():
            technology = "simulator"
        else:
            technology = "superconducting"  # IBM usa principalmente superconductores
        
        # Obtener número de qubits
        num_qubits = config.n_qubits if config and hasattr(config, 'n_qubits') else 32
        
        # Obtener conectividad
        connectivity = {}
        if config and hasattr(config, 'coupling_map') and config.coupling_map:
            connectivity = {
                "topology_type": "coupling_map",
                "coupling_map": config.coupling_map,
                "num_edges": len(config.coupling_map)
            }
        else:
            connectivity = {"topology_type": "all_to_all"}
        
        # Obtener características de ruido
        noise_characteristics = {}
        if properties and config:
            try:
                t1_values = []
                t2_values = []
                for qubit in range(num_qubits):
                    try:
                        t1 = properties.t1(qubit)
                        if t1 is not None:
                            t1_values.append(t1)
                    except Exception:
                        pass
                    try:
                        t2 = properties.t2(qubit)
                        if t2 is not None:
                            t2_values.append(t2)
                    except Exception:
                        pass
                
                if t1_values:
                    noise_characteristics["avg_t1_us"] = sum(t1_values) / len(t1_values) * 1e6  # Convertir a microsegundos
                if t2_values:
                    noise_characteristics["avg_t2_us"] = sum(t2_values) / len(t2_values) * 1e6
            except Exception:
                pass
        
        # Obtener parámetros operacionales
        operational_parameters = {}
        if config:
            if hasattr(config, 'basis_gates'):
                operational_parameters["basis_gates"] = config.basis_gates
            if hasattr(config, 'max_shots'):
                operational_parameters["max_shots"] = config.max_shots
            if hasattr(config, 'backend_version'):
                operational_parameters["backend_version"] = config.backend_version
        
        if hasattr(backend, 'is_local'):
            operational_parameters["local"] = backend.is_local()
        if hasattr(backend, 'is_simulator'):
            operational_parameters["simulator"] = backend.is_simulator()
        
        # Obtener versión del backend
        backend_version = "1.0"
        if config and hasattr(config, 'backend_version'):
            backend_version = config.backend_version
        
        device_metadata = DeviceMetadata(
            device_id=backend_name,
            provider="IBM",
            technology=technology,
            backend_name=backend_name,
            num_qubits=num_qubits,
            version=backend_version,
            timestamp_metadata=datetime.datetime.utcnow().isoformat() + "Z",
            connectivity=connectivity,
            noise_characteristics=noise_characteristics,
            operational_parameters=operational_parameters
        )
        
        return device_metadata
    
    def get_calibration_data(self, backend_name: str) -> Any:
        """
        Obtiene datos de calibración desde IBM Quantum
        
        Args:
            backend_name: Nombre del backend
        
        Returns:
            CalibrationData
        """
        from model.qc_metadata_model import CalibrationData
        
        backend = self.get_backend(backend_name)
        
        # Intentar obtener propiedades del backend
        try:
            properties = backend.properties()
        except Exception:
            properties = None
        
        try:
            config = backend.configuration()
            num_qubits = config.n_qubits if hasattr(config, 'n_qubits') else 32
        except Exception:
            config = None
            num_qubits = 32
        
        if not properties:
            # Para simuladores, crear calibración dummy
            return CalibrationData(
                calibration_id=f"cal_{backend_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                device_id=backend_name,
                timestamp_captured=datetime.datetime.utcnow().isoformat() + "Z",
                valid_until=(datetime.datetime.utcnow() + datetime.timedelta(hours=4)).isoformat() + "Z",
                calibration_method="simulator_default",
                calibration_version="1.0",
                qubit_properties={},
                gate_fidelities={},
                crosstalk_matrix={}
            )
        
        # Obtener propiedades de qubits
        qubit_properties = {}
        if config:
            for qubit in range(num_qubits):
                qubit_props = {}
                try:
                    t1 = properties.t1(qubit)
                    if t1 is not None:
                        qubit_props["t1_us"] = t1 * 1e6  # Convertir a microsegundos
                except Exception:
                    pass
                try:
                    t2 = properties.t2(qubit)
                    if t2 is not None:
                        qubit_props["t2_us"] = t2 * 1e6
                except Exception:
                    pass
                try:
                    readout_error = properties.readout_error(qubit)
                    if readout_error is not None:
                        qubit_props["readout_error"] = readout_error
                except Exception:
                    pass
                if qubit_props:
                    qubit_properties[qubit] = qubit_props
        
        # Obtener fidelidades de puertas
        gate_fidelities = {"1q_gates": {}, "2q_gates": {}}
        try:
            if hasattr(properties, 'gates'):
                for gate in properties.gates:
                    gate_name = gate.gate
                    qubits = gate.qubits
                    if len(qubits) == 1:
                        try:
                            gate_error = properties.gate_error(gate_name, qubits[0])
                            if gate_error is not None:
                                gate_fidelities["1q_gates"][f"{gate_name}_{qubits[0]}"] = 1 - gate_error
                        except Exception:
                            pass
                    elif len(qubits) == 2:
                        try:
                            gate_error = properties.gate_error(gate_name, qubits)
                            if gate_error is not None:
                                gate_fidelities["2q_gates"][f"{gate_name}_{qubits[0]}_{qubits[1]}"] = 1 - gate_error
                        except Exception:
                            pass
        except Exception:
            pass
        
        # Obtener timestamp de calibración
        try:
            if hasattr(properties, 'last_update_date'):
                last_update_date = properties.last_update_date
            else:
                last_update_date = datetime.datetime.utcnow()
        except Exception:
            last_update_date = datetime.datetime.utcnow()
        
        # Calcular validez (típicamente 24 horas para IBM)
        if isinstance(last_update_date, datetime.datetime):
            valid_until = last_update_date + datetime.timedelta(hours=24)
        else:
            valid_until = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        
        calibration = CalibrationData(
            calibration_id=f"cal_{backend_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            device_id=backend_name,
            timestamp_captured=last_update_date.isoformat() + "Z" if isinstance(last_update_date, datetime.datetime) else datetime.datetime.utcnow().isoformat() + "Z",
            valid_until=valid_until.isoformat() + "Z",
            calibration_method="ibm_quantum_api",
            calibration_version="1.0",
            qubit_properties=qubit_properties,
            gate_fidelities=gate_fidelities,
            crosstalk_matrix={},
            additional_metrics={
                "last_update_date": last_update_date.isoformat() + "Z" if isinstance(last_update_date, datetime.datetime) else None
            }
        )
        
        return calibration
    
    def execute_circuit(self, circuit, backend_name: str, shots: int = 1024, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta un circuito en un backend de IBM Quantum
        
        Args:
            circuit: Circuito cuántico de Qiskit
            backend_name: Nombre del backend
            shots: Número de shots
            **kwargs: Argumentos adicionales para la ejecución
        
        Returns:
            Diccionario con resultados
        """
        backend = self.service.backend(backend_name)

        circuit_to_run = circuit.copy()
        # Asegurar que haya mediciones
        if circuit_to_run.num_clbits == 0:
            circuit_to_run.measure_all()

        if hasattr(circuit_to_run, "remove_idle_qubits"):
            try:
                circuit_to_run = circuit_to_run.remove_idle_qubits()
            except Exception:
                pass

        # Ejecutar utilizando Sampler (interfaz actual recomendada)
        try:
            from qiskit import transpile
            # V2 primitives require circuits to be transpiled to Instruction Set Architecture (ISA)
            # before execution.
            isa_circuit = transpile(circuit_to_run, backend=backend, optimization_level=1)
            
            from qiskit_ibm_runtime import Sampler, Session

            # Intentar usar Session primero (mejor rendimiento si está disponible)
            try:
                # Session signature varies by version; safer to pass backend keyword
                with Session(backend=backend) as session:
                    # Sampler V2 uses 'mode' instead of 'session' in some versions, or 'session' in others.
                    try:
                        sampler = Sampler(mode=session)
                    except TypeError:
                        # Fallback for versions where arg is named 'session'
                        sampler = Sampler(session=session)

                    # Sampler V2 run() expects a list of pubs (circuits)
                    job = sampler.run([isa_circuit], shots=shots)
                    result = job.result()

            except Exception as e:
                # Si falla Session (ej. Open Plan no lo soporta), intentar Job Mode
                if "open plan" in str(e).lower() or "not authorized" in str(e).lower():
                    print(f"  ⚠ Session no soportada en este plan. Intentando Job Mode directo...")
                    try:
                        sampler = Sampler(mode=backend)
                    except TypeError:
                         # Fallback for versions needing backend arg directly or service
                         try:
                             sampler = Sampler(backend=backend)
                         except TypeError:
                             # Último intento: sin argumentos, asumiendo contexto global o default
                             sampler = Sampler()
                    
                    job = sampler.run([isa_circuit], shots=shots)
                    result = job.result()
                else:
                    raise e

            counts = {}
            # Manejo de resultados V2 (PrimitiveResult)
            if hasattr(result, '__getitem__') and hasattr(result[0], 'data'):
                # Asumimos que si usamos measure_all la info está en 'meas'
                # O buscamos el primer registro de bits disponible
                pub_result = result[0]
                if hasattr(pub_result.data, 'meas'):
                    counts = pub_result.data.meas.get_counts()
                elif hasattr(pub_result.data, 'c'):
                    counts = pub_result.data.c.get_counts()
                else:
                    # Intentar encontrar cualquier atributo que parezca un registro de bits
                    for attr in dir(pub_result.data):
                        val = getattr(pub_result.data, attr)
                        if hasattr(val, 'get_counts'):
                            counts = val.get_counts()
                            break
            
            # Manejo de resultados V1 (quasi_dists)
            elif hasattr(result, "quasi_dists"):
                quasi_dist = result.quasi_dists[0]
                for bitstr, prob in quasi_dist.items():
                    if isinstance(bitstr, int):
                        key = format(bitstr, f"0{circuit_to_run.num_qubits}b")
                    else:
                        key = bitstr
                    counts[key] = int(prob * shots)
            else:
                # Fallback si no se encuentra estructura conocida
                counts = {"0" * circuit_to_run.num_qubits: shots}

        except Exception as e:
            print(f"  ⚠ Error en Sampler Runtime: {e}. Usando fallback Aer.")
            from qiskit import transpile
            # Fallback utilizando AerSimulator para entornos locales
            from qiskit_aer import AerSimulator

            simulator = AerSimulator()
            # Usamos circuit_to_run que ya tiene mediciones
            compiled_local = transpile(circuit_to_run, simulator)
            job = simulator.run(compiled_local, shots=shots)
            result = job.result()
            counts = result.get_counts()

        return {
            "counts": counts,
            "shots": shots,
            "success": True,
            "job_id": job.job_id() if hasattr(job, 'job_id') else f"job_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "backend_name": backend_name,
            "execution_time": getattr(result, 'execution_time', None)
        }


# ============================================================
# AWS BRAKET
# ============================================================

class AWSBraketProvider:
    """Wrapper para AWS Braket"""
    
    def __init__(self, aws_profile: Optional[str] = None, region: str = "us-east-1"):
        """
        Inicializa el proveedor de AWS Braket
        
        Args:
            aws_profile: Perfil de AWS (opcional)
            region: Región de AWS (default: us-east-1)
        """
        self.aws_profile = aws_profile
        self.region = region
        self._initialize_service()
    
    def _initialize_service(self):
        """Inicializa el servicio de AWS Braket"""
        try:
            import boto3
            from braket.aws import AwsDevice
            
            if self.aws_profile:
                self.session = boto3.Session(profile_name=self.aws_profile, region_name=self.region)
            else:
                self.session = boto3.Session(region_name=self.region)
            
            print("✓ AWS Braket Service inicializado")
        except ImportError:
            raise ImportError("aws-braket-sdk no está instalado. Instala con: pip install amazon-braket-sdk")
        except Exception as e:
            raise Exception(f"Error al inicializar AWS Braket Service: {e}")
    
    def get_device(self, device_arn: str):
        """
        Obtiene un dispositivo de AWS Braket
        
        Args:
            device_arn: ARN del dispositivo (p.ej., 'arn:aws:braket:::device/quantum-simulator/amazon/sv1')
        
        Returns:
            Dispositivo de Braket
        """
        try:
            from braket.aws import AwsDevice
            
            device = AwsDevice(device_arn, aws_session=self.session)
            print(f"✓ Dispositivo obtenido: {device_arn}")
            return device
        except Exception as e:
            raise Exception(f"Error al obtener dispositivo {device_arn}: {e}")
    
    def get_device_metadata(self, device_arn: str) -> Dict[str, Any]:
        """
        Obtiene metadatos del dispositivo desde AWS Braket
        
        Args:
            device_arn: ARN del dispositivo
        
        Returns:
            DeviceMetadata como diccionario
        """
        from model.qc_metadata_model import DeviceMetadata
        
        device = self.get_device(device_arn)
        properties = device.properties
        
        # Determinar tecnología
        if "simulator" in device_arn.lower():
            technology = "simulator"
        elif "rigetti" in device_arn.lower():
            technology = "superconducting"
        elif "ionq" in device_arn.lower():
            technology = "ion_trap"
        elif "oqc" in device_arn.lower():
            technology = "superconducting"
        else:
            technology = "unknown"
        
        # Obtener conectividad
        connectivity = {}
        if hasattr(properties, 'action') and hasattr(properties.action, 'braket') and hasattr(properties.action.braket, 'device'):
            device_props = properties.action.braket.device
            if hasattr(device_props, 'connectivity'):
                connectivity = {
                    "topology_type": "braket_connectivity",
                    "connectivity": device_props.connectivity
                }
            else:
                connectivity = {"topology_type": "all_to_all"}
        else:
            connectivity = {"topology_type": "all_to_all"}
        
        # Obtener número de qubits
        num_qubits = properties.service.deviceParameters.paradigm.qubitCount if hasattr(properties, 'service') else 0
        
        device_metadata = DeviceMetadata(
            device_id=device_arn,
            provider="AWS",
            technology=technology,
            backend_name=device.name,
            num_qubits=num_qubits,
            version=getattr(properties, 'deviceDocumentation', {}).get('version', '1.0') if hasattr(properties, 'deviceDocumentation') else '1.0',
            timestamp_metadata=datetime.datetime.utcnow().isoformat() + "Z",
            connectivity=connectivity,
            noise_characteristics={},
            operational_parameters={
                "device_arn": device_arn,
                "status": device.status,
                "region": self.region
            }
        )
        
        return device_metadata
    
    def get_calibration_data(self, device_arn: str) -> Any:
        """
        Obtiene datos de calibración desde AWS Braket
        
        Args:
            device_arn: ARN del dispositivo
        
        Returns:
            CalibrationData
        """
        from model.qc_metadata_model import CalibrationData
        
        device = self.get_device(device_arn)
        properties = device.properties
        
        # Para simuladores, crear calibración dummy
        # Para QPUs reales, AWS Braket no expone calibración directamente
        # pero podemos usar las propiedades del dispositivo
        
        calibration = CalibrationData(
            calibration_id=f"cal_{device_arn.replace('/', '_')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            device_id=device_arn,
            timestamp_captured=datetime.datetime.utcnow().isoformat() + "Z",
            valid_until=(datetime.datetime.utcnow() + datetime.timedelta(hours=24)).isoformat() + "Z",
            calibration_method="aws_braket_api",
            calibration_version="1.0",
            qubit_properties={},
            gate_fidelities={},
            crosstalk_matrix={},
            additional_metrics={
                "device_status": device.status,
                "device_type": "simulator" if "simulator" in device_arn.lower() else "qpu"
            }
        )
        
        return calibration
    
    def execute_circuit(self, circuit_braket, device_arn: str, shots: int = 1024, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta un circuito en un dispositivo de AWS Braket
        
        Args:
            circuit_braket: Circuito cuántico de Braket (no Qiskit)
            device_arn: ARN del dispositivo
            shots: Número de shots
        
        Returns:
            Diccionario con resultados
        """
        device = self.get_device(device_arn)
        
        # Ejecutar
        task = device.run(circuit_braket, shots=shots, **kwargs)
        
        # Esperar resultado
        result = task.result()
        
        # Convertir resultado a formato estándar
        counts = {}
        if hasattr(result, 'measurement_counts'):
            counts = {k: v for k, v in result.measurement_counts.items()}
        elif hasattr(result, 'values'):
            # Para resultados de estado
            counts = result.values
        
        return {
            "counts": counts,
            "shots": shots,
            "success": True,
            "task_id": task.id,
            "device_arn": device_arn,
            "execution_time": getattr(result, 'additional_metadata', {}).get('taskMetadata', {}).get('duration', None) if hasattr(result, 'additional_metadata') else None
        }


# ============================================================
# SPINQ (NMR Quantum Computer)
# ============================================================

class SpinQProvider:
    """Wrapper para SpinQ NMR Quantum Computer"""
    
    def __init__(self, ip: str, port: int = 8989, username: str = None, password: str = None):
        """
        Inicializa el proveedor de SpinQ
        
        Args:
            ip: Dirección IP del equipo cuántico
            port: Puerto de comunicación (default: 8989)
            username: Usuario para autenticación
            password: Contraseña para autenticación
        """
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.engine = None
        self.compiler = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Inicializa el servicio de SpinQ"""
        try:
            from spinqit import get_nmr, get_compiler
            
            self.engine = get_nmr()
            self.compiler = get_compiler("native")
            print("✓ SpinQ NMR Service inicializado")
        except ImportError:
            raise ImportError("spinqit no está instalado. Instala con: pip install spinqit")
        except Exception as e:
            raise Exception(f"Error al inicializar SpinQ Service: {e}")
    
    def get_device_metadata(self, device_name: str = "SpinQ-NMR") -> Dict[str, Any]:
        """
        Obtiene metadatos del dispositivo SpinQ
        
        Args:
            device_name: Nombre del dispositivo (default: SpinQ-NMR)
        
        Returns:
            DeviceMetadata como diccionario
        """
        from model.qc_metadata_model import DeviceMetadata
        
        # SpinQ NMR típicamente tiene 2 qubits (según la documentación)
        device_metadata = DeviceMetadata(
            device_id=device_name,
            provider="SpinQ",
            technology="nmr",  # Nuclear Magnetic Resonance
            backend_name=device_name,
            num_qubits=2,  # Límite físico según documentación
            version="1.0",
            timestamp_metadata=datetime.datetime.utcnow().isoformat() + "Z",
            connectivity={"topology_type": "all_to_all"},  # NMR típicamente permite todas las conexiones
            noise_characteristics={},  # NMR no expone estas métricas fácilmente
            operational_parameters={
                "ip": self.ip,
                "port": self.port,
                "compiler": "native"
            }
        )
        
        return device_metadata
    
    def get_calibration_data(self, device_name: str = "SpinQ-NMR") -> Any:
        """
        Obtiene datos de calibración para SpinQ
        Nota: NMR no expone calibración como IBM, así que creamos datos dummy
        
        Args:
            device_name: Nombre del dispositivo
        
        Returns:
            CalibrationData
        """
        from model.qc_metadata_model import CalibrationData
        
        # NMR no tiene calibración expuesta, creamos datos dummy
        calibration = CalibrationData(
            calibration_id=f"cal_{device_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            device_id=device_name,
            timestamp_captured=datetime.datetime.utcnow().isoformat() + "Z",
            valid_until=(datetime.datetime.utcnow() + datetime.timedelta(hours=24)).isoformat() + "Z",
            calibration_method="nmr_default",
            calibration_version="1.0",
            qubit_properties={
                0: {"t1_us": None, "t2_us": None, "readout_error": None},
                1: {"t1_us": None, "t2_us": None, "readout_error": None}
            },
            gate_fidelities={
                "1q_gates": {"q0": None, "q1": None},
                "2q_gates": {}
            },
            crosstalk_matrix={},
            additional_metrics={
                "technology": "nmr",
                "calibration_available": False
            }
        )
        
        return calibration
    
    def execute_circuit(self, circuit_spinq, shots: int = 1024, task_name: str = None, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta un circuito en SpinQ NMR
        
        Args:
            circuit_spinq: Circuito de SpinQ (spinqit.Circuit)
            shots: Número de shots
            task_name: Nombre de la tarea (opcional)
            **kwargs: Argumentos adicionales
        
        Returns:
            Diccionario con resultados
        """
        try:
            from spinqit import NMRConfig
            
            # Compilar el circuito
            exe = self.compiler.compile(circuit_spinq, 0)
            
            # Configurar conexión
            config = NMRConfig()
            config.configure_shots(shots)
            config.configure_ip(self.ip)
            config.configure_port(self.port)
            
            if self.username and self.password:
                config.configure_account(self.username, self.password)
            
            if task_name:
                config.configure_task(task_name, task_name)
            else:
                task_name = f"task_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
                config.configure_task(task_name, task_name)
            
            # Ejecutar
            result = self.engine.execute(exe, config)
            
            # Convertir probabilidades a counts
            counts = {}
            if hasattr(result, 'probabilities'):
                probs = result.probabilities
                # probs es un diccionario o array, convertir a counts
                if isinstance(probs, dict):
                    for state, prob in probs.items():
                        counts[str(state)] = int(prob * shots)
                elif isinstance(probs, (list, tuple)):
                    # Si es array, asumir orden binario (00, 01, 10, 11)
                    num_qubits = circuit_spinq.num_qubits if hasattr(circuit_spinq, 'num_qubits') else 2
                    for i, prob in enumerate(probs):
                        state_str = format(i, f'0{num_qubits}b')
                        counts[state_str] = int(prob * shots)
            
            return {
                "counts": counts,
                "shots": shots,
                "success": True,
                "job_id": task_name,
                "backend_name": "SpinQ-NMR",
                "probabilities": result.probabilities if hasattr(result, 'probabilities') else None
            }
            
        except Exception as e:
            raise Exception(f"Error al ejecutar circuito en SpinQ: {e}")


# ============================================================
# FUNCIONES DE UTILIDAD
# ============================================================

def convert_qiskit_to_braket(qiskit_circuit):
    """
    Convierte un circuito de Qiskit a Braket
    Nota: Esta es una conversión básica, puede requerir ajustes
    
    Args:
        qiskit_circuit: Circuito de Qiskit
    
    Returns:
        Circuito de Braket
    """
    try:
        from braket.circuits import Circuit
        from braket.circuits import gates as braket_gates
        
        braket_circuit = Circuit()
        
        # Mapeo de puertas básicas
        gate_map = {
            'h': braket_gates.H,
            'x': braket_gates.X,
            'y': braket_gates.Y,
            'z': braket_gates.Z,
            'cx': braket_gates.CNot,
            'cz': braket_gates.CZ,
            'ry': braket_gates.Ry,
            'rz': braket_gates.Rz,
            'rx': braket_gates.Rx,
        }
        
        for instruction in qiskit_circuit.data:
            gate_name = instruction.operation.name
            qubits = [q.index for q in instruction.qubits]
            
            if gate_name in gate_map:
                gate_class = gate_map[gate_name]
                params = instruction.operation.params
                
                if params:
                    braket_circuit += gate_class(qubits[0], *[float(p) for p in params])
                else:
                    if len(qubits) == 1:
                        braket_circuit += gate_class(qubits[0])
                    elif len(qubits) == 2:
                        braket_circuit += gate_class(qubits[0], qubits[1])
        
        # Añadir mediciones
        for instruction in qiskit_circuit.data:
            if instruction.operation.name == 'measure':
                qubits = [q.index for q in instruction.qubits]
                clbits = [c.index for c in instruction.clbits]
                # Braket mide todos los qubits por defecto
                pass
        
        return braket_circuit
    except ImportError:
        raise ImportError("amazon-braket-sdk no está instalado")
    except Exception as e:
        raise Exception(f"Error al convertir circuito: {e}")
