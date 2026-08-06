import random
import os
import time

def generar_datos(nombre_archivo, total_registros=5000000):
    """
    Genera un archivo de texto con mediciones de temperatura sintéticas.
    Cada medición es un número flotante entre -10.0 y 50.0 grados Celsius,
    con dos decimales, representando lecturas de sensores IoT.
    """
    print(f"=== Generador de Datos de Temperatura IoT ===")
    print(f"Objetivo: Crear archivo con {total_registros:,} registros.")
    
    inicio = time.time()
    
    # Crear la carpeta contenedora si no existe
    directorio = os.path.dirname(nombre_archivo)
    if directorio and not os.path.exists(directorio):
        os.makedirs(directorio)
        print(f"Directorio creado: {directorio}")
        
    # Escribir en bloques de 100,000 para optimizar el rendimiento del disco
    tamano_bloque = 100000
    cantidad_bloques = total_registros // tamano_bloque
    
    try:
        with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
            for i in range(cantidad_bloques):
                # Generar un bloque de lecturas aleatorias en memoria
                bloque = [f"{random.uniform(-10.0, 50.0):.2f}\n" for _ in range(tamano_bloque)]
                # Escribir el bloque completo al disco de una sola vez
                archivo.writelines(bloque)
                
                # Feedback visual de progreso
                if (i + 1) % 10 == 0 or (i + 1) == cantidad_bloques:
                    progreso = ((i + 1) / cantidad_bloques) * 100
                    print(f"Progreso de generación: {progreso:.0f}%...")
                    
        fin = time.time()
        tamano_mb = os.path.getsize(nombre_archivo) / (1024 * 1024)
        
        print("\n=== Generación Completada ===")
        print(f"Archivo guardado en: {nombre_archivo}")
        print(f"Tamaño del archivo: {tamano_mb:.2f} MB")
        print(f"Tiempo transcurrido: {fin - inicio:.2f} segundos.")
        
    except IOError as e:
        print(f"Error de E/S al escribir el archivo: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    # Generamos los datos en el directorio local
    generar_datos("data/temperaturas.txt", 5000000)
