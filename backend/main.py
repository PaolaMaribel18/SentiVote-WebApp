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

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:3000"])

# Cargar modelo de análisis de sentimiento en español
try:
    modelo = pipeline("sentiment-analysis", model="finiteautomata/beto-sentiment-analysis")
    print("Modelo BETO cargado exitosamente")
except Exception as e:
    print(f"Error cargando modelo BETO: {e}")
    print("Usando modelo alternativo...")
    modelo = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")

# Diccionario de palabras positivas y negativas
diccionario_positivo = [
    "bueno", "excelente", "positivo", "genial", "amor", "éxito", "feliz", "maravilloso", 
    "fortaleza", "esperanza", "progreso", "desarrollo", "bienestar", "paz", "justicia",
    "honesto", "transparente", "eficiente", "competente", "liderazgo", "experiencia"
]

diccionario_negativo = [
    "malo", "horrible", "negativo", "terrible", "odio", "fracaso", "débil", "miseria", 
    "desastre", "corrupción", "mentira", "robo", "incompetente", "ineficiente", "crisis",
    "problema", "conflicto", "violencia", "inseguridad", "pobreza", "desempleo"
]

# Palabras vacías en español para el wordcloud
# Articulos relacionados a los mapas de palabras
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

# Valor de alfa
alpha = 0.4

def limpiar_texto_para_wordcloud(texto):
    """Limpia el texto para el wordcloud"""
    # Remover URLs
    texto = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', texto)
    # Remover menciones @usuario
    texto = re.sub(r'@\w+', '', texto)
    # Remover hashtags pero mantener el texto
    texto = re.sub(r'#(\w+)', r'\1', texto)
    # Remover caracteres especiales excepto letras, números y espacios
    texto = re.sub(r'[^\w\s]', ' ', texto)
    # Remover números solos
    texto = re.sub(r'\b\d+\b', '', texto)
    # Normalizar espacios
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto.lower()

def generar_wordcloud(textos):
    """Genera un wordcloud a partir de una lista de textos"""
    try:
        # Combinar todos los textos
        texto_combinado = ' '.join([limpiar_texto_para_wordcloud(texto) for texto in textos if texto.strip()])
        
        if not texto_combinado.strip():
            return None
        
        # Configuración del wordcloud
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            max_words=50,
            stopwords=STOP_WORDS_ES,
            min_font_size=10,
            max_font_size=80,
            colormap='viridis',
            relative_scaling=0.5,
            random_state=42
        ).generate(texto_combinado)
        
        # Crear la imagen
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        
        # Convertir a base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150, 
                   facecolor='white', edgecolor='none')
        img_buffer.seek(0)
        
        # Codificar en base64
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        plt.close()
        
        return img_base64
        
    except Exception as e:
        print(f"Error generando wordcloud: {e}")
        return None

def cargar_corpus():
    """Cargar el corpus de datos"""
    ruta = os.path.join(os.path.dirname(__file__), "data/corpus_completo.json")
    print("Ruta del archivo JSON:", ruta)
    
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            corpus = json.load(f)
        print(f"Corpus cargado exitosamente: {len(corpus)} publicaciones")
        return corpus
    except FileNotFoundError:
        print("ERROR: Archivo corpus_completo.json no encontrado")
        return []
    except json.JSONDecodeError as e:
        print(f"ERROR: Error al decodificar JSON: {e}")
        return []

def filtrar_por_fecha(publicaciones, fecha_desde=None, fecha_hasta=None):
    """Filtrar publicaciones por rango de fechas"""
    if not fecha_desde and not fecha_hasta:
        return publicaciones
    return publicaciones

def analizar_texto_con_diccionario(texto, sentimiento_modelo, confianza_modelo):
    """Mejorar el análisis usando el diccionario de palabras"""
    texto_lower = texto.lower()
    
    palabras_positivas = sum(1 for palabra in diccionario_positivo if palabra in texto_lower)
    palabras_negativas = sum(1 for palabra in diccionario_negativo if palabra in texto_lower)
    
    if palabras_positivas > palabras_negativas and palabras_positivas > 0:
        return "POS", min(confianza_modelo + 0.1, 1.0)
    elif palabras_negativas > palabras_positivas and palabras_negativas > 0:
        return "NEG", min(confianza_modelo + 0.1, 1.0)
    else:
        return sentimiento_modelo, confianza_modelo

@app.route("/", methods=["GET"])
def home():
    """Endpoint de prueba"""
    return jsonify({
        "mensaje": "API de Análisis de Sentimientos funcionando",
        "endpoints": {
            "/analizar": "POST - Analizar sentimientos de un candidato",
            "/salud": "GET - Verificar estado de la API"
        }
    })

@app.route("/salud", methods=["GET"])
def salud():
    """Verificar el estado de la API"""
    corpus = cargar_corpus()
    return jsonify({
        "estado": "activo",
        "modelo_cargado": True,
        "publicaciones_disponibles": len(corpus),
        "candidatos_disponibles": list(set([post.get("candidato", "Sin candidato") for post in corpus]))
    })

@app.route("/analizar", methods=["POST"])
def analizar():
    """Endpoint principal para análisis de sentimientos"""
    try:
        datos = request.json
        if not datos:
            return jsonify({"error": "No se recibieron datos JSON"}), 400
        
        query = datos.get("query", "").strip()
        fecha_desde = datos.get("dateFrom")
        fecha_hasta = datos.get("dateTo")
        plataformas = datos.get("platforms", [])
        min_engagement = datos.get("minEngagement", 0)
        
        if not query:
            return jsonify({"error": "La consulta (query) es requerida."}), 400
        
        print(f"Búsqueda recibida: '{query}'")
        
        # Cargar corpus
        corpus = cargar_corpus()
        if not corpus:
            return jsonify({"error": "No se pudo cargar el corpus de datos"}), 500

        # Depuración: Mostrar candidatos disponibles
        candidatos_disponibles = [post.get("candidato", "Sin candidato") for post in corpus]
        print(f"Candidatos disponibles: {set(candidatos_disponibles)}")

        # Búsqueda flexible
        publicaciones_filtradas = []
        for post in corpus:
            candidato = post.get("candidato", "").lower()
            if query.lower() in candidato or any(word.lower() in candidato for word in query.split()):
                publicaciones_filtradas.append(post)
        
        print(f"Publicaciones encontradas: {len(publicaciones_filtradas)}")
        
        if not publicaciones_filtradas:
            return jsonify({
                "mensaje": f"No se encontraron publicaciones para '{query}'.",
                "candidatos_disponibles": list(set(candidatos_disponibles))
            }), 404

        # Filtrar por fechas
        publicaciones_filtradas = filtrar_por_fecha(publicaciones_filtradas, fecha_desde, fecha_hasta)

        # Procesar las publicaciones filtradas
        publicaciones_procesadas = []
        todos_los_textos = []  # Para el wordcloud general
        
        for post in publicaciones_filtradas:
            print(f"Procesando publicación del candidato {post.get('candidato', 'Sin candidato')}")
            
            # Analizar la publicación
            texto_publicacion = post.get("texto", "")
            if not texto_publicacion:
                continue
            
            # Agregar texto al wordcloud general
            todos_los_textos.append(texto_publicacion)
                
            try:
                resultado_publicacion = modelo([texto_publicacion])[0]
                sentimiento_publicacion = resultado_publicacion["label"]
                confianza_publicacion = round(resultado_publicacion["score"], 3)
                
                sentimiento_publicacion, confianza_publicacion = analizar_texto_con_diccionario(
                    texto_publicacion, sentimiento_publicacion, confianza_publicacion
                )
                
            except Exception as e:
                print(f"Error analizando publicación: {e}")
                sentimiento_publicacion = "NEU"
                confianza_publicacion = 0.5

            # Analizar los comentarios
            comentarios_detalle = []
            sentimientos_comentarios = []
            confianza_comentarios = []

            for comentario in post.get("comentarios", []):
                texto_comentario = comentario.get("texto_comentario", "")
                if not texto_comentario:
                    continue
                
                # Agregar comentario al wordcloud general
                todos_los_textos.append(texto_comentario)
                    
                try:
                    resultado_comentario = modelo([texto_comentario])[0]
                    sentimiento_comentario = resultado_comentario["label"]
                    confianza_comentario = round(resultado_comentario["score"], 3)
                    
                    sentimiento_comentario, confianza_comentario = analizar_texto_con_diccionario(
                        texto_comentario, sentimiento_comentario, confianza_comentario
                    )
                    
                except Exception as e:
                    print(f"Error analizando comentario: {e}")
                    sentimiento_comentario = "NEU"
                    confianza_comentario = 0.5

                comentarios_detalle.append({
                    "id_comentario": comentario.get("id_comentario", f"comment_{len(comentarios_detalle)}"),
                    "texto_comentario": texto_comentario,
                    "sentimiento_comentario": sentimiento_comentario,
                    "confianza_comentario": confianza_comentario
                })

                sentimientos_comentarios.append(sentimiento_comentario)
                confianza_comentarios.append(confianza_comentario)

            # Calcular sentimiento general de los comentarios
            if sentimientos_comentarios:
                avg_sentimiento_comentarios = max(set(sentimientos_comentarios), key=sentimientos_comentarios.count)
                avg_confianza_comentarios = sum(confianza_comentarios) / len(confianza_comentarios)
            else:
                avg_sentimiento_comentarios = "NEU"
                avg_confianza_comentarios = 0.5

            # Sentimiento final combinado
            if sentimiento_publicacion == "POS" and avg_sentimiento_comentarios == "POS":
                sentimiento_final = "POS"
            elif sentimiento_publicacion == "NEG" or avg_sentimiento_comentarios == "NEG":
                sentimiento_final = "NEG"
            else:
                sentimiento_final = "NEU"

            # Combinación de confianza
            confianza_final = alpha * confianza_publicacion + (1 - alpha) * avg_confianza_comentarios

            fecha = post.get("fecha", "")
            
            publicaciones_procesadas.append({
                "id_post": post.get("id_post", f"post_{len(publicaciones_procesadas)}"),
                "candidato": post.get("candidato", "Sin candidato"),
                "texto": texto_publicacion,
                "sentimiento_publicacion": sentimiento_publicacion,
                "confianza_publicacion": confianza_publicacion,
                "comentarios": comentarios_detalle,
                "sentimiento_comentarios": avg_sentimiento_comentarios,
                "confianza_comentarios": round(avg_confianza_comentarios, 3),
                "sentimiento_final": sentimiento_final,
                "confianza_final": round(confianza_final, 3),
                "fecha": fecha
            })

        # Generar wordcloud general
        print("Generando wordcloud...")
        wordcloud_image = generar_wordcloud(todos_los_textos)
        
        response_data = {
            "publicaciones": publicaciones_procesadas,
            "wordcloud": wordcloud_image,
            "total_textos_analizados": len(todos_los_textos)
        }

        print(f"Publicaciones procesadas exitosamente: {len(publicaciones_procesadas)}")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error en endpoint /analizar: {e}")
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500

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
    
    app.run(debug=True, host='0.0.0.0', port=5000)