from pymongo import MongoClient
import json
import os
from dotenv import load_dotenv

def cargar_json_a_mongo(ruta_json, collection_name=None):
    """
    Carga los datos de un archivo JSON a una colección de MongoDB.
    Usa la variable de entorno MONGO_URI para la conexión.
    
    Args:
        ruta_json (str): Ruta al archivo JSON (ej: 'datasets/processed/corpus_completo.json')
        collection_name (str, optional): Nombre de la colección. Si es None, se lee de MONGO_COLLECTION_NAME.
    """
    # 1. Cargar variables de entorno
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB_NAME", "tesis_analisis_sentimiento")
    
    # Obtener nombre de colección desde env si no se pasa explícitamente
    if collection_name is None:
        collection_name = os.getenv("MONGO_COLLECTION_NAME", "corpus_politico")
    
    if not mongo_uri:
        print("- Error: No se encontró la variable MONGO_URI en el archivo .env")
        return

    try:
        # 2. Conectar a MongoDB
        client = MongoClient(mongo_uri)
        db = client[db_name]
        collection = db[collection_name]
        
        print(f"- Conectado a MongoDB: {db_name}.{collection_name}")

        # 3. Leer archivo JSON
        if not os.path.exists(ruta_json):
            print(f"- Error: El archivo {ruta_json} no existe.")
            return

        with open(ruta_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print("- Advertencia: El JSON no es una lista de objetos. Se intentará insertar como un solo documento.")
            data = [data]

        total_docs = len(data)
        print(f"- Archivo leído. Preparando para procesar {total_docs} documentos...")

        # 4. Insertar/Actualizar documentos (Upsert basado en id_post)
        operaciones = 0
        modificados = 0
        nuevos = 0

        for doc in data:
            # Asumimos que 'id_post' es el identificador único del post
            # Si no existe, usamos una combinación de candidato+usuario+fecha o generamos un hash
            filtro = {}
            if "id_post" in doc:
                filtro = {"id_post": doc["id_post"]}
            else:
                # Fallback simple si no hay id_post (aunque el script de transformación lo genera)
                filtro = {"candidato": doc.get("candidato"), "texto": doc.get("texto")}

            # Upsert: Actualiza si existe, Inserta si no
            resultado = collection.update_one(filtro, {"$set": doc}, upsert=True)
            
            if resultado.upserted_id:
                nuevos += 1
            elif resultado.modified_count > 0:
                modificados += 1
            
            operaciones += 1
            if operaciones % 100 == 0:
                print(f"   - Procesados {operaciones}/{total_docs}...")

        print(f"\nProceso completado en MongoDB.")
        print(f" - Documentos nuevos: {nuevos}")
        print(f" - Documentos actualizados: {modificados}")
        print(f" - Total en colección: {collection.count_documents({})}")

        client.close()

    except Exception as e:
        print(f"Error crítico en la carga a MongoDB: {e}")
