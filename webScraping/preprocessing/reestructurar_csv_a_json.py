import pandas as pd
import json
import os
from typing import Dict, Any, List

def reestructurar_csv_a_json_simple(ruta_csv_entrada: str, ruta_json_salida: str) -> None:
    """
    Carga un archivo CSV y lo reestructura en un formato JSON jerárquico,
    agrupando los comentarios por la publicación original (identificada por
    candidato y fecha).

    Args:
        ruta_csv_entrada (str): Ruta completa del archivo CSV a leer.
        ruta_json_salida (str): Ruta completa del archivo JSON a guardar.
    """
    
    # 0. Crear carpeta de salida si no existe
    carpeta_salida = os.path.dirname(ruta_json_salida)
    if carpeta_salida and not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
        print(f"Creada carpeta de salida: {carpeta_salida}")

    # 1. Cargar el archivo CSV
    try:
        df = pd.read_csv(ruta_csv_entrada)
        print(f"Archivo CSV cargado: {len(df)} filas.")
    except Exception as e:
        print(f"Error al cargar el CSV '{ruta_csv_entrada}': {e}")
        return

    # 2. Estructuras de datos para la reestructuración
    posts_seen: Dict[str, Dict[str, Any]] = {}
    
    # 3. Iterar y reestructurar los datos
    print("Reestructurando datos...")
    
    for _, row in df.iterrows():
        # Un identificador único para cada publicación
        post_id = f"{row['candidato']}_{row['fecha']}" 
        
        # 3.1. Si la publicación no ha sido agregada, crear su estructura (el POST)
        if post_id not in posts_seen:
            post_data = {
                "id_post": len(posts_seen) + 1, 
                "candidato": row["candidato"],
                "usuario": row["usuario"],
                "fecha": row["fecha"],
                "texto": row["texto"],
                "comentarios": []
            }
            posts_seen[post_id] = post_data
        
        # 3.2. Obtener la referencia a la publicación actual
        post_data = posts_seen[post_id]
        
        # 3.3. Si hay un comentario, agregarlo al campo de comentarios
        # NOTA: Tu código original usaba 'texto_comentario', que puede contener texto sucio/bruto.
        # Si tienes la columna limpia, es mejor usarla aquí (e.g., row["texto_comentario_limpio"]).
        if pd.notna(row["texto_comentario"]):
            comment_id = len(post_data["comentarios"]) + 1
            post_data["comentarios"].append({
                "id_comentario": comment_id,
                "texto_comentario": row["texto_comentario"]
            })
            
    # 4. Agregar todas las publicaciones al nuevo archivo
    new_data: List[Dict[str, Any]] = list(posts_seen.values())

    # 5. Guardar el nuevo archivo JSON con la estructura modificada
    with open(ruta_json_salida, 'w', encoding='utf-8') as new_file:
        json.dump(new_data, new_file, indent=4, ensure_ascii=False)

    print(f"\nArchivo reestructurado guardado como '{ruta_json_salida}'")
    print(f"Total de publicaciones (posts) únicas reestructuradas: {len(new_data)}")