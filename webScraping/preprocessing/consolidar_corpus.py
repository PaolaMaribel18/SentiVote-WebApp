import pandas as pd
import os

def consolidar_corpus_csvs(carpeta_entrada: str, archivo_salida: str) -> None:
    """
    Carga todos los archivos CSV de una carpeta, los concatena y guarda
    el resultado en un único archivo CSV consolidado.

    Args:
        carpeta_entrada (str): Ruta a la carpeta que contiene los archivos CSV
                               a consolidar (e.g., "../datosLimpios").
        archivo_salida (str): Ruta completa del archivo donde se guardará el
                              corpus final (e.g., "../datosLimpios/corpus_completo.csv").
    """
    
    # Extraer la ruta del directorio del archivo de salida
    carpeta_salida = os.path.dirname(archivo_salida)
    
    # Si la carpeta de salida no es vacía (es decir, no es solo el nombre del archivo)
    if carpeta_salida and not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
        print(f"Creada carpeta de salida: {carpeta_salida}")
    
    # 1. Inicializar la lista de DataFrames
    dataframes = []
    archivos_procesados = 0

    # 2. Recorrer archivos .csv en la carpeta de entrada
    print(f"Iniciando consolidación de CSVs en: {carpeta_entrada}")
    
    # Manejar el caso donde la carpeta de entrada no existe
    if not os.path.exists(carpeta_entrada):
        print(f"Error: La carpeta de entrada no existe: {carpeta_entrada}")
        return
        
    for filename in os.listdir(carpeta_entrada):
        if filename.endswith(".csv"):
            filepath = os.path.join(carpeta_entrada, filename)
            
            # Omitir el archivo de salida si ya existe y está en la misma carpeta
            if filepath == archivo_salida:
                print(f"Omitiendo el archivo de salida: {filename}")
                continue
            
            try:
                print(f"Cargando: {filename}")
                df = pd.read_csv(filepath)
                dataframes.append(df)
                archivos_procesados += 1
            except Exception as e:
                print(f"Error al leer {filename}. Ignorando. Error: {e}")

    # 3. Verificar si se cargaron archivos
    if not dataframes:
        print("No se encontraron archivos CSV para consolidar.")
        return

    # 4. Unir todos los DataFrames
    print(f"\nCargados {archivos_procesados} archivos. Concatenando...")
    corpus_df = pd.concat(dataframes, ignore_index=True)

    # 5. Guardar corpus consolidado
    corpus_df.to_csv(archivo_salida, index=False)
    
    print(f"Total de filas en el corpus: {len(corpus_df)}")
    print(f"Corpus guardado en: {archivo_salida}")