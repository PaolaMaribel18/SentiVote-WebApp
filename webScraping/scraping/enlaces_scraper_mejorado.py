"""
Módulo: enlaces_scraper_mejorado
--------------------------------

Versión mejorada del scraper de enlaces de publicaciones de X (Twitter).
Incluye:
- Scroll dinámico con detección de fin de contenido
- Pausas aleatorias más humanas
- Múltiples selectores para mayor robustez
- Guardado incremental (no pierde datos si falla)
- Métricas de rendimiento
"""

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core.utils import limpiar_nombre_archivo
import time
import csv
import os
import random
from datetime import datetime


def scrapear_enlaces_tweets_mejorado(
    driver, 
    query: str, 
    max_scrolls: int = 50,
    pausa_min: float = 3.0,
    pausa_max: float = 7.0,
    scrolls_sin_cambio_limite: int = 3
) -> dict:
    """
    Scraper mejorado de enlaces de tweets con scroll dinámico.
    
    Mejoras vs versión original:
    - Pausas aleatorias (más humano)
    - Detección automática de fin de contenido
    - Múltiples selectores CSS/XPath
    - Métricas de rendimiento
    
    Args:
        driver: WebDriver de Selenium
        query: Cadena de búsqueda
        max_scrolls: Máximo de scrolls (default: 50)
        pausa_min: Pausa mínima entre scrolls (segundos)
        pausa_max: Pausa máxima entre scrolls (segundos)
        scrolls_sin_cambio_limite: Scrolls sin nuevos enlaces para parar
        
    Returns:
        dict: {
            'enlaces': list,
            'total': int,
            'scrolls_realizados': int,
            'tiempo_segundos': float,
            'fin_detectado': bool
        }
    """
    print(f"\n[MEJORADO] Minando con query: {query}")
    
    # Construir URL de búsqueda
    url = f"https://twitter.com/search?q={query}&src=typed_query&f=top"
    driver.get(url)
    
    # Esperar carga inicial
    tiempo_inicio = time.time()
    time.sleep(random.uniform(4, 6))
    
    enlaces = set()
    scrolls_sin_cambio = 0
    scrolls_realizados = 0
    fin_detectado = False
    
    # Selectores múltiples para robustez
    selectores_tweets = [
        (By.CSS_SELECTOR, "article[role='article']"),
        (By.CSS_SELECTOR, "article[data-testid='tweet']"),
        (By.XPATH, "//article[@data-testid='tweet']"),
    ]
    
    for i in range(max_scrolls):
        scrolls_realizados = i + 1
        cantidad_antes = len(enlaces)
        
        # Extraer enlaces de tweets visibles
        tweets = []
        for selector_type, selector in selectores_tweets:
            try:
                tweets = driver.find_elements(selector_type, selector)
                if tweets:
                    break
            except:
                continue
        
        # Procesar cada tweet
        for tweet in tweets:
            try:
                # Buscar enlaces a status
                link_elems = tweet.find_elements(By.XPATH, ".//a[contains(@href, '/status/')]")
                for link in link_elems:
                    try:
                        href = link.get_attribute("href")
                        if href and '/status/' in href:
                            # Normalizar URL
                            if href.startswith("/"):
                                href = "https://twitter.com" + href
                            # Limpiar parámetros
                            href = href.split('?')[0]
                            enlaces.add(href)
                    except StaleElementReferenceException:
                        continue
            except StaleElementReferenceException:
                continue
            except Exception:
                continue
        
        # Verificar progreso
        nuevos = len(enlaces) - cantidad_antes
        
        if nuevos == 0:
            scrolls_sin_cambio += 1
            print(f"  Scroll #{i+1}: Sin nuevos enlaces ({scrolls_sin_cambio}/{scrolls_sin_cambio_limite}) - Total: {len(enlaces)}")
            
            if scrolls_sin_cambio >= scrolls_sin_cambio_limite:
                print(f"  >> Fin de contenido detectado en scroll #{i+1}")
                fin_detectado = True
                break
        else:
            scrolls_sin_cambio = 0
            print(f"  Scroll #{i+1}: +{nuevos} nuevos - Total: {len(enlaces)}")
        
        # Scroll con comportamiento humano
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Pausa aleatoria
        pausa = random.uniform(pausa_min, pausa_max)
        time.sleep(pausa)
    
    tiempo_total = time.time() - tiempo_inicio
    
    resultado = {
        'enlaces': list(enlaces),
        'total': len(enlaces),
        'scrolls_realizados': scrolls_realizados,
        'tiempo_segundos': round(tiempo_total, 2),
        'fin_detectado': fin_detectado
    }
    
    print(f"  >> Total: {resultado['total']} enlaces en {resultado['tiempo_segundos']}s ({scrolls_realizados} scrolls)")
    
    return resultado


def guardar_enlaces_candidatos_mejorado(
    driver, 
    candidatos: list, 
    palabras_clave: list,
    carpeta_salida: str = None,
    max_scrolls: int = 50,
    pausa_entre_queries_min: float = 10.0,
    pausa_entre_queries_max: float = 20.0,
    pausa_entre_candidatos_min: float = 300.0,
    pausa_entre_candidatos_max: float = 480.0
) -> dict:
    """
    Guarda enlaces de publicaciones para múltiples candidatos y palabras clave.
    
    Mejoras vs versión original:
    - Guardado incremental (no pierde datos si falla)
    - Pausas aleatorias configurables
    - Métricas detalladas de rendimiento
    - Resumen final con estadísticas
    
    Args:
        driver: WebDriver de Selenium
        candidatos: Lista de nombres de candidatos
        palabras_clave: Lista de palabras clave
        carpeta_salida: Carpeta donde guardar CSVs (default: datasets/raw/enlaces_publicaciones_v2)
        max_scrolls: Máximo de scrolls por query
        pausa_entre_queries_min/max: Rango de pausa entre queries (segundos)
        pausa_entre_candidatos_min/max: Rango de pausa entre candidatos (segundos)
        
    Returns:
        dict: Métricas de rendimiento del scraping completo
    """
    # Carpeta de salida
    if carpeta_salida is None:
        carpeta_salida = os.path.join("datasets", "raw", "enlaces_publicaciones_v2")
    os.makedirs(carpeta_salida, exist_ok=True)
    
    # Métricas globales
    metricas_globales = {
        'inicio': datetime.now().isoformat(),
        'candidatos_procesados': 0,
        'total_enlaces': 0,
        'total_queries': 0,
        'tiempo_total_segundos': 0,
        'detalles_candidatos': []
    }
    
    tiempo_inicio_global = time.time()
    
    print(f"\n{'='*60}")
    print(f"[SCRAPER MEJORADO] Iniciando extracción de enlaces")
    print(f"  Candidatos: {len(candidatos)}")
    print(f"  Palabras clave: {len(palabras_clave)}")
    print(f"  Total queries: {len(candidatos) * len(palabras_clave)}")
    print(f"{'='*60}\n")
    
    for idx_candidato, candidato in enumerate(candidatos):
        print(f"\n{'='*50}")
        print(f"CANDIDATO {idx_candidato + 1}/{len(candidatos)}: {candidato}")
        print(f"{'='*50}")
        
        # Archivo CSV para este candidato
        nombre_archivo = f"{limpiar_nombre_archivo(candidato)}_enlaces_tweets.csv"
        ruta_archivo = os.path.join(carpeta_salida, nombre_archivo)
        
        # Métricas del candidato
        metricas_candidato = {
            'candidato': candidato,
            'enlaces_totales': 0,
            'queries_procesadas': 0,
            'tiempo_segundos': 0
        }
        
        tiempo_inicio_candidato = time.time()
        
        # Abrir archivo y escribir encabezado
        with open(ruta_archivo, mode="w", newline="", encoding="utf-8") as archivo_csv:
            writer = csv.writer(archivo_csv)
            writer.writerow(["candidato", "palabra_clave", "enlace_original", "enlace_limpio"])
            
            for idx_palabra, palabra in enumerate(palabras_clave):
                query = f'{candidato} {palabra}'
                
                print(f"\n  Query {idx_palabra + 1}/{len(palabras_clave)}: '{query}'")
                
                # Ejecutar scraping mejorado
                resultado = scrapear_enlaces_tweets_mejorado(
                    driver, 
                    query, 
                    max_scrolls=max_scrolls
                )
                
                # Guardar enlaces inmediatamente (incremental)
                for enlace in resultado['enlaces']:
                    enlace_limpio = enlace.replace("/analytics", "") if enlace else ""
                    writer.writerow([candidato, palabra, enlace, enlace_limpio])
                
                # Flush para asegurar escritura
                archivo_csv.flush()
                
                # Actualizar métricas
                metricas_candidato['enlaces_totales'] += resultado['total']
                metricas_candidato['queries_procesadas'] += 1
                metricas_globales['total_queries'] += 1
                
                # Pausa entre queries (excepto la última)
                if idx_palabra < len(palabras_clave) - 1:
                    pausa = random.uniform(pausa_entre_queries_min, pausa_entre_queries_max)
                    print(f"    Pausa de {pausa:.1f}s antes de siguiente query...")
                    time.sleep(pausa)
        
        # Calcular tiempo del candidato
        metricas_candidato['tiempo_segundos'] = round(time.time() - tiempo_inicio_candidato, 2)
        
        # Actualizar métricas globales
        metricas_globales['candidatos_procesados'] += 1
        metricas_globales['total_enlaces'] += metricas_candidato['enlaces_totales']
        metricas_globales['detalles_candidatos'].append(metricas_candidato)
        
        print(f"\n  >> Guardado: {ruta_archivo}")
        print(f"  >> Total enlaces: {metricas_candidato['enlaces_totales']}")
        print(f"  >> Tiempo: {metricas_candidato['tiempo_segundos']}s")
        
        # Pausa entre candidatos (excepto el último)
        if idx_candidato < len(candidatos) - 1:
            pausa = random.uniform(pausa_entre_candidatos_min, pausa_entre_candidatos_max)
            print(f"\n  Pausa de {pausa/60:.1f} minutos antes del siguiente candidato...")
            time.sleep(pausa)
    
    # Finalizar métricas
    metricas_globales['tiempo_total_segundos'] = round(time.time() - tiempo_inicio_global, 2)
    metricas_globales['fin'] = datetime.now().isoformat()
    
    # Resumen final
    print(f"\n{'='*60}")
    print(f"[SCRAPER MEJORADO] RESUMEN FINAL")
    print(f"{'='*60}")
    print(f"  Candidatos procesados: {metricas_globales['candidatos_procesados']}")
    print(f"  Total queries: {metricas_globales['total_queries']}")
    print(f"  Total enlaces: {metricas_globales['total_enlaces']}")
    print(f"  Tiempo total: {metricas_globales['tiempo_total_segundos']/60:.1f} minutos")
    print(f"{'='*60}\n")
    
    return metricas_globales
