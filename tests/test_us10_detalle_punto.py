"""US-10 · Detalle de un punto."""


def test_ca1_detalle_muestra_direccion_materiales_y_horario(app, client, crear_punto, consultar):
    from app import db as bd
    punto = crear_punto("Centro del parque", "Calle Ficticia 123", "Lince")
    vidrio = consultar("SELECT id FROM materiales WHERE nombre = 'Vidrio'", uno=True)["id"]
    with app.app_context():
        bd.execute("INSERT INTO punto_material (punto_id, material_id) VALUES (%s, %s)", (punto, vidrio))
        bd.execute("INSERT INTO horarios (punto_id, dia, apertura, cierre) VALUES (%s, 1, '08:00', '17:00')", (punto,))
    html = client.get(f"/puntos/{punto}").get_data(as_text=True)
    for texto in ("Calle Ficticia 123", "Lince", "Vidrio", "Lunes", "08:00 a 17:00"):
        assert texto in html


def test_ca2_sin_horario_se_indica(client, crear_punto):
    punto = crear_punto()
    assert "Horario no informado" in client.get(f"/puntos/{punto}").get_data(as_text=True)


def test_ca3_punto_inexistente_da_404(client):
    assert client.get("/puntos/999999").status_code == 404


def test_punto_desactivado_no_esta_disponible(client, crear_punto):
    assert client.get(f"/puntos/{crear_punto(activo=0)}").status_code == 404
