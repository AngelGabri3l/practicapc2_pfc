"""US-17 · Marcar como recogida o liberar."""
import pytest


@pytest.fixture
def aceptada(entrar_como, crear_usuario, crear_oferta):
    recolector, recolector_id = entrar_como("recolector")
    oferta = crear_oferta(crear_usuario("ana@example.com"), estado="Aceptada", recolector_id=recolector_id)
    return recolector, oferta


def test_ca1_marcar_como_recogida_registra_la_fecha(aceptada, post, consultar):
    recolector, oferta = aceptada
    post(recolector, f"/recolector/ofertas/{oferta}/recogida")
    fila = consultar("SELECT estado, recogida_en FROM ofertas WHERE id = %s", (oferta,), uno=True)
    assert fila["estado"] == "Recogida" and fila["recogida_en"] is not None


def test_ca2_liberar_la_devuelve_a_disponible(aceptada, post, consultar):
    recolector, oferta = aceptada
    post(recolector, f"/recolector/ofertas/{oferta}/liberar")
    fila = consultar("SELECT estado, recolector_id FROM ofertas WHERE id = %s", (oferta,), uno=True)
    assert fila == {"estado": "Disponible", "recolector_id": None}


def test_ca3_otro_recolector_no_puede_modificarla(aceptada, entrar_como, post, consultar):
    _, oferta = aceptada
    intruso, _ = entrar_como("recolector")
    assert post(intruso, f"/recolector/ofertas/{oferta}/recogida").status_code == 403
    assert post(intruso, f"/recolector/ofertas/{oferta}/liberar").status_code == 403
    assert consultar("SELECT estado FROM ofertas WHERE id = %s", (oferta,), uno=True)["estado"] == "Aceptada"
