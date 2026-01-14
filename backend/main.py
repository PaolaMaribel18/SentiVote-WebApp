import os
import json
import re
import io
import base64
import unicodedata

# Librerías de Machine Learning / NLP
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification 
import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer

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


# Configurar variables de entorno
load_dotenv()

# ---------------------------------------------------------------------------------------------------
# Configurar Gemini 2.5 Flash de Google Generative AI API 
# ---------------------------------------------------------------------------------------------------
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model_gemini = genai.GenerativeModel("gemini-2.5-flash-lite")
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
    "mano dura",
    
    # Expresiones y modismos positivos
    "me encanta", "apoyo", "aplaudo", "bien hecho", "gran trabajo", "felicitaciones", "bravo", "aplausos", "excelente gestión", "muy bien", "buen trabajo", "aplaudible", "admirable", "impresionante", "increíble", "fantástico", "apoyamos", "apoyaré", "apoyaré siempre", "apoyando", "apoyada", "apoyado", "apoyados", "apoyada siempre", "apoyando siempre"
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
    "engaño", "burla", "desconfianza", "cínico", "cúpula",
    # Expresiones y modismos negativos
    "que asco", "que vergüenza", "pésimo", "pésima", "pésimos", "pésimas", "lamentable", "decepcionante", "decepcionado", "decepcionada", "decepcionados", "decepcionadas", "fracaso total", "puro cuento", "pura mentira", "mentira tras mentira", "mentiroso", "mentirosa", "mentirosos", "mentirosas", "no sirve", "no sirven", "no sirvió", "no sirvieron", "no funciona", "no funcionan", "no funcionará", "no funcionarán", "no funcionaría", "no funcionarían",
    # Expresiones frecuentes en comentarios
    "es un chiste", "llenando los bolsillos", "cachetes", "otra vez", "no llegará", "no aporta", "no suma", "no representa", "no cuenta", "no importa", "no sirve para nada", "no tiene sentido", "no tiene caso", "no tiene lógica", "no tiene razón", "no tiene futuro", "no tiene solución", "no tiene arreglo", "no tiene remedio", "no tiene esperanza", "no tiene valor", "no tiene mérito", "no tiene apoyo", "no tiene respaldo", "no tiene fuerza", "no tiene liderazgo", "no tiene experiencia", "no tiene capacidad", "no tiene honestidad", "no tiene transparencia", "no tiene eficiencia", "no tiene competencia", "no tiene propuestas", "no tiene calma", "no tiene mano dura"
]

# Diccionario de insultos y malas palabras ecuatorianas (puedes ampliarlo según tu contexto)
diccionario_insultos_ecuador = [
    "huevon", "huevón", "verga", "longo", "caretuco", "mamerto", "pendejo", "cojudo", "cojudos", "cojuda", "cojudas", "maricón", "maricon", "puta", "puto", "putas", "putos", "mierda", "jodido", "jodida", "jodidos", "jodidas", "cabron", "cabrona", "cabrones", "chucha", "chuchaqui", "chuchaquis", "chuchaqueros", "chuchaquera", "chuchaqueras", "chuchaquero", "chuchaqueros", "carajo", "carajos", "culero", "culera", "culeros", "culeras", "culicagado", "culicagada", "culicagados", "culicagadas", "mamón", "mamon", "mamona", "mamones", "mamonas", "pendejada", "pendejadas", "pendejo", "pendeja", "pendejos", "pendejas", "baboso", "babosa", "babosos", "babosas", "imbecil", "imbécil", "imbeciles", "imbéciles", "idiota", "idiotas", "tarado", "tarada", "tarados", "taradas", "zángano", "zangano", "zángana", "zangana", "zánganos", "zanganos", "zánganas", "zanganas"
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
    # Verbos y conectores comunes que no aportan sentimiento
    'ser', 'estar', 'hacer', 'decir', 'ver', 'ir', 'dar', 'ya', 'si', 'no', 'tan', 'muy', 
    'mas', 'más', 'porque', 'porqué', 'ahora', 'aqui', 'aquí', 'alli', 'allí', 'entonces',
    'creo', 'dice', 'hace', 'solo', 'sólo', 'cada', 'vez', 'todo', 'toda', 'todos', 'todas',
    'gente', 'pues', 'así', 'asi', 'cosa', 'cosas', 'año', 'años', 'video', 'foto', 'imagen'
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
    """Limpia el texto para el wordcloud eliminando ruido y palabras cortas"""
    if not texto: return ""
    
    # Pasar a minúsculas
    texto = texto.lower()
    
    # Eliminar URLs completas
    texto = re.sub(r'http\S+|www\.\S+', '', texto)
    
    # Eliminar menciones (@usuario)
    texto = re.sub(r'@\w+', '', texto)
    
    # Hashtags: Quitar el símbolo # pero dejar el texto (opcional: quitar todo si prefieres)
    texto = re.sub(r'#', '', texto)
    
    # Eliminar caracteres especiales (dejando letras y tildes)
    texto = re.sub(r'[^\w\sáéíóúñü]', ' ', texto)
    
    # Eliminar números
    texto = re.sub(r'\d+', '', texto)
    
    # Eliminar palabras de 1 o 2 letras (ruido como "x", "q", "de", "el")
    texto = re.sub(r'\b\w{1,2}\b', '', texto)
    
    # Eliminar espacios múltiples
    texto = re.sub(r'\s+', ' ', texto).strip()
    
    return texto

# Función para generar wordcloud y devolver imagen en base64 y palabras frecuentes 

def generar_wordcloud(textos, colormap='viridis'): 
    """Genera un wordcloud a partir de una lista de textos con color específico"""
    try:
        # Usamos la limpieza mejorada del paso anterior
        texto_combinado = ' '.join([limpiar_texto_para_wordcloud(texto) for texto in textos if texto])
        
        if not texto_combinado.strip() or len(texto_combinado) < 3:
            return None, {} 
        
        wordcloud = WordCloud(
            width=800, height=400,
            background_color='white',
            max_words=80,             # Menos palabras para que sea más legible
            stopwords=STOP_WORDS_ES,
            min_font_size=10, max_font_size=90,
            colormap=colormap,        
            relative_scaling=0.5,
            collocations=False,       # Evita frases repetidas
            random_state=42
        ).generate(texto_combinado)
        
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150, facecolor='white')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        plt.close()
        
        return img_base64, wordcloud.words_
        
    except Exception as e:
        print(f"Error generando wordcloud: {e}")
        return None, {}
    
# Función para normalizar palabras y detectar insultos disfrazados
def normalizar_palabra(palabra):
    # Quitar acentos y normalizar caracteres
    palabra = unicodedata.normalize('NFKD', palabra).encode('ascii', 'ignore').decode('utf-8')
    # Reemplazos comunes de leet y símbolos
    reemplazos = {
        '1': 'i', '3': 'e', '4': 'a', '5': 's', '7': 't', '0': 'o', '@': 'a', '$': 's', '!': 'i', 'x': 'a', '*': 'a', '?': 'a', 'ñ': 'n'
    }
    for k, v in reemplazos.items():
        palabra = palabra.replace(k, v)
    return palabra

# Regex para malas palabras disfrazadas (puedes ampliar)
regex_insultos = [
    r'm[i1!][e3]r[dtd][a@x*?]',
    r'h[ue]+v[o0]n',
    r'p[u*]t[ao@*?]',
    r'c[o0]j[u*]d[ao@*?]',
    r'v[e3]rg[a@x*?]',
    r'mam[o0]n',
    r'imb[e3]c[i1]l',
    r'idi[o0]t[ao@*?]',
    r'p[e3]nd[e3]j[ao@*?]',
    r'cabron',
    r'chucha',
    r'jodid[oa@*?]',
    r'babos[oa@*?]',
    r'tarad[oa@*?]',
    r'zangan[oa@*?]'
]

def es_insulto(palabra):
    palabra_norm = normalizar_palabra(palabra.lower())
    for insulto in diccionario_insultos_ecuador:
        if insulto in palabra_norm:
            return True
    for patron in regex_insultos:
        if re.fullmatch(patron, palabra_norm):
            return True
    return False

# Ampliar el diccionario negativo con palabras problemáticas
palabras_negativas_extra = [
    "culpa", "culpable", "culpables", "drogas", "droga", "panfleto", "panfletos", "curia", "carita", "miedo", "pobres", "negro", "indecencia", "indecente", "indecentes", "pobre", "pobresa", "pobrezas", "caritas", "curias", "negros", "miedos"
]
diccionario_negativo = list(set(diccionario_negativo + palabras_negativas_extra))

# --------------------------------------------------------------------------------------
# Generar wordclouds por sentimiento con filtrado avanzado
# --------------------------------------------------------------------------------------
# Inicializar stemmer español
stemmer = SnowballStemmer("spanish")

# Filtrado por raíz (stemming) en el filtrado de wordclouds
def filtrar_por_diccionario(textos, sentimiento):
    filtrados = []
    stems_neg = set(stemmer.stem(p) for p in diccionario_negativo)
    stems_pos = set(stemmer.stem(p) for p in diccionario_positivo)
    for texto in textos:
        palabras = texto.lower().split()
        palabras_filtradas = []
        for p in palabras:
            if es_insulto(p):
                continue
            stem = stemmer.stem(p)
            if sentimiento == "POS" and (p in diccionario_negativo or stem in stems_neg):
                continue
            if sentimiento == "NEG" and (p in diccionario_positivo or stem in stems_pos):
                continue
            if sentimiento == "NEU" and ((p in diccionario_positivo or stem in stems_pos) or (p in diccionario_negativo or stem in stems_neg)):
                continue
            palabras_filtradas.append(p)
        filtrados.append(' '.join(palabras_filtradas))
    return filtrados

# Generar wordclouds separados por sentimiento


# --------------------------------------------------------------------------------------
# Función auxiliar para usar Gemini en la selección de keywords para WordCloud
# --------------------------------------------------------------------------------------
def extraer_palabras_clave_gemini(textos, sentimiento):
    """Usa Gemini para extraer palabras clave relevantes y limpiar ruido."""
    if not model_gemini:
        return None
    
    # Unir textos y truncar si es demasiado largo (aprox 25k caracteres para evitar errores de cuota/contexto)
    texto_completo = "\n".join(textos)[:25000] 
    
    prompt = f"""
    Actúa como un experto en análisis de sentimiento político de Ecuador.
    Analiza los siguientes comentarios que han sido clasificados como: {sentimiento}.
    
    Tu tarea es generar una lista de palabras clave para una Nube de Palabras (WordCloud).
    
    Instrucciones obligatorias:
    1. EXTRAE solo las palabras o frases cortas (máx 2 palabras) que justifiquen el sentimiento {sentimiento}.
    2. ELIMINA RUIDO: Nombres propios de políticos (Noboa, Luisa, Topic, Iza, etc.), ciudades (Quito, Guayaquil, Ecuador), gentilicios, y palabras genéricas (país, gobierno, presidente, gente, ver, video, pueblo).
    3. MANTÉN la frecuencia semántica: Si un tema es muy recurrente en los textos, repite las palabras clave relacionadas varias veces en tu respuesta para que resalten en la nube.
    4. Devuelve SOLO las palabras separadas por espacio. Sin explicaciones, sin markdown, sin viñetas.

    Textos a analizar:
    {texto_completo}
    """
    
    try:
        response = model_gemini.generate_content(prompt)
        return response.text.replace("\n", " ").strip()
    except Exception as e:
        print(f"Error Gemini WordCloud ({sentimiento}): {e}")
        return None

def generar_wordclouds_por_sentimiento(publicaciones):
    textos_por_sentimiento = {
        "POS": [],
        "NEG": [],
        "NEU": []
    }

    # Mapa de colores para cada sentimiento (Visualmente ayuda a diferenciar)
    colores_map = {
        "POS": "Greens",   
        "NEG": "Reds",     
        "NEU": "Blues"     
    }

    conteo_origen = {"posts": 0, "comentarios": 0}

    for pub in publicaciones:
        # 1. El texto del POST
        sentimiento_post = pub.get("sentiment", "NEU")
        texto_post = pub.get("texto", "")      
        if not texto_post:
            texto_post = pub.get("text", "")
            if texto_post:
                print(f"ALERTA DEBUG: El texto estaba en 'text', no en 'texto'. Ajusta tu código.")

        if sentimiento_post in textos_por_sentimiento and texto_post:
            textos_por_sentimiento[sentimiento_post].append(texto_post)
            conteo_origen["posts"] += 1
        
        # 2. El texto del COMENTARIO
        for comentario in pub.get("comentarios", []):
            sentimiento_com = comentario.get("sentimiento_comentario", "NEU")
            texto_com = comentario.get("texto_comentario", "")
            
            if sentimiento_com in textos_por_sentimiento and texto_com:
                textos_por_sentimiento[sentimiento_com].append(texto_com)
                conteo_origen["comentarios"] += 1
                
    wordclouds_sentimiento = {}
    for sentimiento, textos in textos_por_sentimiento.items():
        color = colores_map.get(sentimiento, "viridis")
        
        # --- LÓGICA MEJORADA CON IA ---
        texto_para_nube = None
        palabras_frecuentes = {}
        img_base64 = None

        # Intentar usar Gemini para filtrar ruido y extraer esencia si hay suficientes textos
        if model_gemini and textos and len(textos) > 5:
             print(f"Mejorando WordCloud {sentimiento} con IA Gemini...")
             texto_para_nube = extraer_palabras_clave_gemini(textos, sentimiento)
        
        if texto_para_nube:
             # Si Gemini funcionó, generamos la nube directamente con su respuesta "limpia"
             # Pasamos como lista de 1 elemento, generar_wordcloud lo limpiará (quita acentos/letras sueltas) pero mantendrá la esencia
             img_base64, palabras_frecuentes = generar_wordcloud([texto_para_nube], colormap=color)
        else:
             # Fallback lógica clásica (filtrado regex + diccionario) si falla Gemini o hay pocos textos
             print(f"Generando WordCloud {sentimiento} con lógica local (Regex/Diccionario)...")
             textos_filtrados = filtrar_por_diccionario(textos, sentimiento)
             img_base64, palabras_frecuentes = generar_wordcloud(textos_filtrados, colormap=color)
        
        wordclouds_sentimiento[sentimiento] = {
            "imagen": img_base64, 
            "palabras": palabras_frecuentes if img_base64 else {}
        }

    return wordclouds_sentimiento

# --------------------------------------------------------------------------------------
# Cargar corpus desde archivo JSON 
#--------------------------------------------------------------------------------------
def cargar_corpus():
    ruta = os.path.join(os.path.dirname(__file__), "data/corpus_completo.json") 
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
    con manejo mejorado de negación, frases y sarcasmo.
    """
    texto_lower = texto.lower()

    # Refuerzo: Si el texto contiene insultos, forzar NEG
    palabras = re.findall(r'\b\w+\b', texto_lower)
    for palabra in palabras:
        if es_insulto(palabra):
            return "NEG", 1.0

    # 1. Limpieza y Tokenización del texto de entrada
    # Mantener el orden para la negación y buscar frases completas
    words = palabras
    palabras_positivas_contadas = 0
    palabras_negativas_contadas = 0

    # Buscar frases completas positivas/negativas
    for frase in diccionario_positivo:
        if frase in texto_lower:
            palabras_positivas_contadas += 2 if ' ' in frase else 1
    for frase in diccionario_negativo:
        if frase in texto_lower:
            palabras_negativas_contadas += 2 if ' ' in frase else 1

    # Lógica de negación mejorada: si una palabra positiva/negativa está precedida por un negador en las 3 palabras anteriores
    for i, word in enumerate(words):
        window = words[max(0, i-3):i]
        is_negated = any(w in NEGATORS for w in window)
        if word in diccionario_positivo and is_negated:
            palabras_positivas_contadas -= 1
        if word in diccionario_negativo and is_negated:
            palabras_negativas_contadas -= 1

    # Refuerzo según confianza del modelo
    if palabras_positivas_contadas > palabras_negativas_contadas and palabras_positivas_contadas > 0:
        if confianza_modelo < 0.7:
            return "POS", min(confianza_modelo + 0.3, 1.0)
        return "POS", min(confianza_modelo + 0.15, 1.0)
    elif palabras_negativas_contadas > palabras_positivas_contadas and palabras_negativas_contadas > 0:
        if confianza_modelo < 0.7:
            return "NEG", min(confianza_modelo + 0.3, 1.0)
        return "NEG", min(confianza_modelo + 0.15, 1.0)
    
    # Detección simple de sarcasmo: si hay "claro", "seguro", "obvio" y signos de exclamación
    sarcasmo = any(s in texto_lower for s in ["claro", "seguro", "obvio"]) and ("!" in texto or "¿" in texto)
    if sarcasmo:
        # Invertir el sentimiento si el modelo no está seguro
        if confianza_modelo < 0.8:
            if sentimiento_modelo == "POS":
                return "NEG", min(confianza_modelo + 0.2, 1.0)
            elif sentimiento_modelo == "NEG":
                return "POS", min(confianza_modelo + 0.2, 1.0)
    
    # Refuerzo para frases cortas y sarcásticas
    if len(words) <= 7 and palabras_negativas_contadas > 0:
        return "NEG", 1.0
    
    return sentimiento_modelo, confianza_modelo

# Funciones de manejo de fechas y rangos
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
       # Wordcloud General (Multicolor por defecto 'viridis' o 'Set2')
        wc_general, _ = generar_wordcloud(todos_los_textos, colormap='Dark2') 
        
        # Wordclouds por sentimiento (Con colores específicos)
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
        
        Responde en 2 frases objetivas como analista de datos electoral.
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