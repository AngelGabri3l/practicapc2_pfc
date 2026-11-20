"""US-13 · Mis ofertas y su estado."""


def test_ca1_veo_mis_ofertas_con_su_estado(entrar_como, crear_oferta):
    ciudadano, usuario_id = entrar_como("ciudadano")
    crear_oferta(usuario_id, material="Vidrio", estado="Disponible")
    crear_oferta(usuario_id, material="Papel", estado="Recogida")
    html = ciudadano.get("/ofertas/mis").get_data(as_text=True)
    assert "Vidrio" in html and "Disponible" in html
    assert "Papel" in html and "Recogida" in html


def test_ca2_no_veo_ofertas_de_otros(entrar_como, crear_oferta, crear_usuario):
    ciudadano, _ = entrar_como("ciudadano")
    otro_id = crear_usuario("otra@example.com")
    crear_oferta(otro_id, material="Electrónicos")
    assert "Electrónicos" not in ciudadano.get("/ofertas/mis").get_data(as_text=True)


def test_ca3_sin_ofertas_se_muestra_el_aviso(entrar_como):
    ciudadano, _ = entrar_como("ciudadano")
    assert "Aún no tienes ofertas" in ciudadano.get("/ofertas/mis").get_data(as_text=True)


def test_tras_publicar_se_llega_a_mis_ofertas(entrar_como, post, consultar):
    from datetime import date, timedelta
    ciudadano, _ = entrar_como("ciudadano")
    vidrio = consultar("SELECT id FROM materiales WHERE nombre = 'Vidrio'", uno=True)["id"]
    respuesta = post(ciudadano, "/ofertas/nueva", {
        "material_id": str(vidrio), "cantidad": "1 caja", "direccion": "Calle Ficticia 742", "distrito": "Miraflores",
        "fecha": (date.today() + timedelta(days=2)).isoformat(), "hora_inicio": "10:00", "hora_fin": "12:00"})
    assert respuesta.headers["Location"].endswith("/ofertas/mis")
