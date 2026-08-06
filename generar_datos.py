import random
import os
import time

def crear_archivo_temperaturas(nombre_archivo, cantidad_datos=5000000):
    """
    Esta función crea un archivo de texto y escribe dentro de él
    millones de lecturas de temperatura de sensores IoT aleatorios.
    Las temperaturas se generan entre -10 y 50 grados Celsius.
    """
    print("=== Generador de Datos de Temperatura IoT ===")
    print(f"Preparando la creación de {cantidad_datos:,} registros...")
    
    tiempo_inicio = time.time()
    
    # Paso 1: Creamos la carpeta 'data' en tu computadora si no existe
    carpeta = os.path.dirname(nombre_archivo)
    if carpeta and not os.path.exists(carpeta):
        os.makedirs(carpeta)
        print(f"Carpeta creada con éxito: {carpeta}")
        
    # Paso 2: Escribimos los números en el archivo de texto
    # Para que sea sumamente rápido y no demore tu disco duro,
    # generamos y escribimos los números en bloques de 100,000 en 100,000.
    bloque_tamano = 100000
    total_bloques = cantidad_datos // bloque_tamano
    
    try:
        with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
            for bloque_actual in range(total_bloques):
                # Generamos 100,000 temperaturas aleatorias con 2 decimales
                bloque = [f"{random.uniform(-10.0, 50.0):.2f}\n" for _ in range(bloque_tamano)]
                # Las guardamos de un solo golpe en el archivo
                archivo.writelines(bloque)
                
                # Barra de progreso visual en pantalla
                if (bloque_actual + 1) % 10 == 0 or (bloque_actual + 1) == total_bloques:
                    progreso = ((bloque_actual + 1) / total_bloques) * 100
                    print(f"Guardando datos... {progreso:.0f}% completado")
                    
        tiempo_fin = time.time()
        peso_archivo = os.path.getsize(nombre_archivo) / (1024 * 1024)
        
        print("\n=== ¡Archivo Generado con Éxito! ===")
        print(f"Guardado en: {nombre_archivo}")
        print(f"Peso del archivo: {peso_archivo:.2f} MB")
        print(f"Tiempo transcurrido: {tiempo_fin - tiempo_inicio:.2f} segundos.")
        
    except Exception as e:
        print(f"Ocurrió un error al crear el archivo: {e}")

if __name__ == "__main__":
    # Creamos el archivo de 5 millones en la carpeta data
    crear_archivo_temperaturas("data/temperaturas.txt", 5000000)
