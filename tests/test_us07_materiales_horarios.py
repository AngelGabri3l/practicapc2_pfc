"""US-07 · Materiales y horarios de un punto."""
import pytest


@pytest.fixture
def escenario(entrar_como, crear_punto, consultar):
    admin, _ = entrar_como("admin")
    punto_id = crear_punto()
    ids = {fila["nombre"]: fila["id"] for fila in consultar("SELECT id, nombre FROM materiales")}
    return admin, punto_id, ids


def test_ca1_materiales_quedan_asociados(escenario, post, consultar):
    admin, punto_id, ids = escenario
    respuesta = post(admin, f"/admin/puntos/{punto_id}/materiales-horarios",
                     {"materiales": [str(ids["Vidrio"]), str(ids["Papel"])]})
    assert respuesta.status_code == 302
    filas = consultar("SELECT material_id FROM punto_material WHERE punto_id = %s", (punto_id,))
    assert {fila["material_id"] for fila in filas} == {ids["Vidrio"], ids["Papel"]}


def test_ca2_horario_queda_guardado(escenario, post, consultar):
    admin, punto_id, _ = escenario
    post(admin, f"/admin/puntos/{punto_id}/materiales-horarios", {"apertura_1": "08:00", "cierre_1": "17:00"})
    horario = consultar("SELECT dia, TIME_FORMAT(apertura, '%%H:%%i') AS a, TIME_FORMAT(cierre, '%%H:%%i') AS c "
                        "FROM horarios WHERE punto_id = %s", (punto_id,), uno=True)
    assert horario == {"dia": 1, "a": "08:00", "c": "17:00"}


def test_ca3_cierre_antes_de_apertura_se_rechaza(escenario, post, consultar):
    admin, punto_id, ids = escenario
    respuesta = post(admin, f"/admin/puntos/{punto_id}/materiales-horarios",
                     {"materiales": [str(ids["Metal"])], "apertura_2": "18:00", "cierre_2": "09:00"})
    assert respuesta.status_code == 422
    assert "posterior a la de apertura" in respuesta.get_data(as_text=True)
    assert consultar("SELECT COUNT(*) AS n FROM horarios", uno=True)["n"] == 0
    assert consultar("SELECT COUNT(*) AS n FROM punto_material", uno=True)["n"] == 0


def test_ca4_al_reabrir_se_ven_los_datos_guardados(escenario, post):
    admin, punto_id, ids = escenario
    url = f"/admin/puntos/{punto_id}/materiales-horarios"
    post(admin, url, {"materiales": [str(ids["Cartón"])], "apertura_3": "09:30", "cierre_3": "13:00"})
    html = admin.get(url).get_data(as_text=True)
    assert f'value="{ids["Cartón"]}" checked' in html
    assert 'value="09:30"' in html and 'value="13:00"' in html
