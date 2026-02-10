# backend/tests/test_routes.py
import json
from backend.main import app


def test_salud_devuelve_estado_y_fechas(monkeypatch):
    client = app.test_client()

    # simular un corpus conocido
    sample_corpus = [
        {"fecha": "2025-01-10T00:00:00Z", "texto": "post de prueba", "candidato": "A"},
        {"fecha": "2025-02-15T00:00:00Z", "texto": "otro post", "candidato": "B"},
    ]
    monkeypatch.setattr('backend.main.cargar_corpus', lambda: sample_corpus)

    response = client.get('/salud')
    data = response.get_json()

    assert response.status_code == 200
    assert data['estado'] == 'activo'
    assert data['publicaciones'] == 2
    assert data['minDate'] == '2025-01-10'
    assert data['maxDate'] == '2025-02-15'


def test_analizar_requiere_query(monkeypatch):
    client = app.test_client()
    monkeypatch.setattr('backend.main.cargar_corpus', lambda: [])

    response = client.post('/analizar', json={"query": ""})
    assert response.status_code == 400
    assert 'error' in response.get_json()

def test_conclusiones_devuelve_conclusion(monkeypatch):
    client = app.test_client()

    fake_conclusion = {
        "conclusion": "Predomina el sentimiento negativo"
    }

    monkeypatch.setattr(
        'backend.main.generar_conclusiones',
        lambda *_: fake_conclusion
    )

    response = client.post('/conclusiones', json={})
    data = response.get_json()

    assert response.status_code == 200
    assert "conclusion" in data
    assert isinstance(data["conclusion"], str)
