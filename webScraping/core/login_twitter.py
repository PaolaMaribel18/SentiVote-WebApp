"""
Módulo: login_twitter
----------------------

Automatiza el proceso de inicio de sesión en X (Twitter) usando Selenium.
Esta versión mejora la lógica de estado y usa PAUSAS ALEATORIAS y SIMULACIÓN DE TECLEO
para evadir la detección de bots.
"""

import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

# ---------------------- FUNCIÓN AUXILIAR DE SIMULACIÓN DE ESCRITURA ----------------------

def escribir_como_humano(element, text: str, min_delay: float = 0.05, max_delay: float = 0.25):
    """
    Simula la escritura de texto en un elemento, letra por letra, con retrasos aleatorios.
    """
    element.clear()
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(min_delay, max_delay))
    time.sleep(random.uniform(0.5, 1.5))  # Pausa extra al final


# ---------------------- FUNCIÓN PRINCIPAL DE LOGIN ----------------------

def login_twitter(driver, usuario: str, password: str, correo: str = None):
    """
    Inicia sesión en Twitter (X) usando credenciales provistas, con lógica adaptada
    al flujo actual (correo y contraseña).
    """
    driver.get("https://twitter.com/i/flow/login")
    time.sleep(random.uniform(5.0, 8.0))

    # Control de qué datos ya se ingresaron
    datos_ingresados = {
        "correo": False,
        "usuario": False,
        "password": False,
        "verificacion": False
    }

    while True:
        # Pausa aleatoria entre intentos
        time.sleep(random.uniform(2.5, 4.5))

        try:
            # Intentar encontrar campo de texto (correo o usuario)
            input_text = driver.find_element(By.NAME, "text")

            # --- Paso 1: Ingreso de correo ---
            if not datos_ingresados["correo"] and correo:
                print("Paso 1: Ingresando Correo con simulación de tecleo...")
                escribir_como_humano(input_text, correo)
                time.sleep(random.uniform(3.0, 5.0))
                
                driver.find_element(By.XPATH, '//span[text()="Siguiente"]').click()
                datos_ingresados["correo"] = True

            # --- Paso 2: Ingreso de usuario (solo si Twitter lo pide) ---
            elif not datos_ingresados["usuario"]:
                try:
                    print("Verificando si Twitter solicita usuario adicional...")
                    escribir_como_humano(input_text, usuario)
                    time.sleep(random.uniform(3.0, 5.0))
                    driver.find_element(By.XPATH, '//span[text()="Siguiente"]').click()
                    datos_ingresados["usuario"] = True
                except Exception:
                    # Si no hay campo de usuario o no aplica, simplemente continúa
                    print("Twitter no solicita usuario. Pasando al paso de contraseña.")
                    datos_ingresados["usuario"] = True

            # --- Paso 3: Verificación adicional (si aplica) ---
            elif datos_ingresados["usuario"] and not datos_ingresados["verificacion"] and correo:
                print("Paso 3: Verificación adicional (Correo/Usuario)...")
                escribir_como_humano(input_text, correo or usuario)
                time.sleep(random.uniform(3.0, 5.0))
                driver.find_element(By.XPATH, '//span[text()="Siguiente"]').click()
                datos_ingresados["verificacion"] = True

            else:
                time.sleep(random.uniform(2.0, 4.0))

        except NoSuchElementException:
            # Si no se encuentra el campo de texto, verificar si hay campo de contraseña
            try:
                input_password = driver.find_element(By.NAME, "password")

                if not datos_ingresados["password"]:
                    print("Paso 4: Ingresando Contraseña con simulación de tecleo...")
                    escribir_como_humano(input_password, password, min_delay=0.10, max_delay=0.35)
                    time.sleep(random.uniform(4.0, 6.0))

                    driver.find_element(By.XPATH, '//span[text()="Iniciar sesión"]').click()
                    datos_ingresados["password"] = True

                    time.sleep(random.uniform(8.0, 15.0))  # Espera tras iniciar sesión
                    print("✅ Inicio de sesión completado. Verificando redirección...")
                    break

            except NoSuchElementException:
                print("Esperando el siguiente campo (correo o contraseña)...")
                time.sleep(random.uniform(4.0, 6.0))
