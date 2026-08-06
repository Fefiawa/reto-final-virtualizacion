import os
import time
import math
from multiprocessing import Pool

# Intentar importar psutil para medir CPU y RAM. Si no está instalado,
# el script seguirá funcionando, pero indicará que no puede obtener esas métricas de hardware.
try:
    import psutil
    PSUTIL_DISPONIBLE = True
except ImportError:
    PSUTIL_DISPONIBLE = False

# =====================================================================
# FUNCIONES AUXILIARES PARA EL PROCESAMIENTO PARALELO (CÓMPUTO LOCAL)
# =====================================================================

def procesar_chunk_fase1(chunk):
    """
    Fase 1 (Local): Cada proceso analiza un fragmento (chunk) de los datos.
    Calcula: conteo, mínimo, máximo, suma y la suma de los valores al cuadrado.
    """
    if not chunk:
        return 0, float('inf'), float('-inf'), 0.0, 0.0
    
    n_local = len(chunk)
    min_local = min(chunk)
    max_local = max(chunk)
    suma_local = sum(chunk)
    # Suma de cuadrados necesaria para calcular la desviación estándar global en paralelo
    suma_cuadrados_local = sum(x**2 for x in chunk)
    
    return n_local, min_local, max_local, suma_local, suma_cuadrados_local

def procesar_chunk_fase2(args):
    """
    Fase 2 (Local): Con el promedio global ya conocido, cada proceso cuenta
    cuántos elementos de su fragmento son mayores que dicho promedio.
    """
    chunk, promedio_global = args
    return sum(1 for x in chunk if x > promedio_global)

# =====================================================================
# ALGORITMO 1: PROCESAMIENTO SECUENCIAL (UN SOLO HILO / PROCESO)
# =====================================================================

def procesar_secuencial(datos):
    """
    Realiza los cálculos de forma secuencial en un solo proceso.
    """
    n = len(datos)
    if n == 0:
        return 0.0, 0.0, 0.0, 0.0, 0

    min_val = min(datos)
    max_val = max(datos)
    suma = sum(datos)
    promedio = suma / n
    
    # Calcular desviación estándar poblacional secuencial
    suma_cuadrados_diff = sum((x - promedio)**2 for x in datos)
    desviacion = math.sqrt(suma_cuadrados_diff / n)
    
    # Contar datos mayores al promedio
    mayores_promedio = sum(1 for x in datos if x > promedio)
    
    return min_val, max_val, promedio, desviacion, mayores_promedio

# =====================================================================
# ALGORITMO 2: PROCESAMIENTO PARALELO (MÚLTIPLES PROCESOS / NÚCLEOS)
# =====================================================================

def procesar_paralelo(datos, num_procesos):
    """
    Divide el trabajo y lo distribuye entre el número especificado de procesos.
    """
    n_total = len(datos)
    if n_total == 0:
        return 0.0, 0.0, 0.0, 0.0, 0

    # 1. Dividir los datos en partes (chunks) proporcionales al número de procesos
    tamano_chunk = math.ceil(n_total / num_procesos)
    chunks = [datos[i:i + tamano_chunk] for i in range(0, n_total, tamano_chunk)]
    
    # 2. FASE 1 en Paralelo: Obtener estadísticas locales
    with Pool(processes=num_procesos) as pool:
        resultados_fase1 = pool.map(procesar_chunk_fase1, chunks)
        
    # 3. Reducción Global de la Fase 1
    n_global = 0
    min_global = float('inf')
    max_global = float('-inf')
    suma_global = 0.0
    suma_cuadrados_global = 0.0
    
    for n_l, min_l, max_l, sum_l, sum_sq_l in resultados_fase1:
        n_global += n_l
        if min_l < min_global: min_global = min_l
        if max_l > max_global: max_global = max_l
        suma_global += sum_l
        suma_cuadrados_global += sum_sq_l
        
    promedio_global = suma_global / n_global
    
    # Varianza global = E[X^2] - (E[X])^2
    varianza_global = (suma_cuadrados_global / n_global) - (promedio_global ** 2)
    varianza_global = max(0.0, varianza_global) # Evitar errores de redondeo de flotantes
    desviacion_global = math.sqrt(varianza_global)
    
    # 4. FASE 2 en Paralelo: Contar mayores al promedio global
    # Preparamos los argumentos para cada proceso: (chunk de datos, promedio global de referencia)
    argumentos_fase2 = [(chunk, promedio_global) for chunk in chunks]
    with Pool(processes=num_procesos) as pool:
        resultados_fase2 = pool.map(procesar_chunk_fase2, argumentos_fase2)
        
    mayores_promedio_global = sum(resultados_fase2)
    
    return min_global, max_global, promedio_global, desviacion_global, mayores_promedio_global

# =====================================================================
# FUNCIÓN PRINCIPAL DE GESTIÓN Y MONITOREO
# =====================================================================

def obtener_metricas_sistema():
    """
    Obtiene el uso actual de CPU y RAM de forma segura.
    """
    if PSUTIL_DISPONIBLE:
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        return cpu, ram
    return "N/A", "N/A"

def ejecutar_prueba(datos, modo, num_procesos=1):
    """
    Ejecuta un análisis (secuencial o paralelo) midiendo tiempo y hardware.
    """
    cpu_inicio, ram_inicio = obtener_metricas_sistema()
    tiempo_inicio = time.time()
    
    if modo == "secuencial":
        min_v, max_v, prom, desv, may_prom = procesar_secuencial(datos)
    else:
        min_v, max_v, prom, desv, may_prom = procesar_paralelo(datos, num_procesos)
        
    tiempo_fin = time.time()
    cpu_fin, ram_fin = obtener_metricas_sistema()
    
    tiempo_total = tiempo_fin - tiempo_inicio
    
    # Estimación simple del uso de hardware promedio durante la ejecución
    if PSUTIL_DISPONIBLE:
        cpu_uso = (cpu_inicio + cpu_fin) / 2
        ram_uso = (ram_inicio + ram_fin) / 2
    else:
        cpu_uso, ram_uso = "Instalar 'psutil'", "Instalar 'psutil'"
        
    resultados = {
        "min": min_v,
        "max": max_v,
        "promedio": prom,
        "desviacion": desv,
        "mayores_promedio": may_prom,
        "tiempo": tiempo_total,
        "cpu": cpu_uso,
        "ram": ram_uso
    }
    
    return resultados

def cargar_datos(nombre_archivo):
    """
    Carga el archivo de temperaturas de forma rápida en memoria.
    """
    print(f"Cargando datos desde '{nombre_archivo}'...")
    inicio = time.time()
    
    if not os.path.exists(nombre_archivo):
        print(f"ERROR: El archivo '{nombre_archivo}' no existe. Ejecuta primero 'generar_datos.py'.")
        return None
        
    temperaturas = []
    with open(nombre_archivo, 'r', encoding='utf-8') as f:
        # Cargamos los datos convirtiendo a flotantes directamente
        temperaturas = [float(linea.strip()) for linea in f]
        
    fin = time.time()
    print(f"Se cargaron {len(temperaturas):,} registros en {fin - inicio:.2f} segundos.")
    return temperaturas

def main():
    ruta_datos = "data/temperaturas.txt"
    datos = cargar_datos(ruta_datos)
    
    if datos is None:
        return
        
    print("\n" + "="*60)
    print(" INICIANDO EXPERIMENTACIÓN Y PRUEBAS DE RENDIMIENTO")
    print("="*60)
    
    # 1. Ejecución Secuencial
    print("\nEjecutando Versión Secuencial (1 núcleo)...")
    res_sec = ejecutar_prueba(datos, "secuencial")
    print(f"-> Completado en {res_sec['tiempo']:.4f} segundos.")
    
    # 2. Ejecución Paralela con 2 núcleos
    print("\nEjecutando Versión Paralela (2 núcleos virtuales)...")
    res_par2 = ejecutar_prueba(datos, "paralelo", num_procesos=2)
    print(f"-> Completado en {res_par2['tiempo']:.4f} segundos.")
    
    # 3. Ejecución Paralela con 4 núcleos
    print("\nEjecutando Versión Paralela (4 núcleos virtuales)...")
    res_par4 = ejecutar_prueba(datos, "paralelo", num_procesos=4)
    print(f"-> Completado en {res_par4['tiempo']:.4f} segundos.")
    
    # =====================================================================
    # MOSTRAR TABLA COMPARATIVA DE RESULTADOS EXPERIMENTALES
    # =====================================================================
    print("\n" + "="*70)
    print("                     TABLA COMPARATIVA DE RENDIMIENTO")
    print("="*70)
    
    col_config = "{:<25}"
    col_vals = "{:>14}"
    
    print(col_config.format("Métrica / Configuración") + col_vals.format("Secuencial") + col_vals.format("Paralelo (2 vCPUs)") + col_vals.format("Paralelo (4 vCPUs)"))
    print("-" * 70)
    
    # Tiempos
    t_sec = res_sec['tiempo']
    t_par2 = res_par2['tiempo']
    t_par4 = res_par4['tiempo']
    
    print(col_config.format("Tiempo de Ejecución (s)") + col_vals.format(f"{t_sec:.4f}") + col_vals.format(f"{t_par2:.4f}") + col_vals.format(f"{t_par4:.4f}"))
    
    # SpeedUp (T_secuencial / T_paralelo)
    su_2 = t_sec / t_par2 if t_par2 > 0 else 0
    su_4 = t_sec / t_par4 if t_par4 > 0 else 0
    print(col_config.format("SpeedUp obtenido") + col_vals.format("1.00x (Ref)") + col_vals.format(f"{su_2:.2f}x") + col_vals.format(f"{su_4:.2f}x"))
    
    # Eficiencia (SpeedUp / Num_procesos)
    efi_2 = (su_2 / 2) * 100
    efi_4 = (su_4 / 4) * 100
    print(col_config.format("Eficiencia de CPU (%)") + col_vals.format("100.0%") + col_vals.format(f"{efi_2:.1f}%") + col_vals.format(f"{efi_4:.1f}%"))
    
    # CPU y RAM
    if PSUTIL_DISPONIBLE:
        print(col_config.format("Uso Promedio CPU (%)") + col_vals.format(f"{res_sec['cpu']:.1f}%") + col_vals.format(f"{res_par2['cpu']:.1f}%") + col_vals.format(f"{res_par4['cpu']:.1f}%"))
        print(col_config.format("Uso Promedio RAM (%)") + col_vals.format(f"{res_sec['ram']:.1f}%") + col_vals.format(f"{res_par2['ram']:.1f}%") + col_vals.format(f"{res_par4['ram']:.1f}%"))
    else:
        print(col_config.format("Uso Promedio CPU (%)") + col_vals.format("Instalar psutil") + col_vals.format("Instalar psutil") + col_vals.format("Instalar psutil"))
        print(col_config.format("Uso Promedio RAM (%)") + col_vals.format("Instalar psutil") + col_vals.format("Instalar psutil") + col_vals.format("Instalar psutil"))
        
    print("="*70)
    
    # =====================================================================
    # VERIFICACIÓN DE EXACTITUD MATEMÁTICA
    # =====================================================================
    print("\n" + "="*70)
    print("                     VERIFICACIÓN DE RESULTADOS MATEMÁTICOS")
    print("="*70)
    print(f"Mínimo calculado:        {res_sec['min']:.2f}°C  (Coincide en todos: {res_sec['min'] == res_par4['min']})")
    print(f"Máximo calculado:        {res_sec['max']:.2f}°C  (Coincide en todos: {res_sec['max'] == res_par4['max']})")
    print(f"Promedio calculado:      {res_sec['promedio']:.4f}°C (Diferencia: {abs(res_sec['promedio'] - res_par4['promedio']):.2e})")
    print(f"Desviación Estándar:     {res_sec['desviacion']:.4f}°C (Diferencia: {abs(res_sec['desviacion'] - res_par4['desviacion']):.2e})")
    print(f"Mayores al promedio:     {res_sec['mayores_promedio']:,} registros (Coincide: {res_sec['mayores_promedio'] == res_par4['mayores_promedio']})")
    print("="*70)

if __name__ == '__main__':
    # Necesario para el correcto funcionamiento de multiprocessing en Windows
    main()
