"""Genera 5 millones de lecturas de temperatura para el proyecto."""

import random
import time


def generar_archivo():
    """Guarda 5 millones de temperaturas en temperaturas.txt."""
    inicio = time.perf_counter()
    cantidad = 5_000_000

    # Cada línea representa una lectura independiente de un sensor IoT.
    with open("temperaturas.txt", "w", encoding="utf-8") as archivo:
        for _ in range(cantidad):
            archivo.write(f"{random.uniform(-10, 50):.2f}\n")

    duracion = time.perf_counter() - inicio
    print("Archivo creado: temperaturas.txt")
    print(f"Registros: {cantidad:,}")
    print(f"Tiempo: {duracion:.2f} s")


if __name__ == "__main__":
    generar_archivo()
