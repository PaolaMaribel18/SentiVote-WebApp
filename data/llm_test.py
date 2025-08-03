import json
import requests
import time
import csv

API_KEY = "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"  
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

modelos = {
    "deepseek": "deepseek/deepseek-chat",
    "gemini": "google/gemini-2.0-flash-001",
}

def construir_prompt(texto):
    return f"""
Analiza el siguiente comentario:

\"{texto}\"

1. ¿Cuál es el sentimiento? (positivo, negativo o neutral)

Formato:
Sentimiento: ...
"""

# Carga el JSON y extrae todos los comentarios
with open("corpus_completo.json", "r", encoding="utf-8") as f:
    data = json.load(f)

comentarios = []
for post in data:
    for comentario in post.get("comentarios", []):
        comentarios.append(comentario["texto_comentario"])

# Limitar a 100 comentarios para prueba
comentarios = comentarios[:100]

# Abrir archivo CSV para guardar resultados
with open("resultados_sentimiento.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    # Escribir encabezados
    writer.writerow(["Comentario_Num", "Texto_Comentario", "Modelo", "Respuesta"])

    for i, texto in enumerate(comentarios, start=1):
        prompt = construir_prompt(texto)
        print(f"\nComentario {i}: {texto}")

        for nombre, modelo_id in modelos.items():
            data = {
                "model": modelo_id,
                "messages": [{"role": "user", "content": prompt}]
            }
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=HEADERS,
                data=json.dumps(data)
            )
            if response.status_code == 200:
                resultado = response.json()
                contenido = resultado["choices"][0]["message"]["content"].strip()
                print(f"→ Modelo {nombre}:\n{contenido}\n")
                # Guardar fila en CSV
                writer.writerow([i, texto, nombre, contenido])
            else:
                error_msg = f"Error {response.status_code}: {response.text}"
                print(f"{error_msg}")
                writer.writerow([i, texto, nombre, error_msg])

            time.sleep(1.5)  # para respetar límites de la API
