from flask import Flask, request, jsonify, send_file
from transformers import pipeline
from flask_cors import CORS
import os
import json
from datetime import datetime
import io
import base64
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Para evitar problemas con GUI
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# --- CORRECCIÓN 1: Nombre del modelo estable ---
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model_gemini = genai.GenerativeModel("gemini-2.5-flash")
else:
    print("⚠️ ADVERTENCIA: No se encontró GEMINI_API_KEY en .env")
    model_gemini = None

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:3000"])

# Cargar modelo de análisis de sentimiento
try:
    modelo = pipeline("sentiment-analysis", model="finiteautomata/beto-sentiment-analysis")
    print("Modelo BETO cargado exitosamente")
except Exception as e:
    print(f"Error cargando modelo BETO: {e}")
    print("Usando modelo alternativo...")
    modelo = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")

# Diccionarios
diccionario_positivo = [
    "bueno", "excelente", "positivo", "genial", "amor", "éxito", "feliz", "maravilloso", 
    "fortaleza", "esperanza", "progreso", "desarrollo", "bienestar", "paz", "justicia",
    "honesto", "transparente", "eficiente", "competente", "liderazgo", "experiencia", "ganar", "vamos"
]

diccionario_negativo = [
    "malo", "horrible", "negativo", "terrible", "odio", "fracaso", "débil", "miseria", 
    "desastre", "corrupción", "mentira", "robo", "incompetente", "ineficiente", "crisis",
    "problema", "conflicto", "violencia", "inseguridad", "pobreza", "desempleo", "ladron", "narco"
]

STOP_WORDS_ES = {
    'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 
    'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'los', 'las', 'una', 'pero', 
    'sus', 'has', 'han', 'muy', 'más', 'yo', 'me', 'mi', 'tu', 'él', 'ella', 'este', 
    'esta', 'si', 'ya', 'así', 'como', 'hasta', 'tiene', 'será', 'fue', 'ser', 'está', 
    'van', 'son', 'hacer', 'ver', 'ir', 'hay', 'bien', 'ahora', 'donde', 'cuando', 
    'después', 'antes', 'tanto', 'todos', 'todo', 'cada', 'puede', 'debe', 'sobre', 
    'sin', 'desde', 'hacia', 'entre', 'porque', 'aunque', 'mientras', 'durante', 
    'según', 'contra', 'tras', 'mediante', 'ante', 'bajo', 'qué', 'cómo', 'cuál', 
    'dónde', 'cuándo', 'por', 'solo', 'también', 'vez', 'hacer', 'ahí', 'estar', 
    'tener', 'poder', 'decir', 'ver', 'dar', 'saber', 'querer', 'llegar', 'pasar', 
    'seguir', 'parecer', 'encontrar', 'llamar', 'venir', 'pensar', 'salir', 'volver', 
    'tomar', 'conocer', 'vivir', 'sentir', 'tratar', 'mirar', 'contar', 'empezar', 
    'esperar', 'buscar', 'existir', 'entrar', 'trabajar', 'escribir', 'producir', 
    'ocurrir', 'recibir', 'cambiar', 'resultar', 'situar', 'reconocer', 'estudiar', 
    'obtener', 'nacer', 'permanecer', 'escuchar', 'realizar', 'suponer', 'disponer', 
    'poner', 'hablar', 'considerar', 'explicar', 'dedicar', 'construir', 'ganar', 
    'brindar', 'ofrecer', 'conseguir', 'mantener', 'presentar', 'crear', 'abrir', 
    'recordar', 'utilizar', 'cerrar', 'mostrar', 'incluir', 'continuar', 'desenvolver',
    'rt', 'via', 'https', 'http', 'www', 'com', 'co', 'ec', 'org'
}

alpha = 0.4

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

def cargar_corpus():
    ruta = os.path.join(os.path.dirname(__file__), "data/corpus.json") 
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("ERROR: Archivo corpus.json no encontrado")
        return []

def analizar_texto_con_diccionario(texto, sentimiento_modelo, confianza_modelo):
    texto_lower = texto.lower()
    palabras_positivas = sum(1 for palabra in diccionario_positivo if palabra in texto_lower)
    palabras_negativas = sum(1 for palabra in diccionario_negativo if palabra in texto_lower)
    
    if palabras_positivas > palabras_negativas and palabras_positivas > 0:
        return "POS", min(confianza_modelo + 0.15, 1.0) # Aumentamos peso al diccionario
    elif palabras_negativas > palabras_positivas and palabras_negativas > 0:
        return "NEG", min(confianza_modelo + 0.15, 1.0)
    else:
        return sentimiento_modelo, confianza_modelo

@app.route("/", methods=["GET"])
def home():
    return jsonify({"mensaje": "API Activa", "endpoints": ["/analizar", "/conclusiones"]})

@app.route("/salud", methods=["GET"])
def salud():
    corpus = cargar_corpus()
    return jsonify({
        "estado": "activo",
        "publicaciones": len(corpus),
        "modelos": "Gemini 1.5 Flash + BETO"
    })

@app.route("/analizar", methods=["POST"])
def analizar():
    try:
        datos = request.json
        query = datos.get("query", "").strip()
        fecha_desde = datos.get("dateFrom")
        fecha_hasta = datos.get("dateTo")
        
        if not query:
            return jsonify({"error": "Query requerida"}), 400
        
        print(f"Búsqueda recibida: '{query}'")
        corpus = cargar_corpus()
        
        # Filtrado simple
        publicaciones_filtradas = [
            p for p in corpus 
            if query.lower() in p.get("candidato", "").replace("_", " ").lower() or 
            query.lower() in p.get("texto", "").lower()
        ]
        
        # Filtrar por fecha si es necesario (Implementación básica)
        if fecha_desde or fecha_hasta:
            # Aquí iría lógica de fecha si el string coincide
            pass

        print(f"Publicaciones encontradas: {len(publicaciones_filtradas)}")
        
        if not publicaciones_filtradas:
            return jsonify({"mensaje": "No se encontraron resultados", "publicaciones": []}), 200

        publicaciones_procesadas = []
        todos_los_textos = [] 
        
        for post in publicaciones_filtradas:
            texto_publicacion = post.get("texto", "")
            if not texto_publicacion: continue
            
            todos_los_textos.append(texto_publicacion)
            
            # 1. Análisis del Post
            try:
                res_post = modelo([texto_publicacion])[0]
                sent_post, conf_post = analizar_texto_con_diccionario(
                    texto_publicacion, res_post["label"], res_post["score"]
                )
            except:
                sent_post, conf_post = "NEU", 0.5

            # 2. Análisis de Comentarios
            comentarios_procesados = []
            sentimientos_comments = []
            confianzas_comments = []

            for com in post.get("comentarios", []):
                txt_com = com.get("texto_comentario", "")
                if not txt_com: continue
                
                todos_los_textos.append(txt_com)
                
                try:
                    res_com = modelo([txt_com])[0]
                    sent_com, conf_com = analizar_texto_con_diccionario(
                        txt_com, res_com["label"], res_com["score"]
                    )
                except:
                    sent_com, conf_com = "NEU", 0.5
                
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
                "texto": texto_publicacion,          # CAMBIO: "text" -> "texto"
                "usuario": usuario,                  # CAMBIO: Enviamos el usuario real (@JacoboG_Ecu)
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

        print("Generando wordclouds...")
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
    
    print("----- MODELOS DISPONIBLES -----")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
    except Exception as e:
        print(f"Error listando modelos: {e}")
    print("-------------------------------")
    # ----------------------------------------
    
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
    
    app.run(debug=True, host='0.0.0.0', port=5000)