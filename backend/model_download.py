from transformers import pipeline

modelo = pipeline("sentiment-analysis", model="finiteautomata/beto-sentiment-analysis")
print("Modelo descargado y listo.")
