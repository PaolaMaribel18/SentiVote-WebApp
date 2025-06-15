from flask import Flask, request, jsonify
from transformers import pipeline
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app)  # Para permitir conexión desde el frontend

# Cargar modelo de análisis de sentimiento en español
modelo = pipeline("sentiment-analysis", model="finiteautomata/beto-sentiment-analysis")

@app.route("/analizar", methods=["POST"])
def analizar():
    datos = request.json
    textos = datos.get("textos", [])
    
    # Eliminar valores None o vacíos
    textos = [t for t in textos if t is not None and t.strip() != ""]

    
    print("Textos recibidos:", textos)  # 🖨️ Imprime los textos antes de analizarlos


    resultados = modelo(textos)
    
    print("Resultados del análisis:")
    for texto, resultado in zip(textos, resultados):
        print(f"- Texto: {texto}")
        print(f"  Sentimiento: {resultado['label']}, Confianza: {round(resultado['score'], 3)}")


    # Formato: [{'label': 'POS', 'score': 0.98}, ...]
    respuesta = []
    for i, r in enumerate(resultados):
        respuesta.append({
            "texto": textos[i], # texto_comentario_limpio
            "sentimiento": r["label"],
            "confianza": round(r["score"], 3)
        })

    return jsonify(respuesta)


@app.route("/api/tweets", methods=["GET"])
def obtener_tweets():
    ruta = os.path.join(os.path.dirname(__file__), "../data/corpus_completo.json")
    print("Ruta del archivo JSON:", ruta)
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            datos = json.load(f)
        return jsonify(datos)
    except FileNotFoundError:
        print("Archivo no encontrado")
        return jsonify({"error": "Archivo no encontrado"}), 404


if __name__ == "__main__":
    app.run(debug=True)
