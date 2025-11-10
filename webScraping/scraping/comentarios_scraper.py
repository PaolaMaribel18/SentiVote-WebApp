import os
import time
import csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

# -------- FUNCIÓN SCROLL DINÁMICO ----------
def scroll_comentarios(driver, max_intentos=15, pausa=5):
    """
    Scrollea hacia abajo hasta que no aparezcan más tweets nuevos o se alcance max_intentos
    """
    old_count = 0
    intentos = 0
    while intentos < max_intentos:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pausa)

        tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
        new_count = len(tweets)

        if new_count == old_count:
            # No cargaron más tweets
            break
        else:
            old_count = new_count
            intentos += 1

    return driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')

# -------- FUNCIÓN EXTRAER COMENTARIOS ----------
def extraer_enlaces_comentarios_csvs(driver, carpeta_entrada: str, carpeta_salida: str, limite_por_publicacion=200):
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    archivos = [f for f in os.listdir(carpeta_entrada) if f.endswith(".csv")]

    for archivo in archivos:
        ruta_csv = os.path.join(carpeta_entrada, archivo)
        nombre_candidato = archivo.replace("_informacion_tweets.csv", "")
        df = pd.read_csv(ruta_csv)

        comentarios_info = []

        for _, fila in df.iterrows():
            try:
                url = fila['url'] if 'url' in fila else fila['enlace_limpio']
                if "/status/" not in url:
                    print(f"Ignorando: {url}")
                    continue

                driver.get(url)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "time")))

                # 🔥 Scroll dinámico para cargar más respuestas
                tweets = scroll_comentarios(driver)

                enlaces_comentarios = set()
                for tweet in tweets[1:]:
                    links = tweet.find_elements(By.XPATH, ".//a[contains(@href, '/status/')]")
                    for link in links:
                        href = link.get_attribute("href")
                        if href and "/status/" in href and href != url:
                            if href.startswith("/"):
                                href = "https://twitter.com" + href
                            enlaces_comentarios.add(href)
                    if len(enlaces_comentarios) >= limite_por_publicacion:
                        break

                if not enlaces_comentarios:
                    comentarios_info.append({
                        "candidato": fila.get("candidato", nombre_candidato),
                        "enlace_limpio": fila["url"] if "url" in fila else fila["enlace_limpio"],
                        "usuario": fila.get("usuario", ""),
                        "fecha": fila.get("fecha", ""),
                        "texto": fila.get("texto", ""),
                        "enlace_comentario_original": None,
                        "enlace_comentario_limpio": None
                    })
                else:
                    for enlace in enlaces_comentarios:
                        comentarios_info.append({
                            "candidato": fila.get("candidato", nombre_candidato),
                            "enlace_limpio": fila["url"] if "url" in fila else fila["enlace_limpio"],
                            "usuario": fila.get("usuario", ""),
                            "fecha": fila.get("fecha", ""),
                            "texto": fila.get("texto", ""),
                            "enlace_comentario_original": enlace,
                            "enlace_comentario_limpio": enlace.replace("/analytics", "")
                        })

                print(f"🧵 {len(enlaces_comentarios)} comentarios en {url}")

            except Exception as e:
                print(f"❌ Error en {url}: {e}")
                continue

        # Guardar en CSV
        nombre_salida = f"{nombre_candidato}_enlaces_comentarios.csv"
        ruta_salida = os.path.join(carpeta_salida, nombre_salida)

        with open(ruta_salida, mode='w', newline='', encoding='utf-8') as archivo_out:
            writer = csv.DictWriter(archivo_out, fieldnames=[
                "candidato", "enlace_limpio", "usuario", "fecha", "texto",
                "enlace_comentario_original", "enlace_comentario_limpio"
            ])
            writer.writeheader()
            writer.writerows(comentarios_info)

        print(f"\n✅ Guardado en {ruta_salida} ({len(comentarios_info)} filas)")