import os
import time
import math
from multiprocessing import Pool

# Intentamos importar la librería psutil para medir el uso de RAM y CPU de tu máquina.
# Si no está instalada, el programa seguirá funcionando igual de bien y medirá los tiempos.
try:
    import psutil
    PSUTIL_DISPONIBLE = True
except ImportError:
    PSUTIL_DISPONIBLE = False

# =====================================================================
# FUNCIONES QUE EJECUTARÁ CADA AYUDANTE (CADA PROCESO EN PARALELO)
# =====================================================================

def calcular_estadisticas_locales(pedazo_datos):
    """
    Fase 1: Cada ayudante toma su pedazo de la lista de temperaturas
    y calcula su propio conteo, mínimo, máximo, suma y suma de cuadrados.
    """
    if not pedazo_datos:
        return 0, float('inf'), float('-inf'), 0.0, 0.0
    
    conteo = len(pedazo_datos)
    minimo = min(pedazo_datos)
    maximo = max(pedazo_datos)
    suma = sum(pedazo_datos)
    
    # Suma de cuadrados de cada temperatura (necesaria para la desviación estándar global)
    suma_cuadrados = sum(x**2 for x in pedazo_datos)
    
    return conteo, minimo, maximo, suma, suma_cuadrados

def contar_mayores_locales(argumentos):
    """
    Fase 2: Cada ayudante toma su pedazo de la lista de temperaturas y el
    promedio global para contar cuántas son mayores que dicho promedio.
    """
    pedazo_datos, promedio_global = argumentos
    return sum(1 for x in pedazo_datos if x > promedio_global)

# =====================================================================
# ALGORITMO SECUENCIAL (UN SOLO TRABAJADOR / NÚCLEO)
# =====================================================================

def analizar_secuencial(temperaturas):
    """
    Una sola persona (1 núcleo de CPU) hace todos los cálculos paso a paso.
    """
    total_datos = len(temperaturas)
    if total_datos == 0:
        return 0.0, 0.0, 0.0, 0.0, 0

    minimo = min(temperaturas)
    maximo = max(temperaturas)
    suma = sum(temperaturas)
    promedio = suma / total_datos
    
    # Calcular desviación estándar (la variación de las temperaturas)
    suma_diferencias_cuadradas = sum((temp - promedio)**2 for temp in temperaturas)
    desviacion = math.sqrt(suma_diferencias_cuadradas / total_datos)
    
    # Contar cuántas temperaturas son mayores al promedio
    mayores_promedio = sum(1 for temp in temperaturas if temp > promedio)
    
    return minimo, maximo, promedio, desviacion, mayores_promedio

# =====================================================================
# ALGORITMO PARALELO (TRABAJO EN EQUIPO / MULTIPLES NÚCLEOS)
# =====================================================================

def analizar_paralelo(temperaturas, num_ayudantes):
    """
    Reparte las temperaturas entre varios ayudantes (núcleos de tu CPU)
    para que trabajen al mismo tiempo y aceleren la velocidad.
    """
    total_datos = len(temperaturas)
    if total_datos == 0:
        return 0.0, 0.0, 0.0, 0.0, 0

    # 1. Dividimos los 5 millones de registros en partes iguales según los ayudantes asignados
    tamano_pedazo = math.ceil(total_datos / num_ayudantes)
    pedazos = [temperaturas[i:i + tamano_pedazo] for i in range(0, total_datos, tamano_pedazo)]
    
    # 2. FASE 1: Los ayudantes calculan sus resúmenes locales de forma paralela
    with Pool(processes=num_ayudantes) as equipo:
        resumenes_ayudantes = equipo.map(calcular_estadisticas_locales, pedazos)
        
    # 3. El Director (Proceso Principal) junta las respuestas parciales de todos para calcular el global
    total_datos_global = 0
    minimo_global = float('inf')
    maximo_global = float('-inf')
    suma_global = 0.0
    suma_cuadrados_global = 0.0
    
    for conteo_loc, min_loc, max_loc, suma_loc, sum2_loc in resumenes_ayudantes:
        total_datos_global += conteo_loc
        if min_loc < minimo_global: minimo_global = min_loc
        if max_loc > maximo_global: maximo_global = max_loc
        suma_global += suma_loc
        suma_cuadrados_global += sum2_loc
        
    promedio_global = suma_global / total_datos_global
    
    # Calcular desviación estándar global exacta
    varianza_global = (suma_cuadrados_global / total_datos_global) - (promedio_global ** 2)
    varianza_global = max(0.0, varianza_global) # Evitamos números negativos diminutos por aproximación de decimales
    desviacion_global = math.sqrt(varianza_global)
    
    # 4. FASE 2: Los ayudantes reciben el promedio y cuentan cuántos le ganan al promedio en paralelo
    datos_fase2 = [(pedazo, promedio_global) for pedazo in pedazos]
    with Pool(processes=num_ayudantes) as equipo:
        conteos_ayudantes = equipo.map(contar_mayores_locales, datos_fase2)
        
    # Sumamos los conteos de todos los ayudantes
    mayores_promedio_global = sum(conteos_ayudantes)
    
    return minimo_global, maximo_global, promedio_global, desviacion_global, mayores_promedio_global

# =====================================================================
# GESTIÓN Y MONITOREO DE PRUEBAS
# =====================================================================

def obtener_uso_hardware():
    """
    Obtiene de forma segura la cantidad de CPU y RAM utilizada en tu sistema.
    """
    if PSUTIL_DISPONIBLE:
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        return cpu, ram
    return "Instalar psutil", "Instalar psutil"

def ejecutar_prueba(datos, modo, num_procesos=1):
    """
    Corre una prueba midiendo tiempos y hardware usado durante la ejecución.
    """
    cpu_inicio, ram_inicio = obtener_uso_hardware()
    tiempo_inicio = time.time()
    
    if modo == "secuencial":
        min_v, max_v, prom, desv, may_prom = analizar_secuencial(datos)
    else:
        min_v, max_v, prom, desv, may_prom = analizar_paralelo(datos, num_procesos)
        
    tiempo_fin = time.time()
    cpu_fin, ram_fin = obtener_uso_hardware()
    
    tiempo_total = tiempo_fin - tiempo_inicio
    
    # Hacemos un promedio simple del uso durante la prueba
    if PSUTIL_DISPONIBLE:
        cpu_uso = (cpu_inicio + cpu_fin) / 2
        ram_uso = (ram_inicio + ram_fin) / 2
    else:
        cpu_uso, ram_uso = "Instalar 'psutil'", "Instalar 'psutil'"
        
    return {
        "min": min_v,
        "max": max_v,
        "promedio": prom,
        "desviacion": desv,
        "mayores_promedio": may_prom,
        "tiempo": tiempo_total,
        "cpu": cpu_uso,
        "ram": ram_uso
    }

def cargar_temperaturas(nombre_archivo):
    """
    Carga de forma rápida los 5 millones de registros en la memoria RAM.
    """
    print(f"Cargando temperaturas desde '{nombre_archivo}'...")
    tiempo_inicio = time.time()
    
    # Verificación de si el archivo existe
    if not os.path.exists(nombre_archivo):
        print(f"ERROR: No se encuentra '{nombre_archivo}'. Ejecuta primero 'generar_datos.py'.")
        return None
        
    with open(nombre_archivo, 'r', encoding='utf-8') as f:
        # Carga rápida: lee cada línea, limpia espacios y la convierte en número flotante
        datos = [float(linea.strip()) for linea in f]
        
    tiempo_fin = time.time()
    print(f"¡Cargados {len(datos):,} registros en {tiempo_fin - tiempo_inicio:.2f} segundos!")
    return datos

def main():
    # El archivo de temperaturas se lee desde el subdirectorio 'data'
    ruta_archivo = "data/temperaturas.txt"
    datos = cargar_temperaturas(ruta_archivo)
    
    if datos is None:
        return
        
    print("\n" + "="*60)
    print(" INICIANDO EXPERIMENTO EN TU MÁQUINA VIRTUAL")
    print("="*60)
    
    # 1. Prueba con 1 núcleo (Secuencial)
    print("\nEjecutando Versión Secuencial (1 trabajador)...")
    resultado_sec = ejecutar_prueba(datos, "secuencial")
    print(f"-> Completado en {resultado_sec['tiempo']:.4f} segundos.")
    
    # 2. Prueba en paralelo con 2 ayudantes
    print("\nEjecutando Versión Paralela (2 ayudantes trabajando en equipo)...")
    resultado_par2 = ejecutar_prueba(datos, "paralelo", num_procesos=2)
    print(f"-> Completado en {resultado_par2['tiempo']:.4f} segundos.")
    
    # 3. Prueba en paralelo con 4 ayudantes
    print("\nEjecutando Versión Paralela (4 ayudantes trabajando en equipo)...")
    resultado_par4 = ejecutar_prueba(datos, "paralelo", num_procesos=4)
    print(f"-> Completado en {resultado_par4['tiempo']:.4f} segundos.")
    
    # =====================================================================
    # TABLA COMPARATIVA FINAL
    # =====================================================================
    print("\n" + "="*70)
    print("                  TABLA DE RESULTADOS DE RENDIMIENTO")
    print("="*70)
    
    col_metrica = "{:<25}"
    col_valores = "{:>14}"
    
    print(col_metrica.format("Métrica / Configuración") + col_valores.format("Secuencial") + col_valores.format("Paralelo (2 CPUs)") + col_valores.format("Paralelo (4 CPUs)"))
    print("-" * 70)
    
    t_sec = resultado_sec['tiempo']
    t_par2 = resultado_par2['tiempo']
    t_par4 = resultado_par4['tiempo']
    
    # Tiempo
    print(col_metrica.format("Tiempo total (segundos)") + col_valores.format(f"{t_sec:.4f}") + col_valores.format(f"{t_par2:.4f}") + col_valores.format(f"{t_par4:.4f}"))
    
    # Aceleración (SpeedUp)
    speedup_2 = t_sec / t_par2 if t_par2 > 0 else 0
    speedup_4 = t_sec / t_par4 if t_par4 > 0 else 0
    print(col_metrica.format("SpeedUp (Aceleración)") + col_valores.format("1.00x (Ref)") + col_valores.format(f"{speedup_2:.2f}x") + col_valores.format(f"{speedup_4:.2f}x"))
    
    # Eficiencia
    eficiencia_2 = (speedup_2 / 2) * 100
    eficiencia_4 = (speedup_4 / 4) * 100
    print(col_metrica.format("Eficiencia de CPU") + col_valores.format("100.0%") + col_valores.format(f"{eficiencia_2:.1f}%") + col_valores.format(f"{eficiencia_4:.1f}%"))
    
    # CPU y RAM (si psutil está disponible)
    if PSUTIL_DISPONIBLE:
        print(col_metrica.format("Uso Promedio de CPU (%)") + col_valores.format(f"{resultado_sec['cpu']:.1f}%") + col_valores.format(f"{resultado_par2['cpu']:.1f}%") + col_valores.format(f"{resultado_par4['cpu']:.1f}%"))
        print(col_metrica.format("Uso Promedio de RAM (%)") + col_valores.format(f"{resultado_sec['ram']:.1f}%") + col_valores.format(f"{resultado_par2['ram']:.1f}%") + col_valores.format(f"{resultado_par4['ram']:.1f}%"))
    else:
        print(col_metrica.format("Uso de CPU / RAM") + col_valores.format("Instalar psutil") + col_valores.format("Instalar psutil") + col_valores.format("Instalar psutil"))
        
    print("="*70)
    
    # =====================================================================
    # VERIFICACIÓN MATEMÁTICA
    # =====================================================================
    print("\n" + "="*70)
    print("                 COMPROBACIÓN DE EXACTITUD MATEMÁTICA")
    print("="*70)
    print(f"Temperatura Mínima:      {resultado_sec['min']:.2f}°C  (Coincide en todos: {resultado_sec['min'] == resultado_par4['min']})")
    print(f"Temperatura Máxima:      {resultado_sec['max']:.2f}°C  (Coincide en todos: {resultado_sec['max'] == resultado_par4['max']})")
    print(f"Promedio de temperatura: {resultado_sec['promedio']:.4f}°C (Coincide en todos: {abs(resultado_sec['promedio'] - resultado_par4['promedio']) < 1e-9})")
    print(f"Desviación Estándar:     {resultado_sec['desviacion']:.4f}°C (Coincide en todos: {abs(resultado_sec['desviacion'] - resultado_par4['desviacion']) < 1e-9})")
    print(f"Lecturas > Promedio:     {resultado_sec['mayores_promedio']:,} registros (Coincide: {resultado_sec['mayores_promedio'] == resultado_par4['mayores_promedio']})")
    print("="*70)

if __name__ == '__main__':
    # Necesario para que el multiprocesamiento funcione correctamente en Windows
    main()
