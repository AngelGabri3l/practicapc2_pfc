"""US-05 · Catálogo de materiales."""
import pytest


@pytest.fixture
def admin(client, crear_usuario, iniciar_sesion):
    crear_usuario("admin@example.com", rol="admin")
    iniciar_sesion(client, "admin@example.com")
    return client


def test_ca1_material_nuevo_aparece_en_el_catalogo(admin, post, consultar):
    respuesta = post(admin, "/admin/materiales", {"nombre": "Tetra Pak"}, follow_redirects=True)
    assert "Tetra Pak" in respuesta.get_data(as_text=True)
    assert consultar("SELECT COUNT(*) AS n FROM materiales WHERE nombre = %s", ("Tetra Pak",), uno=True)["n"] == 1


def test_ca2_nombre_duplicado_se_rechaza(admin, post, consultar):
    respuesta = post(admin, "/admin/materiales", {"nombre": "vidrio"})
    assert respuesta.status_code == 422
    assert "ya existe" in respuesta.get_data(as_text=True)
    assert consultar("SELECT COUNT(*) AS n FROM materiales", uno=True)["n"] == 6


def test_ca3_catalogo_inicial_tiene_los_seis_materiales(consultar):
    nombres = {fila["nombre"] for fila in consultar("SELECT nombre FROM materiales")}
    assert nombres == {"Papel", "Cartón", "Plástico", "Vidrio", "Metal", "Electrónicos"}


def test_solo_el_administrador_gestiona_materiales(client, post, crear_usuario, iniciar_sesion):
    crear_usuario("ana@example.com", rol="ciudadano")
    iniciar_sesion(client, "ana@example.com")
    assert post(client, "/admin/materiales", {"nombre": "Pilas"}).status_code == 403
