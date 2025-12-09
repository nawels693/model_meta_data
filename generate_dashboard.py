import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os

def load_metadata(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_dashboard(metadata, output_file='dashboard_report.png'):
    # Configuración de la figura
    fig = plt.figure(figsize=(20, 12))
    fig.suptitle(f"QC Metadata Dashboard - {metadata['device_metadata']['device_id']}", fontsize=16)
    
    # Grid de 2x2
    gs = fig.add_gridspec(2, 2)
    ax1 = fig.add_subplot(gs[0, 0]) # Calibración T1/T2
    ax2 = fig.add_subplot(gs[0, 1]) # Métricas de Compilación
    ax3 = fig.add_subplot(gs[1, 0]) # Resultados de Ejecución
    ax4 = fig.add_subplot(gs[1, 1]) # Info General

    # --- PANEL 1: Calibración Qubits (T1 y T2) ---
    cal_data = metadata['calibration_data'][0]
    qubits = []
    t1_times = []
    t2_times = []
    
    # Extraer datos de qubits (limitamos a los primeros 20 para legibilidad si son muchos)
    qubit_props = cal_data.get('qubit_properties', {})
    sorted_qubits = sorted([int(q) for q in qubit_props.keys()])[:20] 
    
    for q in sorted_qubits:
        props = qubit_props[str(q)]
        qubits.append(f"Q{q}")
        # Convertir a microsegundos si es necesario (asumiendo que ya están en us según el modelo)
        t1_times.append(props.get('t1_us', 0))
        t2_times.append(props.get('t2_us', 0))

    x = np.arange(len(qubits))
    width = 0.35
    
    if t1_times:
        rects1 = ax1.bar(x - width/2, t1_times, width, label='T1 (µs)', color='skyblue')
        rects2 = ax1.bar(x + width/2, t2_times, width, label='T2 (µs)', color='lightcoral')
        ax1.set_ylabel('Tiempo (µs)')
        ax1.set_title('Tiempos de Coherencia (Primeros Qubits)')
        ax1.set_xticks(x)
        ax1.set_xticklabels(qubits)
        ax1.legend()
    else:
        ax1.text(0.5, 0.5, "No hay datos de calibración T1/T2", ha='center')

    # --- PANEL 2: Métricas de Compilación ---
    trace = metadata['compilation_trace']
    if isinstance(trace, list): trace = trace[0] # Tomar el primero si es lista
    
    metrics = trace.get('optimization_metrics', {})
    original_depth = metrics.get('original_depth', 0)
    compiled_depth = metrics.get('compiled_depth', 0)
    original_gates = metrics.get('original_gates', 0)
    compiled_gates = metrics.get('compiled_gates', 0)

    labels = ['Profundidad', 'Num Puertas']
    original_vals = [original_depth, original_gates]
    compiled_vals = [compiled_depth, compiled_gates]

    x_metrics = np.arange(len(labels))
    ax2.bar(x_metrics - width/2, original_vals, width, label='Original', color='gray')
    ax2.bar(x_metrics + width/2, compiled_vals, width, label='Compilado', color='purple')
    ax2.set_ylabel('Conteo')
    ax2.set_title('Impacto de la Compilación')
    ax2.set_xticks(x_metrics)
    ax2.set_xticklabels(labels)
    ax2.legend()
    
    # Añadir texto de duración
    duration = trace.get('compilation_duration_ms', 0)
    ax2.text(0.5, 0.9, f"Duración Compilación: {duration:.2f} ms", 
             transform=ax2.transAxes, ha='center', bbox=dict(facecolor='white', alpha=0.8))

    # --- PANEL 3: Resultados de Ejecución ---
    exec_ctx = metadata['execution_context'][0]
    results = exec_ctx.get('results', {}).get('counts', {})
    
    # Ordenar resultados por probabilidad
    sorted_counts = dict(sorted(results.items(), key=lambda item: item[1], reverse=True))
    states = list(sorted_counts.keys())[:10] # Top 10 estados
    counts = list(sorted_counts.values())[:10]
    
    ax3.bar(states, counts, color='teal')
    ax3.set_ylabel('Cuentas (Shots)')
    ax3.set_title(f"Resultados (Top 10) - Total Shots: {exec_ctx.get('num_shots')}")
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)

    # --- PANEL 4: Resumen Informativo ---
    ax4.axis('off')
    info_text = [
        f"Fecha Ejecución: {exec_ctx.get('timestamp_execution')}",
        f"Backend: {metadata['device_metadata']['backend_name']}",
        f"Algoritmo: {metadata['circuit_metadata']['circuit_name']}",
        f"Provider: {metadata['device_metadata']['provider']}",
        f"Ejecución ID: {exec_ctx.get('execution_id')}",
        f"Calibración ID: {cal_data.get('calibration_id')}",
        f"Estado Validación: {exec_ctx.get('freshness_validation', {}).get('calibration_expired', 'Unknown')}"
    ]
    
    y_pos = 0.9
    ax4.text(0.05, 1.0, "Resumen de Ejecución", fontsize=14, fontweight='bold')
    for line in info_text:
        ax4.text(0.05, y_pos, line, fontsize=11, transform=ax4.transAxes)
        y_pos -= 0.1

    plt.tight_layout()
    plt.savefig(output_file)
    print(f"✓ Dashboard generado exitosamente: {output_file}")

if __name__ == "__main__":
    # Buscar automáticamente el archivo JSON más reciente en outputs/
    output_dir = "outputs"
    if os.path.exists(output_dir):
        files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith('.json')]
        if files:
            latest_file = max(files, key=os.path.getctime)
            print(f"Procesando archivo más reciente: {latest_file}")
            
            try:
                data = load_metadata(latest_file)
                create_dashboard(data, output_file=f"{latest_file.replace('.json', '_dashboard.png')}")
            except Exception as e:
                print(f"Error al generar dashboard: {e}")
        else:
            print("No se encontraron archivos JSON en outputs/")
    else:
        print("Directorio outputs/ no existe")