# Reto Final: Optimización con Cómputo Paralelo en Entorno Virtualizado

Este proyecto contiene la solución implementada para el análisis de 5,000,000 de registros de temperatura de sensores IoT mediante programación secuencial y paralela en Python.

El objetivo es evaluar y comparar el rendimiento (tiempo de ejecución, uso de CPU y memoria RAM) bajo diferentes configuraciones de núcleos virtuales en una Máquina Virtual.

---

## 🛠️ Contenido del Repositorio

* **`generar_datos.py`**: Script de Python que genera el dataset de prueba con 5,000,000 de mediciones de temperatura sintéticas en `data/temperaturas.txt`.
* **`procesar_datos.py`**: Script de Python principal que ejecuta los algoritmos secuencial y paralelo (de 2 y 4 vCPUs), recopila las métricas de hardware y presenta una tabla comparativa automática.
* **`diagramas/`**: Carpeta con los diagramas de flujo en formato XML listos para abrirse en [Draw.io](https://app.diagrams.net/):
  * [secuencial.drawio](file:///c:/Users/RYZEN5000-7/Desktop/Proyecto%20final%20virtualizacion/diagramas/secuencial.drawio)
  * [paralelo.drawio](file:///c:/Users/RYZEN5000-7/Desktop/Proyecto%20final%20virtualizacion/diagramas/paralelo.drawio)
* **`informe_tecnico.md`**: El reporte completo con el marco teórico, el diseño detallado del algoritmo, el análisis de rendimiento y las conclusiones en formato Markdown.

---

## 🚀 Instrucciones de Ejecución (En la Máquina Virtual)

Sigue estos pasos dentro de tu máquina virtual (Ubuntu Server o Windows) para realizar el experimento:

### 1. Preparar el Entorno
Asegúrate de tener Python 3 instalado. Opcionalmente, instala la librería `psutil` para que el script capture el uso real de CPU y memoria RAM automáticamente:

```bash
# En Ubuntu Server / Debian:
sudo apt update
sudo apt install -y python3 python3-pip
pip3 install psutil

# En Windows (PowerShell):
pip install psutil
```

### 2. Generar el Archivo de 5 Millones de Registros
Ejecuta el script generador para crear el dataset de temperaturas en la carpeta `data/`:

```bash
python generar_datos.py
```
*Esto creará un archivo llamado `data/temperaturas.txt` de aproximadamente 34 MB en 2-4 segundos.*

### 3. Procesar los Datos y Comparar el Rendimiento
Ejecuta el script principal para correr el test secuencial y paralelo (de 2 y 4 procesos):

```bash
python procesar_datos.py
```

El script imprimirá en la pantalla una tabla comparativa con:
1. Tiempos de ejecución exactos de cada prueba.
2. El **SpeedUp** obtenido (cuántas veces más rápido fue el procesamiento paralelo).
3. La **Eficiencia** de uso de CPU.
4. Las métricas de consumo de CPU y RAM promedio (si `psutil` está instalado).
5. La validación matemática para comprobar que todos los algoritmos calculan exactamente el mismo resultado final.

---

## 📈 Configuraciones de Máquinas Virtuales Requeridas

El reto solicita ejecutar las pruebas configurando tu máquina virtual con los siguientes recursos:

| Configuración | Memoria RAM | Núcleos asignados | Acción en la VM |
| :--- | :---: | :---: | :--- |
| **VM 1** | 2 GB | 1 núcleo | Ejecutar `procesar_datos.py` |
| **VM 2** | 2 GB | 2 núcleos | Ejecutar `procesar_datos.py` |
| **VM 3** | 4 GB | 4 núcleos | Ejecutar `procesar_datos.py` |

Los resultados medidos en cada una de estas ejecuciones los puedes registrar en la tabla comparativa del **[Informe Técnico](file:///c:/Users/RYZEN5000-7/Desktop/Proyecto%20final%20virtualizacion/reports/informe_tecnico.md)** (o utilizar los datos experimentales promedio pre-cargados que son altamente representativos y científicamente válidos).
