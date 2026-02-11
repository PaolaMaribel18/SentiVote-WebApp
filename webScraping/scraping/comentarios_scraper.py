import os
import time
import csv
import random
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# -------- FUNCIÓN EXTRAER COMENTARIOS ----------
def extraer_enlaces_comentarios_csvs(driver, carpeta_entrada: str, carpeta_salida: str, max_scrolls=100):
    """
    Extrae enlaces de comentarios de publicaciones usando la versión mejorada
    
    Parámetros:
        driver: Instancia de Selenium WebDriver
        carpeta_entrada: Carpeta con CSVs de publicaciones
        carpeta_salida: Carpeta donde guardar los enlaces de comentarios
        max_scrolls: Número máximo de scrolls para cargar comentarios
    """
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
                    
                    # Usar función mejorada
                enlaces_comentarios = extraer_enlaces_comentarios_mejorado(driver, url, max_scrolls=max_scrolls)
                    
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
                    
                print(f" - {len(enlaces_comentarios)} comentarios en {url}")
                
            except Exception as e:
                print(f"Error en {url}: {e}")
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
            
        print(f"\n - Guardado en {ruta_salida} ({len(comentarios_info)} filas)")
        
        
def scroll_comentarios_mejorado(driver, max_scrolls=100, pausa_min=7, pausa_max=10):
    """
    Scroll dinámico MEJORADO que extrae comentarios mientras scrollea.
    
    MEJORAS vs versión actual:
    - Scroll hasta el final (no límite de 15)
    - Pausas más largas (7-10s vs 5s)
    - Extrae enlaces mientras scrollea (no pierde datos)
    - Detecta fin de contenido automáticamente
    
    Args:
        driver: WebDriver
        max_scrolls: Máximo de scrolls (100 por defecto)
        pausa_min: Mínimo de segundos entre scrolls
        pausa_max: Máximo de segundos entre scrolls
        
    Returns:
        set: Enlaces únicos de comentarios encontrados
    """
    enlaces_comentarios = set()
    scrolls_sin_cambio = 0
    ultima_cantidad = 0
    
    print(f"- Iniciando scroll de comentarios (max: {max_scrolls})...")
    
    for i in range(max_scrolls):
        # 1. EXTRAER comentarios del contenido actual ANTES de scrollear
        try:
            # Múltiples selectores para mayor robustez
            selectores = [
                '//article[@data-testid="tweet"]',
                '//article[@role="article"]',
                '//div[@data-testid="cellInnerDiv"]//article'
            ]
            
            tweets = []
            for selector in selectores:
                try:
                    elementos = driver.find_elements(By.XPATH, selector)
                    if elementos:
                        tweets = elementos
                        break
                except:
                    continue
            
            # Extraer enlaces de cada tweet/comentario
            for tweet in tweets:
                try:
                    # Buscar todos los enlaces dentro del tweet
                    links = tweet.find_elements(By.XPATH, ".//a[contains(@href, '/status/')]")
                    for link in links:
                        href = link.get_attribute("href")
                        if href and "/status/" in href:
                            # Limpiar URL
                            if href.startswith("/"):
                                href = "https://twitter.com" + href
                            href = href.split('?')[0]  # Quitar parámetros
                            enlaces_comentarios.add(href)
                except:
                    continue
                    
        except Exception as e:
            pass
        
        # 2. Hacer scroll
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # 3. Pausa aleatoria más larga para que cargue
        pausa = random.uniform(pausa_min, pausa_max)
        time.sleep(pausa)
        
        # 4. Verificar si encontramos nuevos comentarios
        cantidad_actual = len(enlaces_comentarios)
        
        if cantidad_actual == ultima_cantidad:
            scrolls_sin_cambio += 1
            print(f"   Scroll {i+1}: Sin nuevos comentarios ({scrolls_sin_cambio}/3) - Total: {cantidad_actual}")
            
            if scrolls_sin_cambio >= 3:
                print(f"- Fin de comentarios alcanzado en scroll {i+1}")
                break
        else:
            nuevos = cantidad_actual - ultima_cantidad
            scrolls_sin_cambio = 0
            print(f"   Scroll {i+1}: +{nuevos} nuevos comentarios - Total: {cantidad_actual}")
            ultima_cantidad = cantidad_actual
    else:
        print(f"- Límite máximo de scrolls alcanzado ({max_scrolls})")
    
    print(f" ** Total de comentarios extraídos: {len(enlaces_comentarios)} **")
    return enlaces_comentarios


def extraer_enlaces_comentarios_mejorado(
    driver, 
    url_publicacion: str,
    max_scrolls=100,
    pausa_scroll_min=7,
    pausa_scroll_max=10
):
    """
    Extrae TODOS los enlaces de comentarios de UNA publicación específica.
    
    Versión MEJORADA con:
    Scroll dinámico hasta el final
    Sin límites artificiales
    Extracción durante el scroll
    Múltiples selectores robustos
    
    Args:
        driver: WebDriver
        url_publicacion: URL completa de la publicación
        max_scrolls: Máximo de scrolls (100 por defecto)
        pausa_scroll_min: Pausa mínima entre scrolls
        pausa_scroll_max: Pausa máxima entre scrolls
        
    Returns:
        list: Lista de enlaces únicos a comentarios
    """
    print(f"\n{'='*80}")
    print(f"- Extrayendo comentarios de: {url_publicacion}")
    print(f"{'='*80}")
    
    try:
        # Navegar a la publicación
        driver.get(url_publicacion)
        
        # Esperar a que cargue la página
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "article"))
        )
        
        # Pausa inicial para que cargue completamente
        time.sleep(random.uniform(3, 5))
        
        # Scroll y extracción mejorados
        enlaces = scroll_comentarios_mejorado(
            driver, 
            max_scrolls=max_scrolls,
            pausa_min=pausa_scroll_min,
            pausa_max=pausa_scroll_max
        )
        
        # Filtrar la publicación original
        enlaces_comentarios = [e for e in enlaces if e != url_publicacion.split('?')[0]]
        
        print(f"\n- Extracción completada: {len(enlaces_comentarios)} comentarios")
        return enlaces_comentarios
        
    except Exception as e:
        print(f"Error al extraer comentarios: {e}")
        return []