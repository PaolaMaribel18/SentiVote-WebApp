# backend/tests/test_units.py
import pytest
from backend.main import (
    limpiar_texto_para_wordcloud,
    normalizar_palabra,
    es_insulto,
    analizar_texto_con_diccionario,
    parse_date
)

# 1. Prueba de limpieza de texto para nubes de palabras
@pytest.mark.parametrize(
    "texto, esperado",
    [
        ("¡Visita https://example.com #Ecuador ahora!", "visita ecuador ahora"),
        ("RT @user: Ganamos 100%", "ganamos"),
    ],
)
def test_limpiar_texto_para_wordcloud(texto, esperado):
    assert limpiar_texto_para_wordcloud(texto) == esperado

# 2. Prueba de normalización de palabras con caracteres especiales o leet
@pytest.mark.parametrize(
    "palabra, esperado",
    [
        ("c0rrupci0n", "corrupcion"),
        ("m4l4", "mala"),
    ],
)
def test_normalizar_palabra(palabra, esperado):
    assert normalizar_palabra(palabra) == esperado

# 3. Prueba de detección de insultos
@pytest.mark.parametrize(
    "palabra, esperado",
    [
        ("huevón", True),
        ("huxv0n", True),  # leet
        ("excelente", False),
    ],
)
def test_es_insulto(palabra, esperado):
    assert es_insulto(palabra) is esperado

# 4. Prueba de refuerzo con diccionario
@pytest.mark.parametrize(
    "texto, modelo_label, modelo_conf, esperado_label",
    [
        ("Este candidato es un desastre", "NEU", 0.6, "NEG"),
        ("Gran líder transparente", "NEU", 0.6, "POS"),
    ],
)
def test_analizar_texto_con_diccionario(texto, modelo_label, modelo_conf, esperado_label):
    label, conf = analizar_texto_con_diccionario(texto, modelo_label, modelo_conf)
    assert label == esperado_label
    assert 0.0 <= conf <= 1.0

# 5. Prueba de conversión de fechas a zona UTC
from datetime import timezone

def test_parse_date_inicio_y_fin():
    inicio = parse_date("2025-01-10", is_end=False)
    fin = parse_date("2025-01-10", is_end=True)
    assert inicio.tzinfo == timezone.utc
    assert inicio.hour == 0 and inicio.minute == 0
    assert fin.hour == 23 and fin.minute == 59
