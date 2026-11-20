"""Pruebas de la estructura base: salud, portada, cabeceras y CSRF."""


def test_health_responde_ok(client):
    respuesta = client.get("/health")
    assert respuesta.status_code == 200
    assert respuesta.get_json() == {"status": "ok", "db": "ok"}


def test_portada_carga(client):
    respuesta = client.get("/")
    assert respuesta.status_code == 200
    assert "ReciclaRed" in respuesta.get_data(as_text=True)


def test_cabeceras_de_seguridad(client):
    respuesta = client.get("/")
    assert respuesta.headers["X-Content-Type-Options"] == "nosniff"
    assert respuesta.headers["X-Frame-Options"] == "DENY"
    assert "frame-ancestors 'none'" in respuesta.headers["Content-Security-Policy"]


def test_post_sin_token_csrf_se_rechaza(client):
    assert client.post("/").status_code == 400


def test_pagina_inexistente_muestra_404(client):
    respuesta = client.get("/no-existe")
    assert respuesta.status_code == 404
    assert "Página no encontrada" in respuesta.get_data(as_text=True)
