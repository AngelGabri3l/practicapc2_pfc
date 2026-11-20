"""US-09 · Buscar puntos por material y distrito."""
import pytest


@pytest.fixture
def puntos(app, crear_punto, consultar):
    from app import db as bd
    ids = {fila["nombre"]: fila["id"] for fila in consultar("SELECT id, nombre FROM materiales")}
    creados = {
        "Punto A": crear_punto("Punto A", distrito="Miraflores"),
        "Punto B": crear_punto("Punto B", distrito="Lince"),
        "Punto C": crear_punto("Punto C", distrito="Miraflores"),
    }
    with app.app_context():
        for nombre, material in (("Punto A", "Vidrio"), ("Punto B", "Vidrio"), ("Punto C", "Papel")):
            bd.execute("INSERT INTO punto_material (punto_id, material_id) VALUES (%s, %s)", (creados[nombre], ids[material]))
    return ids


def nombres(respuesta):
    html = respuesta.get_data(as_text=True)
    return {n for n in ("Punto A", "Punto B", "Punto C") if n in html}


def test_ca1_filtro_por_material(client, puntos):
    assert nombres(client.get(f"/puntos/?material={puntos['Vidrio']}")) == {"Punto A", "Punto B"}


def test_ca2_filtro_por_distrito(client, puntos):
    assert nombres(client.get("/puntos/?distrito=Miraflores")) == {"Punto A", "Punto C"}


def test_ca3_filtros_combinados(client, puntos):
    assert nombres(client.get(f"/puntos/?material={puntos['Vidrio']}&distrito=Miraflores")) == {"Punto A"}


def test_ca4_sin_resultados_permite_limpiar_filtros(client, puntos):
    html = client.get(f"/puntos/?material={puntos['Metal']}").get_data(as_text=True)
    assert "Sin resultados" in html and "Limpiar filtros" in html


def test_parametros_maliciosos_no_rompen_la_busqueda(client, puntos):
    respuesta = client.get("/puntos/?material=1%20OR%201=1&distrito=%27%20OR%20%271%27=%271")
    assert respuesta.status_code == 200
    assert nombres(respuesta) == {"Punto A", "Punto B", "Punto C"}
