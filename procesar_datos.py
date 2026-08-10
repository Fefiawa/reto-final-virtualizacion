"""Procesa temperaturas de forma secuencial y paralela en Linux."""

import math
import os
import time
from multiprocessing import Pool


ARCHIVO = "temperaturas.txt"
TEMPERATURAS = []


def resumir(rango):
    """Calcula mínimo, máximo, suma y suma de cuadrados de un rango."""
    inicio, fin = rango
    datos = TEMPERATURAS[inicio:fin]
    return len(datos), min(datos), max(datos), sum(datos), sum(valor * valor for valor in datos)


def contar_mayores(tarea):
    """Cuenta las temperaturas de un rango que son mayores al promedio."""
    inicio, fin, promedio = tarea
    return sum(valor > promedio for valor in TEMPERATURAS[inicio:fin])


def obtener_resultados(resumenes, conteos):
    """Une los resultados parciales y calcula las cinco estadísticas finales."""
    cantidad = sum(resumen[0] for resumen in resumenes)
    minimo = min(resumen[1] for resumen in resumenes)
    maximo = max(resumen[2] for resumen in resumenes)
    suma = sum(resumen[3] for resumen in resumenes)
    suma_cuadrados = sum(resumen[4] for resumen in resumenes)
    promedio = suma / cantidad
    # max evita un negativo microscópico causado por redondeo decimal.
    desviacion = math.sqrt(max(0, suma_cuadrados / cantidad - promedio ** 2))

    return minimo, maximo, promedio, desviacion, sum(conteos)


def procesar_secuencial():
    """Un solo proceso analiza todas las temperaturas."""
    resumen = resumir((0, len(TEMPERATURAS)))
    promedio = resumen[3] / resumen[0]
    mayores = contar_mayores((0, len(TEMPERATURAS), promedio))
    return obtener_resultados([resumen], [mayores])


def dividir_rangos(procesos):
    """Divide las temperaturas en partes casi iguales para los procesos."""
    tamano = math.ceil(len(TEMPERATURAS) / procesos)
    return [(inicio, min(inicio + tamano, len(TEMPERATURAS)))
            for inicio in range(0, len(TEMPERATURAS), tamano)]


def procesar_paralelo(procesos):
    """Varios procesos analizan distintas partes de las temperaturas."""
    rangos = dividir_rangos(procesos)

    # En Linux los procesos heredan los datos ya cargados, sin recargar el archivo.
    with Pool(procesos) as pool:
        resumenes = pool.map(resumir, rangos)
        promedio = sum(resumen[3] for resumen in resumenes) / len(TEMPERATURAS)
        tareas = [(inicio, fin, promedio) for inicio, fin in rangos]
        conteos = pool.map(contar_mayores, tareas)

    return obtener_resultados(resumenes, conteos)


def mostrar_resultados(titulo, resultado, tiempo):
    minimo, maximo, promedio, desviacion, mayores = resultado
    print(f"\n{titulo}")
    print(f"Tiempo de ejecución: {tiempo:.4f} segundos")
    print(f"Temperatura más alta: {maximo:.2f} °C")
    print(f"Temperatura más baja: {minimo:.2f} °C")
    print(f"Promedio: {promedio:.2f} °C")
    print(f"Desviación estándar: {desviacion:.4f}")
    print(f"Temperaturas mayores al promedio: {mayores:,}")


def main():
    global TEMPERATURAS

    if not os.path.exists(ARCHIVO):
        print(f"No se encontró {ARCHIVO}. Ejecuta primero generar_datos.py")
        return

    # Se cargan las temperaturas una sola vez. Este tiempo no se compara,
    # porque ambos métodos necesitan los mismos datos en memoria.
    with open(ARCHIVO, encoding="utf-8") as archivo:
        TEMPERATURAS = [float(linea) for linea in archivo]

    inicio = time.perf_counter()
    resultado_secuencial = procesar_secuencial()
    tiempo_secuencial = time.perf_counter() - inicio
    mostrar_resultados("RESULTADOS SECUENCIALES", resultado_secuencial, tiempo_secuencial)

    procesos = os.cpu_count() or 1
    inicio = time.perf_counter()
    resultado_paralelo = procesar_paralelo(procesos)
    tiempo_paralelo = time.perf_counter() - inicio
    mostrar_resultados(
        f"RESULTADOS PARALELOS ({procesos} núcleos virtuales)",
        resultado_paralelo,
        tiempo_paralelo,
    )


if __name__ == "__main__":
    main()
