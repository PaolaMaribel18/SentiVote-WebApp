"""
Script para UNIFICAR corpus viejo y nuevo, y aplicar limpieza PROFUNDA.
Este script:
1. Lee el corpus original.
2. Lee el corpus nuevo.
3. Los fusiona en uno solo.
4. Aplica la función limpiar_y_normalizar_corpus (que elimina duplicados).
5. Guarda el resultado en la carpeta datasets/raw/corpus_completo.
"""

import pandas as pd
import os
import sys
from pathlib import Path

# Añadir el directorio actual al path para importar módulos locales
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from preprocessing.limpieza_texto import limpiar_y_normalizar_corpus

def unificar_y_limpiar(
    ruta_original_str="webScraping/datasets/processed/corpus_preprocesado.csv", 
    ruta_nuevo_str="webScraping/datasets/processed/corpus_preprocesado_corregido.csv",
    ruta_salida_final="webScraping/datasets/processed/corpus_preprocesado_unificado.csv"
):
    """
    Fusiona dos CSVs (ej: histórico y reciente) y aplica limpieza para eliminar duplicados.
    """
    # Rutas de los archivos usando Path para compatibilidad SO
    base_path = Path(os.getcwd())
    
    # Manejo de rutas relativas si se pasan como strings
    ruta_original = Path(ruta_original_str) if os.path.isabs(ruta_original_str) else base_path / ruta_original_str
    ruta_nuevo = Path(ruta_nuevo_str) if os.path.isabs(ruta_nuevo_str) else base_path / ruta_nuevo_str
    
    # Verificación
    if not ruta_original.exists():
        print(f"- No se encuentra el archivo 'histórico/original': {ruta_original}")
        print("   -> Se usará SOLAMENTE el archivo nuevo.")
        df_orig = pd.DataFrame() # DataFrame vacío
    else:
        df_orig = pd.read_csv(ruta_original)
        print(f"- Archivo Original cargado: {len(df_orig)} filas.")

    if not ruta_nuevo.exists():
        print(f"- No se encuentra el archivo nuevo: {ruta_nuevo}")
        return

    df_new = pd.read_csv(ruta_nuevo)
    print(f"- Archivo Nuevo cargado:    {len(df_new)} filas.")

    # 3. Concatenar (Fusión Cruda)
    df_concat = pd.concat([df_orig, df_new], ignore_index=True)
    
    # Guardar temporalmente para que limpiar_y_normalizar lo procese
    temp_path = base_path / "webScraping" / "datasets" / "temp_unificado_raw.csv"
    os.makedirs(temp_path.parent, exist_ok=True)
    df_concat.to_csv(temp_path, index=False)
    
    print(f"Fusionados en memoria: {len(df_concat)} filas.")

    # 4. Aplicar Limpieza y Deduplicación (Usando la lógica existente en limpieza_texto)
    print("\n- Ejecutando limpieza y desduplicación...")
    
    # Nota: limpiar_y_normalizar_corpus toma (entrada, carpeta_salida, nombre_archivo)
    carpeta_salida = Path(ruta_salida_final).parent
    nombre_archivo = Path(ruta_salida_final).name
    
    limpiar_y_normalizar_corpus(str(temp_path), str(carpeta_salida), nombre_archivo_salida=nombre_archivo)
    
    # Limpieza archivo temporal
    if temp_path.exists():
        os.remove(temp_path)

if __name__ == "__main__":
    unificar_y_limpiar()
