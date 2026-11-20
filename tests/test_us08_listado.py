"""US-08 · Listado de puntos de acopio."""


def test_ca1_listado_muestra_nombre_direccion_y_distrito(client, crear_punto):
    crear_punto("Centro de acopio del parque", "Calle Ficticia 123", "Lince")
    html = client.get("/puntos/").get_data(as_text=True)
    for texto in ("Centro de acopio del parque", "Calle Ficticia 123", "Lince"):
        assert texto in html


def test_ca2_sin_puntos_se_muestra_el_aviso(client):
    assert "Aún no hay puntos registrados" in client.get("/puntos/").get_data(as_text=True)


def test_ca3_el_directorio_es_publico(client, crear_punto):
    crear_punto()
    respuesta = client.get("/puntos/")
    assert respuesta.status_code == 200
    assert "Punto de prueba" in respuesta.get_data(as_text=True)


def test_puntos_inactivos_no_aparecen(client, crear_punto):
    crear_punto("Punto cerrado", activo=0)
    assert "Punto cerrado" not in client.get("/puntos/").get_data(as_text=True)


def test_datos_demo_se_cargan_una_sola_vez(app, consultar):
    from app.seed import crear_datos_demo
    app.config["SEED_DEMO"] = True
    try:
        with app.app_context():
            crear_datos_demo()
            crear_datos_demo()
    finally:
        app.config["SEED_DEMO"] = False
    assert consultar("SELECT COUNT(*) AS n FROM puntos_acopio", uno=True)["n"] == 6
