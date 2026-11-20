"""US-18 · Ver quién aceptó mi oferta."""


def test_ca1_oferta_aceptada_muestra_nombre_y_telefono(entrar_como, crear_usuario, crear_oferta):
    ciudadano, ciudadano_id = entrar_como("ciudadano")
    recolector_id = crear_usuario("luis@example.com", rol="recolector", nombre="Luis Rojas", telefono="912345678")
    oferta = crear_oferta(ciudadano_id, estado="Aceptada", recolector_id=recolector_id)
    html = ciudadano.get(f"/ofertas/{oferta}").get_data(as_text=True)
    assert "Luis Rojas" in html and "912345678" in html


def test_ca2_oferta_disponible_no_muestra_datos_de_recolectores(entrar_como, crear_usuario, crear_oferta):
    ciudadano, ciudadano_id = entrar_como("ciudadano")
    crear_usuario("luis@example.com", rol="recolector", nombre="Luis Rojas", telefono="912345678")
    oferta = crear_oferta(ciudadano_id)
    html = ciudadano.get(f"/ofertas/{oferta}").get_data(as_text=True)
    assert "Luis Rojas" not in html and "912345678" not in html
    assert "Aún ningún recolector aceptó" in html


def test_ca3_oferta_de_otro_ciudadano_da_acceso_denegado(entrar_como, crear_usuario, crear_oferta):
    ciudadano, _ = entrar_como("ciudadano")
    ajena = crear_oferta(crear_usuario("otra@example.com"))
    assert ciudadano.get(f"/ofertas/{ajena}").status_code == 403
