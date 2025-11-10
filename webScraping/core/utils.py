"""
Módulo: utils
--------------

Contiene funciones auxiliares reutilizables para limpieza de texto, nombres de archivos
y otras operaciones comunes.
"""

import unicodedata
import os

def limpiar_nombre_archivo(nombre: str) -> str:
    """
    Limpia un texto para usarlo como nombre de archivo válido en el sistema.

    - Elimina tildes y acentos.
    - Reemplaza espacios por guiones bajos.

    Args:
        nombre (str): Texto original.

    Returns:
        str: Texto limpio y seguro para usar como nombre de archivo.
    """
    nombre_sin_tildes = ''.join(
        c for c in unicodedata.normalize('NFD', nombre)
        if unicodedata.category(c) != 'Mn'
    )
    return nombre_sin_tildes.replace(" ", "_")

def crear_carpeta_si_no_existe(ruta: str):
    """
    Crea una carpeta si no existe.

    Args:
        ruta (str): Ruta de la carpeta a crear.
    """
    os.makedirs(ruta, exist_ok=True)
