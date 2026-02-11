from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from core.login_twitter import login_twitter
from core.utils import limpiar_nombre_archivo
import time
import csv
import unicodedata
import os
import random

def scrapear_enlaces_tweets_scroll_incremental(driver, query, scrolls=15):
    print(f"\nMinando con query: {query}")
    url = f"https://twitter.com/search?q={query}&src=typed_query&f=top"
    driver.get(url)
    time.sleep(5)

    enlaces = set()

    for i in range(scrolls):
        print(f"  Scroll #{i+1}...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        tweets = driver.find_elements(By.CSS_SELECTOR, "article[role='article']")
        for tweet in tweets:
            try:
                link_elems = tweet.find_elements(By.XPATH, ".//a[contains(@href, '/status/')]")
                for link in link_elems:
                    href = link.get_attribute("href")
                    if href and '/status/' in href:
                        if href.startswith("/"):
                            href = "https://twitter.com" + href
                        enlaces.add(href)
            except:
                continue

    print(f"Enlaces encontrados: {len(enlaces)}")
    return list(enlaces)

"""
Módulo: enlaces_scraper
-----------------------

Extrae enlaces de publicaciones de X (Twitter) para un conjunto de candidatos y palabras clave.
Guarda los resultados en archivos CSV dentro de datasets/raw/enlaces_candidatos.
"""

def guardar_enlaces_candidatos(driver, candidatos_presidenciales_2025, palabras_clave):
    """
    Ejecuta el scraping de enlaces de publicaciones de Twitter (X) para varios candidatos y palabras clave.
    Guarda los resultados en la carpeta datasets/raw/enlaces_candidatos.

    Args:
        usuario (str): Usuario de Twitter.
        password (str): Contraseña de Twitter.
        correo (str): Correo de recuperación/verificación.
        candidatos_presidenciales_2025 (list): Lista de nombres de candidatos.
        palabras_clave (list): Lista de palabras clave.
    """

    # Crear carpeta dentro de datasets/raw/enlaces_publicaciones
    carpeta_salida = os.path.join("datasets", "raw", "enlaces_publicaciones")
    os.makedirs(carpeta_salida, exist_ok=True)
    
    # Iniciar sesión en Twitter
    # login_twitter(usuario, password, correo)

    # Recorrer los candidatos
    for candidato in candidatos_presidenciales_2025:
        # Construir la ruta completa del archivo CSV
        nombre_archivo = f"{limpiar_nombre_archivo(candidato)}_enlaces_tweets.csv"
        ruta_archivo = os.path.join(carpeta_salida, nombre_archivo)

        # Crear y escribir encabezado del CSV
        with open(ruta_archivo, mode="w", newline="", encoding="utf-8") as archivo_csv:
            writer = csv.writer(archivo_csv)
            writer.writerow(["candidato", "palabra_clave", "enlace_original", "enlace_limpio"])

            # Recorrer las palabras clave
            for palabra in palabras_clave:
                query = f'{candidato} {palabra}'
                enlaces = scrapear_enlaces_tweets_scroll_incremental(driver, query, scrolls=25)

                # Escribir los enlaces obtenidos
                for enlace in enlaces:
                    enlace_original = enlace
                    enlace_limpio = enlace.replace("/analytics", "") if enlace else ""
                    writer.writerow([candidato, palabra, enlace_original, enlace_limpio])

        print(f"Guardado: {ruta_archivo}")
        pausa = 420 + random.uniform(-30, 30)
        print(f" - Pausa de {pausa/60:.1f} minutos antes del siguiente candidato...")
        time.sleep(pausa)

