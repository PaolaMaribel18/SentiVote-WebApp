import os
import json
import re
import io
import base64

# Librerías de Machine Learning / NLP
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification 
import nltk
from nltk.corpus import stopwords

# Librerías de la Web (Flask)
from flask import Flask, request, jsonify # Eliminamos 'send_file' si no se usa
from flask_cors import CORS
from dotenv import load_dotenv

# Librerías de Visualización
import matplotlib
import matplotlib.pyplot as plt
from wordcloud import WordCloud
matplotlib.use('Agg') # Para evitar problemas con GUI

# Librerías de LLM
import google.generativeai as genai 

from datetime import datetime, timezone 
# --------------------------------------------------------------------------------


# Configurar variables de entorno
load_dotenv()

# ---------------------------------------------------------------------------------------------------
# Configurar Gemini 2.5 Flash de Google Generative AI API 
# ---------------------------------------------------------------------------------------------------
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model_gemini = genai.GenerativeModel("gemini-2.5-flash")
else:
    print("⚠️ ADVERTENCIA: No se encontró GEMINI_API_KEY en .env")
    model_gemini = None

# ---------------------------------------------------------------------------------------------------
# Configurar Flask y CORS
# ---------------------------------------------------------------------------------------------------
app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:3000"])

# ---------------------------------------------------------------------------------------------------
# Cargar modelo de análisis de sentimiento BETO desde Hugging Face
# ---------------------------------------------------------------------------------------------------
# try:
#     modelo = pipeline("sentiment-analysis", model="finiteautomata/beto-sentiment-analysis")
#     print("Modelo BETO cargado exitosamente")
# except Exception as e:
#     print(f"Error cargando modelo BETO: {e}")
#     print("Usando modelo alternativo...")
#     modelo = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
    
    
# ---------------------------------------------------------------------------------------------------
# Cargar modelo de análisis de sentimiento fine-tuned localmente
# ---------------------------------------------------------------------------------------------------

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "fineTuning", "modelo_final")

try:
    print(f"Intentando cargar modelo fine-tuned desde: {MODEL_DIR}")
    modelo = pipeline(
        "sentiment-analysis", 
        model=MODEL_DIR, 
        device=-1, # -1 para usar CPU, 0 para usar GPU 
        truncation=True,
        max_length=128 #Mejorar modelo para que acepte textos más largos
    )
    print("Modelo fine-tuned 'sentimiento-politica' cargado exitosamente.")

except Exception as e:
    print(f"ERROR: No se pudo cargar el modelo fine-tuned local: {e}")
    # Fallback al modelo de Hugging Face por si falla la carga local
    print("Usando modelo pre-entrenado alternativo como fallback...")
    try:
        modelo = pipeline("sentiment-analysis", model="finiteautomata/beto-sentiment-analysis")
        print("Modelo BETO de Hugging Face cargado como fallback.")
    except Exception as e_fallback:
        print(f"ERROR: No se pudo cargar ningún modelo. {e_fallback}")
        modelo = None # Si todo falla, no hay modelo.
# ---------------------------------------------------------------------------------------------------
    
    

# Diccionarios
diccionario_positivo = [
    # Términos generales de alta carga
    "bueno", "excelente", "genial", "amor", "éxito", "feliz", "maravilloso", 
    "fortaleza", "esperanza", "progreso", "desarrollo", "bienestar", "paz", "justicia",
    "honesto", "transparente", "eficiente", "competente", "liderazgo", "experiencia", "ganar", "vamos",
    
    # Términos especializados en política y agenda ecuatoriana
    "seguridad", "protección", "firmeza", "orden", "estabilidad", "futuro", "empleo", 
    "oportunidad", "inversión", "crecimiento", "salud", "educación", "libertad", 
    "consenso", "patria", "unión", "solución", "seriedad", "propuestas", "calma", 
    "mano dura"
]

diccionario_negativo = [
    # Términos generales de alta carga
    "malo", "horrible", "negativo", "terrible", "odio", "fracaso", "débil", "miseria", 
    "desastre", "corrupción", "mentira", "robo", "incompetente", "ineficiente", "crisis",
    "problema", "conflicto", "violencia", "inseguridad", "pobreza", "desempleo", "ladron", "narco",
    
    # Términos especializados en política y agenda ecuatoriana
    "sicariato", "extorsión", "impunidad", "bandas", "crimen", "cárcel", "caos",
    "deuda", "impuestos", "alza", "carestía", "deficit", "quiebra", "fraude", 
    "populismo", "traidor", "incumplimiento", "montaje", "juicio", "asamblea",
    "engaño", "burla", "desconfianza", "cínico", "cúpula"
]

NEGATORS = {
    "no", "ni", "nunca", "jamás", "tampoco", "sin", "excepto", "salvo", "ni siquiera"
}

# --------------------------------------------------------------------------------------
# Carga de Stop Words desde NLTK + Términos Específicos 
# --------------------------------------------------------------------------------------

# 1. Cargar las stop words estándar en español de NLTK
try:
    NLTK_STOP_WORDS = set(stopwords.words('spanish'))
except LookupError:
    # Esto ocurre si el paquete 'stopwords' no se descargó (Paso 1.B)
    print("⚠️ ADVERTENCIA: NLTK 'stopwords' no está descargado. Ejecute 'nltk.download(\\'stopwords\\')'")
    NLTK_STOP_WORDS = set()

# 2. Palabras específicas de tu dominio (redes sociales y URLs)
CUSTOM_STOP_WORDS = {
    'rt', 'via', 'https', 'http', 'www', 'com', 'co', 'ec', 'org'
    # Las palabras del diccionario manual que quitaste están ahora en NLTK
}

# 3. Combinar y usar el nuevo conjunto robusto
STOP_WORDS_ES = NLTK_STOP_WORDS.union(CUSTOM_STOP_WORDS)
print(f"INFO: Lista de Stop Words cargada con {len(STOP_WORDS_ES)} términos (NLTK + Personalizados).")

alpha = 0.4
# --------------------------------------------------------------------------------------
# Funciones auxiliares
# --------------------------------------------------------------------------------------
# Función para limpiar texto para wordcloud y análisis 
def limpiar_texto_para_wordcloud(texto):
    """Limpia el texto para el wordcloud"""
    if not texto: return ""
    texto = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', texto)
    texto = re.sub(r'@\w+', '', texto)
    texto = re.sub(r'#(\w+)', r'\1', texto)
    texto = re.sub(r'[^\w\s]', ' ', texto)
    texto = re.sub(r'\b\d+\b', '', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto.lower()

# Función para generar wordcloud y devolver imagen en base64 y palabras frecuentes 
def generar_wordcloud(textos):
    """Genera un wordcloud a partir de una lista de textos"""
    try:
        texto_combinado = ' '.join([limpiar_texto_para_wordcloud(texto) for texto in textos if texto.strip()])
        
        # Validar si hay suficientes palabras (al menos 1 palabra válida)
        if not texto_combinado.strip() or len(texto_combinado) < 3:
            return None, {} 
        
        wordcloud = WordCloud(
            width=800, height=400,
            background_color='white',
            max_words=50,
            stopwords=STOP_WORDS_ES,
            min_font_size=10, max_font_size=80,
            colormap='viridis',
            relative_scaling=0.5,
            random_state=42
        ).generate(texto_combinado)
        
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150, facecolor='white', edgecolor='none')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        plt.close()
        
        return img_base64, wordcloud.words_
        
    except Exception as e:
        print(f"Error generando wordcloud: {e}")
        return None, {}

def generar_wordclouds_por_sentimiento(publicaciones):
    textos_por_sentimiento = {
        "POS": [],
        "NEG": [],
        "NEU": []
    }

    # --- CORRECCIÓN DE LÓGICA DE AGRUPACIÓN ---
    for pub in publicaciones:
        # 1. El texto del POST va a la categoría del POST
        sentimiento_post = pub.get("sentiment", "NEU") # Usamos "sentiment" que es la clave que definimos en procesar
        if sentimiento_post in textos_por_sentimiento:
            textos_por_sentimiento[sentimiento_post].append(pub.get("text", "")) 
        
        # 2. El texto del COMENTARIO va a la categoría del COMENTARIO (Independiente del post)
        for comentario in pub.get("comentarios", []):
            sentimiento_com = comentario.get("sentimiento_comentario", "NEU")
            if sentimiento_com in textos_por_sentimiento:
                textos_por_sentimiento[sentimiento_com].append(comentario["texto_comentario"])
            
    # DEBUG: Ver distribución real de palabras
    print("--- Distribución de textos para Nubes de Palabras ---")
    for key, textos in textos_por_sentimiento.items():
        print(f"[{key}]: {len(textos)} textos acumulados.")

    wordclouds_sentimiento = {}
    for sentimiento, textos in textos_por_sentimiento.items():
        img_base64, palabras_frecuentes = generar_wordcloud(textos)
        
        wordclouds_sentimiento[sentimiento] = {
            "imagen": img_base64, # Puede ser None si no hay suficientes palabras
            "palabras": palabras_frecuentes if img_base64 else {}
        }

    return wordclouds_sentimiento

# Cargar corpus desde archivo JSON 
def cargar_corpus():
    ruta = os.path.join(os.path.dirname(__file__), "data/corpus.json") 
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("ERROR: Archivo corpus.json no encontrado")
        return []

# --------------------------------------------------------------------------------------
# FUNCIÓN DE ANÁLISIS DE DICCIONARIO MEJORADA CON MANEJO DE NEGACIÓN
# --------------------------------------------------------------------------------------
def analizar_texto_con_diccionario(texto, sentimiento_modelo, confianza_modelo):
    """
    Analiza el texto buscando palabras clave para reforzar la confianza del modelo,
    con manejo básico de negación.
    """
    texto_lower = texto.lower()
    
    # 1. Limpieza y Tokenización del texto de entrada
    # Limpiamos solo para obtener palabras, pero mantenemos el orden para la negación.
    words = re.findall(r'\b\w+\b', texto_lower)
    
    palabras_positivas_contadas = 0
    palabras_negativas_contadas = 0
    
    for i, word in enumerate(words):
        # 2. Revisar si la palabra está negada
        # Buscamos si la palabra anterior (índice i-1) es un negador.
        is_negated = False
        if i > 0 and words[i-1] in NEGATORS:
            is_negated = True
        
        # 3. Aplicar la lógica de sentimiento
        if word in diccionario_positivo:
            if not is_negated:
                palabras_positivas_contadas += 1
            # Si se niega ("no bueno"), no cuenta como positivo, sino como neutral.
            
        elif word in diccionario_negativo:
            if not is_negated:
                palabras_negativas_contadas += 1
            # Si se niega ("no corrupción"), no cuenta como negativo, sino como neutral.
            
    # 4. Decisión de Refuerzo
    if palabras_positivas_contadas > palabras_negativas_contadas and palabras_positivas_contadas > 0:
        # Si el modelo base predijo algo negativo o neutro, le damos un empujón positivo.
        return "POS", min(confianza_modelo + 0.15, 1.0) 
        
    elif palabras_negativas_contadas > palabras_positivas_contadas and palabras_negativas_contadas > 0:
        # Si el modelo base predijo algo positivo o neutro, le damos un empujón negativo.
        return "NEG", min(confianza_modelo + 0.15, 1.0)
        
    else:
        # Si no hay palabras clave o si se anularon por negación, confiamos en el modelo de Deep Learning.
        return sentimiento_modelo, confianza_modelo


def parse_date(date_str, is_end=False):
    """
    Convierte una cadena de fecha (YYYY-MM-DD) en un objeto datetime aware (UTC), 
    ajustando a los límites del día.
    """
    if not date_str:
        return None
    try:
        # 1. Parsear la fecha simple YYYY-MM-DD
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        
        # 2. Asignar explícitamente la zona horaria UTC (CRUCIAL para 'offset-aware')
        dt = dt.replace(tzinfo=timezone.utc) 
        
    except ValueError:
        print(f"Advertencia: Formato de fecha de filtro inesperado para {date_str}")
        return None
    
    # 3. Ajustar a los límites del día (00:00:00 o 23:59:59)
    if not is_end:
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        # Nota: Usamos 23:59:59.999999 para incluir todo el día
        return dt.replace(hour=23, minute=59, second=59, microsecond=999999)
    
def obtener_rango_fechas(corpus):
    """Calcula la fecha mínima y máxima del corpus."""
    if not corpus:
        return None, None
    
    fechas = []
    
    for post in corpus:
        date_str = post.get("fecha")
        if date_str:
            try:
                # Usamos el mismo método robusto que en /analizar
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                fechas.append(dt)
            except ValueError:
                continue # Ignoramos fechas inválidas
    
    if not fechas:
        return None, None
        
    # Encontramos la fecha más antigua y la más reciente
    min_date = min(fechas)
    max_date = max(fechas)
    
    # Formateamos las fechas al formato simple YYYY-MM-DD para el frontend
    # Nota: Usamos el formato ISO completo si es necesario, pero YYYY-MM-DD es suficiente para el selector
    return min_date.strftime("%Y-%m-%d"), max_date.strftime("%Y-%m-%d")

# --------------------------------------------------------------------------------------
# Rutas de la API
# --------------------------------------------------------------------------------------
# Ruta raíz 
@app.route("/", methods=["GET"])
def home():
    return jsonify({"mensaje": "API Activa", "endpoints": ["/analizar", "/conclusiones"]})

# Ruta de salud
@app.route("/salud", methods=["GET"])
def salud():
    corpus = cargar_corpus()
    min_date_str, max_date_str = obtener_rango_fechas(corpus) # <--- Llamada a la nueva función
    
    return jsonify({
        "estado": "activo",
        "publicaciones": len(corpus),
        "modelos": "Gemini 2.5 Flash + Robertuito Electoral FT",
        "minDate": min_date_str, # <--- ¡Nuevo campo!
        "maxDate": max_date_str  # <--- ¡Nuevo campo!
    })
    
    
# Ruta para análisis de sentimiento 
@app.route("/analizar", methods=["POST"])
def analizar():
    # Procesar solicitud de análisis de sentimiento 
    try:
        datos = request.json
        query = datos.get("query", "").strip()
        fecha_desde_str = datos.get("dateFrom")
        fecha_hasta_str = datos.get("dateTo")
        
        if not query:
            return jsonify({"error": "Query requerida"}), 400
        
        print(f"Búsqueda recibida: '{query}'")
        corpus = cargar_corpus()
        
        start_date = parse_date(fecha_desde_str, is_end=False)
        end_date = parse_date(fecha_hasta_str, is_end=True)
        
        if not query:
            return jsonify({"error": "Query requerida"}), 400
        
        print(f"Búsqueda recibida: '{query}'")
        corpus = cargar_corpus()
        
        # 1. PARSEO DE FECHAS DE ENTRADA
        start_date = parse_date(fecha_desde_str, is_end=False)
        end_date = parse_date(fecha_hasta_str, is_end=True)
        
        # 2. FILTRADO INICIAL POR QUERY (Mantener la funcionalidad actual)
        publicaciones_filtradas_por_query = [
            p for p in corpus 
            if query.lower() in p.get("candidato", "").replace("_", " ").lower() or 
            query.lower() in p.get("texto", "").lower()
        ]
        
        # 3. FILTRADO POR FECHA (Lógica Completada)
        publicaciones_filtradas = []
        
        if start_date or end_date:
            print(f"Aplicando filtro de fecha: Desde {start_date} hasta {end_date}")
            for p in publicaciones_filtradas_por_query:
                post_date_str = p.get("fecha") # Asume el formato ISO del corpus (ej. 2025-01-05T17:57:48.000Z)
                if not post_date_str:
                    continue
                
                # CORRECCIÓN CLAVE: Asegurar que la fecha del corpus sea consciente de la zona horaria.
                try:
                    # fromisoformat es la mejor opción para formatos ISO con Z (lo convierte a +00:00)
                    post_date = datetime.fromisoformat(post_date_str.replace('Z', '+00:00'))
                    
                    # SI el corpus no tiene Z o +00:00, hay que forzarlo, pero fromisoformat generalmente lo maneja.
                    # Si el error persiste, deberíamos forzar: post_date = post_date.replace(tzinfo=timezone.utc)
                    
                except ValueError:
                    # Si el formato no es válido, lo ignoramos.
                    continue 

                is_within_start = (not start_date) or (post_date >= start_date)
                is_within_end = (not end_date) or (post_date <= end_date)
                
                if is_within_start and is_within_end:
                    publicaciones_filtradas.append(p)
        else:
            # Si no hay filtros de fecha, se mantienen solo los filtrados por query
            publicaciones_filtradas = publicaciones_filtradas_por_query

        print(f"Publicaciones encontradas: {len(publicaciones_filtradas)}")
        
        if not publicaciones_filtradas:
            return jsonify({"mensaje": "No se encontraron resultados", "publicaciones": []}), 200

        publicaciones_procesadas = []
        todos_los_textos = [] 
        # Procesar cada publicación 
        
        for post in publicaciones_filtradas:
            texto_publicacion = post.get("texto", "")
            if not texto_publicacion: continue
            
            todos_los_textos.append(texto_publicacion)
            
            # 1. Análisis del Post
            try:
                res_post = modelo([texto_publicacion])[0]
                
                # Almacenar resultado PURO del modelo FT (antes del diccionario)
                raw_post_sentiment = res_post["label"].upper().replace("NEGATIVE", "NEG").replace("POSITIVE", "POS").replace("NEUTRAL", "NEU")
                raw_post_confidence = res_post["score"]
                
                # Aplicar Normalización y Refuerzo del Diccionario
                normalized_label = raw_post_sentiment
                sent_post, conf_post = analizar_texto_con_diccionario(
                    texto_publicacion, normalized_label, raw_post_confidence
                )
            except:
                raw_post_sentiment = "NEU (Error)"
                raw_post_confidence = 0.0
                sent_post, conf_post = "NEU", 0.5
            
            # -------------------------------------------------------------
            # >>> IMPRESIÓN DE COMPARACIÓN DEL POST <<<
            # -------------------------------------------------------------
            # print(f"\n--- POST: {post.get('id_post', 'N/A')} ---")
            # print(f"Texto: '{texto_publicacion[:100]}...'")
            # print(f"  [1] Modelo FT Puro: {raw_post_sentiment} (Confianza: {raw_post_confidence:.3f})")
            # print(f"  [2] Híbrido Reforzado: {sent_post} (Confianza: {conf_post:.3f})")
            
            # Solo muestra el mensaje si hubo un cambio significativo
            # if raw_post_sentiment != sent_post or abs(raw_post_confidence - conf_post) > 0.01:
            #      print("  >>> POST REFORZADO/AJUSTADO por Diccionario/Negación <<<")
            # -------------------------------------------------------------


            # 2. Análisis de Comentarios
            comentarios_procesados = []
            sentimientos_comments = []
            confianzas_comments = []
            
            # >>> IMPRESIÓN DE COMENTARIOS (Opcional, activa solo para depuración profunda) <<<
            # print(f"\n   --- Comentarios del Post {post.get('id_post')} ---") 

            for com in post.get("comentarios", []):
                txt_com = com.get("texto_comentario", "")
                if not txt_com: continue
                
                todos_los_textos.append(txt_com)
                
                try:
                    res_com = modelo([txt_com])[0]
                    
                    # Resultado PURO del modelo FT
                    raw_com_sentiment = res_com["label"].upper().replace("NEGATIVE", "NEG").replace("POSITIVE", "POS").replace("NEUTRAL", "NEU")
                    raw_com_confidence = res_com["score"]
                    
                    # Aplicar Normalización y Refuerzo del Diccionario
                    normalized_label_com = raw_com_sentiment
                    sent_com, conf_com = analizar_texto_con_diccionario(
                        txt_com, normalized_label_com, raw_com_confidence
                    )
                except:
                    raw_com_sentiment = "NEU (Error)"
                    raw_com_confidence = 0.0
                    sent_com, conf_com = "NEU", 0.5
                
                # >>> IMPRESIÓN DE COMPARACIÓN DEL COMENTARIO (Descomentar para ver) <<<
                # if raw_com_sentiment != sent_com or abs(raw_com_confidence - conf_com) > 0.01:
                #     print(f"     [!] Comentario ajustado: '{txt_com[:50]}...'")
                #     print(f"         Puro: {raw_com_sentiment} ({raw_com_confidence:.3f}) -> Híbrido: {sent_com} ({conf_com:.3f})")
                
                comentarios_procesados.append({
                    "id_comentario": com.get("id_comentario"),
                    "texto_comentario": txt_com,
                    "sentimiento_comentario": sent_com,
                    "confianza_comentario": round(conf_com, 3)
                })
                sentimientos_comments.append(sent_com)
                confianzas_comments.append(conf_com)

            # 3. Lógica de Sentimiento Final (Ponderado)
            if sentimientos_comments:
                avg_sent_comments = max(set(sentimientos_comments), key=sentimientos_comments.count)
                avg_conf_comments = sum(confianzas_comments) / len(confianzas_comments)
            else:
                avg_sent_comments = "NEU"
                avg_conf_comments = 0.5

            # Si el post es NEG o los comentarios son mayormente NEG -> Final NEG
            if sent_post == "NEG" or avg_sent_comments == "NEG":
                sent_final = "NEG"
            elif sent_post == "POS" and avg_sent_comments == "POS":
                sent_final = "POS"
            else:
                sent_final = "NEU"
            
            conf_final = alpha * conf_post + (1 - alpha) * avg_conf_comments
            
            fecha = post.get("fecha", "")
            
            usuario = post.get("usuario", "Anónimo")
            
            publicaciones_procesadas.append({
                "id_post": str(post.get("id_post")), # Aseguramos que coincida con la interface
                "texto": texto_publicacion, # CAMBIO: "text" -> "texto"
                "usuario": usuario, # CAMBIO: Enviamos el usuario real (@JacoboG_Ecu)
                "candidato": post.get("candidato"), 
                "fecha": post.get("fecha"),
                
                "sentiment": sent_final,
                "confidence": round(conf_final, 3),
                "platform": "twitter",
                "candidato": post.get("candidato"),
                "comentarios": comentarios_procesados,
                # Datos extra para el frontend si los necesita
                "sentimiento_publicacion": sent_post,
                "sentimiento_comentarios": avg_sent_comments,
                "sentimiento_final": sent_final,
                "confianza_final": round(conf_final, 3),
                "comentarios": comentarios_procesados
            })

        print("\nGenerando wordclouds...")
        # Wordcloud General
        wc_general, _ = generar_wordcloud(todos_los_textos)
        
        # Wordclouds por sentimiento (POS, NEG, NEU)
        wc_sentimientos = generar_wordclouds_por_sentimiento(publicaciones_procesadas)

        return jsonify({
            "publicaciones": publicaciones_procesadas,
            "wordcloud": {
                "general": wc_general,
                "por_sentimiento": wc_sentimientos
            },
            "total_textos_analizados": len(todos_los_textos)
        })

    except Exception as e:
        print(f"ERROR CRITICO EN /analizar: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Ruta para generar conclusiones 
@app.route("/conclusiones", methods=["POST"])
def generar_conclusiones():
    try:
        datos = request.json
        query = datos.get("query", "Consulta")
        wordclouds = datos.get("wordclouds", {})
        
        # Construir resumen de palabras
        top_pos = ", ".join(list(wordclouds.get("POS", {}).keys())[:5])
        top_neg = ", ".join(list(wordclouds.get("NEG", {}).keys())[:5])
        
        prompt = f"""
        Analiza brevemente la reputación digital de "{query}" basándote en estas palabras clave detectadas:
        - Positivas: {top_pos if top_pos else "No detectadas"}
        - Negativas: {top_neg if top_neg else "No detectadas"}
        
        Responde en 2 frases objetivas como analista de datos.
        """
        
        try:
            if model_gemini:
                resp = model_gemini.generate_content(prompt)
                return jsonify({"conclusion": resp.text.strip()})
            else:
                raise Exception("Modelo no configurado")
        except Exception as ia_error:
            print(f"Error IA: {ia_error}")
            return jsonify({
                "conclusion": "El análisis muestra tendencias mixtas. Se recomienda revisar los comentarios destacados para mayor contexto.",
                "nota": "Generado localmente (IA no disponible)"
            })

    except Exception as e:
        return jsonify({"error": "Error generando conclusión"}), 500


if __name__ == "__main__":
    print("Iniciando servidor Flask...")
    
    print("Verificando modelo de ML...")
    
    # Verificar que el modelo funciona
    try:
        test_result = modelo(["Este es un texto de prueba"])
        print("Modelo funcionando correctamente")
    except Exception as e:
        print(f"Error con el modelo: {e}")
    
    # Verificar que el corpus existe
    corpus_test = cargar_corpus()
    if corpus_test:
        print(f"Corpus cargado: {len(corpus_test)} publicaciones")
    else:
        print("ADVERTENCIA: No se pudo cargar el corpus")
    
    #verificar rango de fechas
    min_date_str, max_date_str = obtener_rango_fechas(corpus_test)
    print(f"Rango de fechas del corpus: {min_date_str} a {max_date_str}")
    

    
    app.run(debug=True, host='0.0.0.0', port=5000)