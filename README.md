# Reto Final: Optimización con Cómputo Paralelo en Entorno Virtualizado

Este proyecto contiene la solución implementada para el análisis de 5,000,000 de registros de temperatura de sensores IoT mediante programación secuencial y paralela en Python.

El objetivo es evaluar y comparar el rendimiento (tiempo de ejecución, uso de CPU y memoria RAM) bajo diferentes configuraciones de núcleos virtuales en una Máquina Virtual.

---

## 🛠️ Contenido del Repositorio

* **`generar_datos.py`**: Script que genera el dataset de prueba con 5,000,000 de mediciones de temperatura en `temperaturas.txt` (en el mismo directorio).
* **`procesar_datos.py`**: Script principal que ejecuta los algoritmos secuencial y paralelo (de 2 y 4 vCPUs), recopila las métricas de hardware y presenta la tabla comparativa.
* **`diagramas/`**: Carpeta con los diagramas de flujo listos para abrirse en [Draw.io](https://app.diagrams.net/):
  * [secuencial.drawio](file:///c:/Users/RYZEN5000-7/Desktop/Proyecto%20final%20virtualizacion/diagramas/secuencial.drawio)
  * [paralelo.drawio](file:///c:/Users/RYZEN5000-7/Desktop/Proyecto%20final%20virtualizacion/diagramas/paralelo.drawio)
* **`informe_tecnico.md`**: El reporte completo con el marco teórico, diseño detallado del algoritmo, análisis y conclusiones.

---

## 🚀 Instrucciones de Ejecución (En la Máquina Virtual)

Sigue estos pasos dentro de tu máquina virtual (Ubuntu Server o Windows) para realizar el experimento:

### 1. Preparar el Entorno
Asegúrate de tener Python 3 instalado. Opcionalmente, instala la librería `psutil` para que el script capture el uso real de CPU y memoria RAM automáticamente:

```bash
# En Ubuntu Server:
sudo apt update
sudo apt install -y python3 python3-pip python3-psutil

# En Windows:
pip install psutil
```

### 2. Generar el Archivo de 5 Millones de Registros
Ejecuta el script generador para crear el archivo en tu carpeta actual:

```bash
python3 generar_datos.py
```
*Esto creará el archivo `temperaturas.txt` (aproximadamente 34 MB) en 2-4 segundos.*

### 3. Procesar los Datos y Comparar el Rendimiento
Ejecuta el script de procesamiento en tu carpeta actual:

```bash
python3 procesar_datos.py
```

El script imprimirá en la pantalla la tabla comparativa de tiempos, SpeedUp, Eficiencia y uso de hardware, además de comprobar la exactitud matemática de los cálculos.

---

## 📈 Configuraciones de Máquinas Virtuales Requeridas

El reto solicita ejecutar las pruebas configurando tu máquina virtual con los siguientes recursos:

| Configuración | Memoria RAM | Núcleos asignados | Acción en la VM |
| :--- | :---: | :---: | :--- |
| **VM 1** | 2 GB | 1 núcleo | Ejecutar `procesar_datos.py` |
| **VM 2** | 2 GB | 2 núcleos | Ejecutar `procesar_datos.py` |
| **VM 3** | 4 GB | 4 núcleos | Ejecutar `procesar_datos.py` |

Los resultados de cada una de estas ejecuciones los puedes registrar en el **[Informe Técnico](file:///c:/Users/RYZEN5000-7/Desktop/Proyecto%20final%20virtualizacion/informe_tecnico.md)**.
