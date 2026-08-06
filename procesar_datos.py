import os
import time
import math
from multiprocessing import Pool

// Esta función calcula las estadísticas locales de un conjunto de datos
def calcular_estadisticas_locales(datos):

    if not datos:
        return 0, float("inf"), float("-inf"), 0.0, 0.0

    cantidad = len(datos)
    minimo = min(datos)
    maximo = max(datos)
    suma = sum(datos)
    suma_cuadrados = sum(x ** 2 for x in datos)

    return cantidad, minimo, maximo, suma, suma_cuadrados

//funcion para contar temporadas mayores al promedio    
def contar_mayores(argumentos):

    datos, promedio = argumentos

    return sum(1 for x in datos if x > promedio)


# ==========================================================
# ALGORITMO SECUENCIAL
# ==========================================================
// Esta función analiza un conjunto de temperaturas y calcula estadísticas
def analizar_secuencial(temperaturas):

    total = len(temperaturas)

    if total == 0:
        return 0, 0, 0, 0, 0

    minimo = min(temperaturas)
    maximo = max(temperaturas)

    suma = sum(temperaturas)
    promedio = suma / total

    suma_diferencias = sum((x - promedio) ** 2 for x in temperaturas)

    desviacion = math.sqrt(suma_diferencias / total)

    mayores = sum(1 for x in temperaturas if x > promedio)

    return (
        minimo,
        maximo,
        promedio,
        desviacion,
        mayores
    )

# ==========================================================
# ALGORITMO PARALELO
# ==========================================================

def analizar_paralelo(temperaturas, procesos):

    total = len(temperaturas)

    if total == 0:
        return 0, 0, 0, 0, 0

    # Dividir los datos entre los procesos
    tamano = math.ceil(total / procesos)

    bloques = [
        temperaturas[i:i + tamano]
        for i in range(0, total, tamano)
    ]

    # -------- FASE 1 --------
    # Cada proceso calcula estadísticas de su bloque

    with Pool(processes=procesos) as pool:
        resultados = pool.map(
            calcular_estadisticas_locales,
            bloques
        )

    total_datos = 0
    suma_total = 0
    suma_cuadrados = 0

    minimo = float("inf")
    maximo = float("-inf")

    for cantidad, minimo_local, maximo_local, suma_local, cuadrados_local in resultados:

        total_datos += cantidad
        suma_total += suma_local
        suma_cuadrados += cuadrados_local

        minimo = min(minimo, minimo_local)
        maximo = max(maximo, maximo_local)

    promedio = suma_total / total_datos

    varianza = (suma_cuadrados / total_datos) - (promedio ** 2)

    if varianza < 0:
        varianza = 0

    desviacion = math.sqrt(varianza)

    # -------- FASE 2 --------
    # Contar temperaturas mayores al promedio

    argumentos = [
        (bloque, promedio)
        for bloque in bloques
    ]

    with Pool(processes=procesos) as pool:
        conteos = pool.map(
            contar_mayores,
            argumentos
        )

    mayores = sum(conteos)

    return (
        minimo,
        maximo,
        promedio,
        desviacion,
        mayores
    )

# ==========================================================
# CARGAR ARCHIVO DE TEMPERATURAS
# ==========================================================

def cargar_temperaturas(ruta_archivo):

    print("\nCargando archivo de temperaturas...")

    if not os.path.exists(ruta_archivo):
        print("\nERROR")
        print("No se encontró el archivo:")
        print(ruta_archivo)
        print("\nPrimero ejecuta generar_datos.py")
        return None

    inicio = time.time()

    with open(ruta_archivo, "r", encoding="utf-8") as archivo:
        temperaturas = [
            float(linea.strip())
            for linea in archivo
        ]

    fin = time.time()

    print(f"Archivo cargado correctamente.")
    print(f"Registros encontrados: {len(temperaturas):,}")
    print(f"Tiempo de carga: {fin - inicio:.2f} segundos\n")

    return temperaturas