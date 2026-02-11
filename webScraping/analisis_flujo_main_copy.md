# Documentación del Flujo de Trabajo: main copy.ipynb

Este documento describe el proceso secuencial ejecutado en `main.ipynb`. A diferencia del script principal original, esta versión incluye pasos adicionales para la unificación con datos históricos y la persistencia en base de datos NoSQL (MongoDB).

## Resumen del Proceso

Este flujo de trabajo orquesta la extracción, limpieza, unificación y almacenamiento de datos sociopolíticos. Introduce una etapa crítica de **integración de datos** donde el corpus recién extraído se fusiona con un corpus "histórico" previamente existente, antes de ser transformado y cargado en la base de datos.

### Fases del Pipeline

1.  **Inicialización y Autenticación**: Configuración del driver y login en Twitter (X).
2.  **Minería de Datos (Scraping)**:
    *   Extracción de enlaces de tweets de candidatos.
    *   Extracción de metadatos de los tweets.
    *   Extracción de enlaces de comentarios.
    *   Extracción del contenido textual de los comentarios.
3.  **Procesamiento y Limpieza**:
    *   Consolidación de los CSVs extraídos en esta ejecución.
    *   Limpieza y normalización del texto.
4.  **Unificación (Etapa Nueva)**: Fusión del corpus actual limpio con el corpus histórico procesado anteriormente para mantener un dataset acumulativo.
5.  **Transformación y Carga (ETL)**:
    *   Conversión del corpus unificado a formato JSON estructurado.
    *   Carga automática de datos hacia **MongoDB**.

## Diagrama de Secuencia

El siguiente diagrama detalla la integración de los nuevos módulos de unificación (`Preprocessing`) y almacenamiento (`Storage`).

```mermaid
sequenceDiagram
    autonumber
    participant NB as Sistema Web Scraping
    participant Driver as Selenium Driver
    participant Scraper as Módulos Scraping
    participant Preproc as Módulos Preprocessing
    participant FS as Sistema de Archivos
    participant DB as MongoDB

    Note over NB, Driver: Fase 1: Configuración y Acceso
    NB->>Driver: get_driver()
    Driver-->>NB: Instancia activa
    NB->>Scraper: login_twitter()

    Note over NB, FS: Fase 2: Minería de Datos (Scraping)
    
    %% Paso 1: Enlaces
    NB->>Scraper: guardar_enlaces_candidatos()
    Scraper->>FS: Guardar *_enlaces_tweets.csv

    %% Paso 2: Info Tweets
    NB->>Scraper: extraer_informacion_tweets()
    Scraper->>FS: Guardar informacion_publicaciones.csv

    %% Paso 3: Enlaces Comentarios
    NB->>Scraper: extraer_enlaces_comentarios_csvs()
    Scraper->>FS: Guardar enlaces_comentarios.csv

    %% Paso 4: Texto Comentarios
    NB->>Scraper: minar_texto_comentarios()
    Scraper->>FS: Guardar datos_completos_publicacion.csv

    NB->>Driver: close_driver()

    Note over NB, FS: Fase 3: Procesamiento

    NB->>Preproc: consolidar_corpus_csvs()
    Preproc->>FS: Generar corpus_comentarios_tweets.csv (Data Nueva)

    NB->>Preproc: limpiar_y_normalizar_corpus()
    Preproc->>FS: Generar corpus_preprocesado_corregido.csv (Data Nueva Limpia)

    Note over NB, FS: Fase 4: Unificación de Corpus

    NB->>Preproc: unificar_y_limpiar(original, nuevo, salida)
    FS->>Preproc: Leer corpus_preprocesado.csv (Histórico)
    FS->>Preproc: Leer corpus_preprocesado_corregido.csv (Nuevo)
    Preproc->>Preproc: Fusión y Eliminación de Duplicados
    Preproc->>FS: Guardar corpus_preprocesado_unificado.csv

    Note over NB, DB: Fase 5: Almacenamiento

    NB->>Preproc: reestructurar_csv_a_json_simple()
    FS->>Preproc: Leer Unificado CSV
    Preproc->>FS: Generar corpus_completo.json

    NB->>NB: Cargar Módulo MongoDB Loader
    NB->>DB: cargar_json_a_mongo(ruta_json)
    FS->>DB: Leer JSON y enviar documentos
```

## Estructura de Salida de Datos

El flujo actualiza la estructura de datos en `datasets/processed`:

| Archivo | Origen | Descripción |
|---------|--------|-------------|
| `corpus_preprocesado_corregido.csv` | Limpieza | Datos limpios **solo de la ejecución actual**. |
| `corpus_preprocesado.csv` | Entrada | Datos históricos (Input para la unificación). |
| `corpus_preprocesado_unificado.csv` | Unificación | **Dataset Maestro**: Combinación de histórico + nuevo. |
| `corpus_completo.json` | Transformación | Versión JSON del dataset maestro lista para la BD. |
