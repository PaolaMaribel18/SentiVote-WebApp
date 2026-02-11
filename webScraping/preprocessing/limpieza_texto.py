import pandas as pd
import string
import nltk
import os
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize
from typing import Dict, Any

# Descargar recursos necesarios de NLTK solo si aún no están descargados
try:
    nltk.data.find('tokenizers/punkt')
except nltk.downloader.DownloadError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except nltk.downloader.DownloadError:
    nltk.download('stopwords')


# Diccionario de normalización personalizado
NORMALIZATION_DICT = {
    'q': 'que', 'xq': 'porque', 'xk': 'porque', 'tmb': 'también',
    'tb': 'también', 'ntp': 'no te preocupes', 'k': 'que', 'd': 'de',
    'x': 'por', 'xD': 'jajaja', 'jaja': 'jajaja', 'jaj': 'jajaja',
    'bn': 'bien', 'holi': 'hola', 'bno': 'bueno', 'pa': 'para',
    'toy': 'estoy', 'salu2': 'saludos' # Añadido un ejemplo
}

def clean_text(text: Any) -> str:
    """Realiza la limpieza básica: minúsculas y eliminación de puntuación."""
    if pd.isnull(text):
        return ""
    text = str(text).lower()
    # Eliminar puntuación
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text.strip()

def normalize_text(text: str, normalization_dict: Dict[str, str]) -> str:
    """Normaliza jerga y abreviaturas comunes."""
    tokens = text.split()
    # Usa get() para devolver el token si no se encuentra en el diccionario
    normalized_tokens = [normalization_dict.get(token, token) for token in tokens]
    return " ".join(normalized_tokens)

def preprocess_text(text: Any, normalization_dict: Dict[str, str]) -> str:
    """Aplica limpieza básica, normalización de jerga y tokenización."""
    cleaned = clean_text(text)
    normalized = normalize_text(cleaned, normalization_dict)
    
    # Tokenización solo si el texto no está vacío después de la limpieza
    if normalized:
        tokens = word_tokenize(normalized, language='spanish')
        return " ".join(tokens)
    return ""

def limpiar_y_normalizar_corpus(
    ruta_archivo_entrada: str, 
    carpeta_salida: str,
    nombre_archivo_salida: str = "corpus_preprocesado.csv",
    normalization_dict: Dict[str, str] = NORMALIZATION_DICT
) -> None:
    """
    Lee el corpus consolidado, aplica la limpieza, normalización y guarda el resultado.

    Args:
        ruta_archivo_entrada (str): Ruta completa del CSV a leer.
        carpeta_salida (str): Carpeta donde se guardará el CSV limpio.
        nombre_archivo_salida (str): Nombre del archivo CSV de salida.
        normalization_dict (Dict[str, str]): Diccionario de jerga para normalizar.
    """
    
    # 0. Verificación de Carpeta de Salida
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
        print(f"Creada carpeta de salida: {carpeta_salida}")

    # 1. Lectura de Datos y Filtrado Inicial
    try:
        df = pd.read_csv(ruta_archivo_entrada)
        print(f"Archivo cargado. Filas iniciales: {len(df)}")
    except Exception as e:
        print(f"Error al leer el archivo: {ruta_archivo_entrada}. Error: {e}")
        return

    # Eliminación de filas con texto nulo en columnas clave (ANTES de limpiar)
    filas_iniciales = len(df)
    df = df.dropna(subset=['texto', 'texto_comentario']).reset_index(drop=True)
    print(f"Filas nulas eliminadas. Filas restantes: {len(df)} (Eliminados: {filas_iniciales - len(df)})")

    # 2. Aplicar Preprocesamiento
    print("\nAplicando limpieza y normalización...")
    
    # Aplicar limpieza a la publicación original
    df['texto_limpio'] = df['texto'].apply(lambda x: preprocess_text(x, normalization_dict))
    
    # Aplicar limpieza al comentario
    df['texto_comentario_limpio'] = df['texto_comentario'].apply(lambda x: preprocess_text(x, normalization_dict))
    
    # 3. Eliminación de Duplicados (DESPUÉS de la limpieza)
    print("\nEliminando duplicados...")
    
    # Primera pasada: eliminar comentarios con texto limpio idéntico
    filas_antes_dup_texto = len(df)
    df = df.drop_duplicates(subset=['texto_comentario_limpio'], keep='first').reset_index(drop=True)
    print(f"Duplicados por texto_comentario_limpio eliminados. Filas restantes: {len(df)} (Eliminados: {filas_antes_dup_texto - len(df)})")
    
    # Segunda pasada: eliminar filas completamente idénticas (por si acaso)
    filas_antes_dup_completo = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    print(f"Duplicados completos eliminados. Filas restantes: {len(df)} (Eliminados: {filas_antes_dup_completo - len(df)})")
    
    # 4. Guardado Final
    
    # Seleccionar columnas requeridas (añadimos todas las columnas limpias)
    columnas_finales = [
        'candidato', 'usuario', 'fecha', 
        'texto', 'texto_limpio', 
        'texto_comentario', 'texto_comentario_limpio',
    ]
    
    # Filtra solo las columnas que existen en el DataFrame
    df_final = df[[col for col in columnas_finales if col in df.columns]]

    ruta_salida_final = os.path.join(carpeta_salida, nombre_archivo_salida)
    
    df_final.to_csv(ruta_salida_final, index=False)

    print(f"\nDatos limpiados y guardados en '{ruta_salida_final}'")
