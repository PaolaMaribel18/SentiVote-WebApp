"""
Módulo: tweets_scraper
----------------------

Lee los enlaces recolectados por el scraper de enlaces y extrae la información
de cada tweet (usuario, fecha, texto).
"""

import os
import time
import csv
import random
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from core.utils import crear_carpeta_si_no_existe

def extraer_informacion_tweets(driver, carpeta_entrada: str, carpeta_salida: str):
    """
    Procesa los archivos de enlaces y extrae información de cada tweet.

    Args:
        driver: Instancia del WebDriver.
        carpeta_entrada (str): Carpeta donde están los CSV de enlaces.
        carpeta_salida (str): Carpeta donde se guardarán los CSV con información.
    """
    crear_carpeta_si_no_existe(carpeta_salida)

    for archivo_csv in os.listdir(carpeta_entrada):
        if not archivo_csv.endswith(".csv"):
            continue

        nombre_candidato = archivo_csv.replace("_enlaces_tweets.csv", "")
        path_archivo = os.path.join(carpeta_entrada, archivo_csv)
        df = pd.read_csv(path_archivo)
        enlaces = df['enlace_limpio'].dropna().tolist()

        datos_tweets = []
        contador = 0

        for url in enlaces:
            try:
                if "/status/" not in url or "/analytics" in url:
                    continue

                driver.get(url)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "time")))

                usuario = "N/A"
                try:
                    # 1. Buscar el contenedor del nombre de usuario (más estable)
                    # El 'data-testid="User-Name"' es el contenedor general.
                    user_container = driver.find_element(By.XPATH, '//div[@data-testid="User-Name"]')
                    
                    # 2. Buscar el <span> que contiene el handle (@...) dentro de ese contenedor.
                    # Usamos un selector XPath que busca cualquier span dentro del contenedor que empiece con '@'.
                    usuario_elem = user_container.find_element(By.XPATH, './/span[starts-with(text(), "@")]')
                    
                    usuario = usuario_elem.text
                    
                except NoSuchElementException:
                    # Si falla, simplemente el usuario es N/A
                    usuario = "N/A"
                
                fecha_elem = driver.find_element(By.TAG_NAME, "time")
                fecha = fecha_elem.get_attribute("datetime") if fecha_elem else "N/A"

                try:
                    texto_elem = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="tweetText"]')
                    texto = texto_elem.text
                except:
                    texto = "N/A"

                datos_tweets.append({
                    "candidato": nombre_candidato,
                    "url": url,
                    "usuario": usuario,
                    "fecha": fecha,
                    "texto": texto
                })

                contador += 1
                time.sleep(random.uniform(5, 10))
                if contador % 40 == 0:
                    time.sleep(600)

            except Exception as e:
                print(f"Error en {url}: {e}")
                continue

        ruta_salida = os.path.join(carpeta_salida, f"{nombre_candidato}_informacion_tweets.csv")
        with open(ruta_salida, mode='w', newline='', encoding='utf-8') as archivo_out:
            writer = csv.DictWriter(archivo_out, fieldnames=["candidato", "url", "usuario", "fecha", "texto"])
            writer.writeheader()
            writer.writerows(datos_tweets)

        print(f"Guardado: {ruta_salida}")
