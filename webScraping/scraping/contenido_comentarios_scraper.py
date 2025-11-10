import os
import time
import csv
import random
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def minar_texto_comentarios(driver, carpeta_entrada: str, carpeta_salida: str, limite=None):
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    archivos = [f for f in os.listdir(carpeta_entrada) if f.endswith(".csv")]
    clase_objetivo = "css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-1inkyih r-16dba41 r-bnwqim r-135wba7"
    
    contador_global = 0
    
    FIELDNAMES = [
        "candidato", "enlace_limpio", "usuario", "fecha", "texto",
        "enlace_comentario_limpio", "texto_comentario"
    ]

    for archivo in archivos:
        ruta_csv = os.path.join(carpeta_entrada, archivo)
        nombre_candidato = archivo.replace("_enlaces_comentarios.csv", "")
        ruta_salida = os.path.join(carpeta_salida, f"{nombre_candidato}_datos_completos.csv")
        
        try:
            df = pd.read_csv(ruta_csv)
        except Exception as e:
            print(f"Error al leer {ruta_csv}: {e}")
            continue

        # Lista temporal para guardar los comentarios entre cada pausa/guardado
        comentarios_buffer = [] 
        
        total_filas = len(df)
        print(f"\n--- Procesando archivo: {archivo} ({total_filas} comentarios/filas) ---")

        for i, fila in df.iterrows():
            if limite and i >= limite:
                break
            
            contador_global += 1

            enlace = fila.get("enlace_comentario_limpio", None)
            
            if pd.isna(enlace) or not isinstance(enlace, str) or not enlace.startswith("http"):
                texto = None
            else:
                try:
                    driver.get(enlace)
                    
                    # Pausa corta aleatoria antes de buscar, simula la lectura humana
                    time.sleep(random.uniform(1, 3)) 
                    
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, f'div.{".".join(clase_objetivo.split())}'))
                    )
                    
                    div = driver.find_element(By.CSS_SELECTOR, f'div.{".".join(clase_objetivo.split())}')
                    partes = div.find_elements(By.XPATH, ".//*")
                    texto = " ".join([p.text.strip() for p in partes if p.text.strip()]) or div.text.strip()
                    print(f"[{contador_global}/{total_filas}] Extraído: {enlace[:40]}...")
                    
                except (NoSuchElementException, TimeoutException) as e:
                    texto = "N/A"
                    print(f"[{contador_global}/{total_filas}] No se pudo extraer texto de: {enlace[:40]}... Error: {e.__class__.__name__}")
                except Exception as e:
                    texto = "N/A"
                    print(f"[{contador_global}/{total_filas}] Error desconocido en {enlace[:40]}... Error: {e.__class__.__name__}")
            
            # --- ALMACENAR EN EL BUFFER ---
            comentarios_buffer.append({
                "candidato": fila.get("candidato", ""),
                "enlace_limpio": fila.get("enlace_limpio", ""),
                "usuario": fila.get("usuario", ""),
                "fecha": fila.get("fecha", ""),
                "texto": fila.get("texto", ""),
                "enlace_comentario_limpio": fila.get("enlace_comentario_limpio", ""),
                "texto_comentario": texto
            })
            
            # --- PAUSA Y GUARDADO ITERATIVO ---
            if contador_global % 40 == 0:
                
                # 1. Guardar el buffer en el archivo
                # Determinar si el archivo ya existe para saber si escribir encabezado
                escribir_encabezado = not os.path.exists(ruta_salida)
                
                # 'a' = append (añadir al final)
                with open(ruta_salida, mode='a', newline='', encoding='utf-8') as archivo_out:
                    writer = csv.DictWriter(archivo_out, fieldnames=FIELDNAMES)
                    
                    if escribir_encabezado:
                        writer.writeheader()
                        
                    writer.writerows(comentarios_buffer)
                
                print(f"Guardado parcial de {len(comentarios_buffer)} filas en {ruta_salida}.")
                
                # 2. Limpiar el buffer
                comentarios_buffer = [] 
                
                print(f"Se han minado {contador_global} comentarios en total. Esperando 10 minutos.")
                time.sleep(600) 

        # Si quedan elementos en el buffer al final del archivo, guárdalos
        if comentarios_buffer:
            escribir_encabezado = not os.path.exists(ruta_salida)
            with open(ruta_salida, mode='a', newline='', encoding='utf-8') as archivo_out:
                writer = csv.DictWriter(archivo_out, fieldnames=FIELDNAMES)
                if escribir_encabezado:
                    writer.writeheader()
                writer.writerows(comentarios_buffer)
                
            print(f"\nGuardado final de {len(comentarios_buffer)} filas restantes en {ruta_salida}.")
        
        print(f"\n--- Archivo {archivo} completado. Total global minado: {contador_global} ---")