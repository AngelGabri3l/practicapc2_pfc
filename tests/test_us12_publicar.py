"""US-12 · Publicar material disponible."""
from datetime import date, timedelta

import pytest


@pytest.fixture
def datos(consultar):
    vidrio = consultar("SELECT id FROM materiales WHERE nombre = 'Vidrio'", uno=True)["id"]
    return {"material_id": str(vidrio), "cantidad": "3 cajas medianas", "direccion": "Calle Ficticia 742",
            "distrito": "Miraflores", "fecha": (date.today() + timedelta(days=1)).isoformat(),
            "hora_inicio": "16:00", "hora_fin": "18:00"}


def test_ca1_oferta_valida_queda_disponible(entrar_como, post, consultar, datos):
    ciudadano, usuario_id = entrar_como("ciudadano")
    respuesta = post(ciudadano, "/ofertas/nueva", datos)
    assert respuesta.status_code == 302
    oferta = consultar("SELECT ciudadano_id, estado, distrito FROM ofertas", uno=True)
    assert oferta == {"ciudadano_id": usuario_id, "estado": "Disponible", "distrito": "Miraflores"}


@pytest.mark.parametrize("faltante", ["material_id", "direccion", "distrito"])
def test_ca2_datos_obligatorios_vacios_se_rechazan(entrar_como, post, consultar, datos, faltante):
    ciudadano, _ = entrar_como("ciudadano")
    assert post(ciudadano, "/ofertas/nueva", {**datos, faltante: ""}).status_code == 422
    assert consultar("SELECT COUNT(*) AS n FROM ofertas", uno=True)["n"] == 0


def test_ca3_ventana_que_termina_antes_de_empezar(entrar_como, post, consultar, datos):
    ciudadano, _ = entrar_como("ciudadano")
    respuesta = post(ciudadano, "/ofertas/nueva", {**datos, "hora_inicio": "18:00", "hora_fin": "16:00"})
    assert respuesta.status_code == 422
    assert "posterior a la de inicio" in respuesta.get_data(as_text=True)
    assert consultar("SELECT COUNT(*) AS n FROM ofertas", uno=True)["n"] == 0


def test_ca4_sin_sesion_redirige_al_inicio_de_sesion(client):
    respuesta = client.get("/ofertas/nueva")
    assert respuesta.status_code == 302
    assert "/login" in respuesta.headers["Location"]


def test_recolector_no_publica_ofertas(entrar_como, post, datos):
    recolector, _ = entrar_como("recolector")
    assert post(recolector, "/ofertas/nueva", datos).status_code == 403
