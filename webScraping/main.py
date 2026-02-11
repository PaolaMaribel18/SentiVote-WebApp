from core.login_twitter import login_twitter
from core.dirver_manager import get_driver, close_driver
from core.utils import limpiar_nombre_archivo, crear_carpeta_si_no_existe
from scraping.enlaces_scraper import guardar_enlaces_candidatos
from dotenv import load_dotenv
from pathlib import Path
import os
import time

candidatos_presidenciales_2025 = [
    "Daniel Noboa"#, "Luisa González", "Wilson Gómez Vascones", "Jimmy Jairala",
    # "Jorge Escala", "Andrea González Náder", "Henry Kronfle", "Carlos Rabascall",
    #"Leonidas Iza", "Iván Saquicela", "Francesco Tabacchi", "Henry Cucalón",
    #""Enrique Gómez", "Víctor Araus", "Juan Iván Cueva", "Pedro Granja"
]

palabras_clave = [
    "elecciones 2025"
    # , "presidenciales 2025", "candidato presidencial", "candidatura 2025",
    # "campaña presidencial", "Ecuador 2025", "presidente Ecuador", "voto 2025",
    # "debate presidencial", "elecciones Ecuador"
]

driver = get_driver()

# 1. Obtenemos el Directorio de Trabajo Actual (donde se ejecuta el Notebook)
#    Si ejecutas desde 'proyecto/webScraping', esto devolverá 'proyecto/webScraping'
current_dir = Path(os.getcwd())

# 2. Subimos un nivel para llegar a la carpeta 'proyecto/' (donde está .env)
#    Esto cambia la ruta de 'proyecto/webScraping' a 'proyecto'
base_dir = current_dir.parent

# 3. Construimos la ruta completa al archivo .env
dotenv_path = base_dir / '.env'

# --- Carga de Variables ---
load_dotenv(dotenv_path=dotenv_path)

# --- Llamada de Variables ---
username = os.getenv("X_USERNAME")
password = os.getenv("X_PASSWORD")
email = os.getenv("X_EMAIL")

login_twitter(driver, username, password, email)

guardar_enlaces_candidatos(driver, candidatos_presidenciales_2025, palabras_clave)

close_driver(driver)