"""US-14 · Cancelar una oferta."""


def test_ca1_oferta_disponible_se_cancela_y_deja_de_verse(entrar_como, post, consultar, crear_oferta):
    ciudadano, ciudadano_id = entrar_como("ciudadano")
    recolector, _ = entrar_como("recolector")
    oferta = crear_oferta(ciudadano_id, material="Vidrio")
    post(ciudadano, f"/ofertas/{oferta}/cancelar")
    assert consultar("SELECT estado FROM ofertas WHERE id = %s", (oferta,), uno=True)["estado"] == "Cancelada"
    assert "Vidrio" not in recolector.get("/recolector/ofertas").get_data(as_text=True)


def test_ca2_oferta_aceptada_no_se_puede_cancelar(entrar_como, post, consultar, crear_oferta, crear_usuario):
    ciudadano, ciudadano_id = entrar_como("ciudadano")
    recolector_id = crear_usuario("luis@example.com", rol="recolector")
    oferta = crear_oferta(ciudadano_id, estado="Aceptada", recolector_id=recolector_id)
    respuesta = post(ciudadano, f"/ofertas/{oferta}/cancelar", follow_redirects=True)
    assert "Solo puedes cancelar ofertas disponibles" in respuesta.get_data(as_text=True)
    assert consultar("SELECT estado FROM ofertas WHERE id = %s", (oferta,), uno=True)["estado"] == "Aceptada"


def test_ca3_oferta_de_otro_ciudadano_da_acceso_denegado(entrar_como, post, consultar, crear_oferta, crear_usuario):
    ciudadano, _ = entrar_como("ciudadano")
    ajena = crear_oferta(crear_usuario("otra@example.com"))
    assert post(ciudadano, f"/ofertas/{ajena}/cancelar").status_code == 403
    assert consultar("SELECT estado FROM ofertas WHERE id = %s", (ajena,), uno=True)["estado"] == "Disponible"
