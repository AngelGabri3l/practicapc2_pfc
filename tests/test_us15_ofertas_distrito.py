"""US-15 · Ofertas disponibles de mi distrito."""


def test_ca1_veo_solo_las_disponibles_de_mi_distrito(entrar_como, crear_oferta, crear_usuario):
    recolector, _ = entrar_como("recolector", distrito="Miraflores")
    ciudadano_id = crear_usuario("ana@example.com")
    crear_oferta(ciudadano_id, material="Vidrio", distrito="Miraflores")
    crear_oferta(ciudadano_id, material="Metal", distrito="Lince")
    crear_oferta(ciudadano_id, material="Papel", distrito="Miraflores", estado="Cancelada")
    html = recolector.get("/recolector/ofertas").get_data(as_text=True)
    assert "Vidrio" in html
    assert "Metal" not in html and "Papel" not in html


def test_ca2_la_direccion_exacta_no_se_muestra(entrar_como, crear_oferta, crear_usuario):
    recolector, _ = entrar_como("recolector")
    crear_oferta(crear_usuario("ana@example.com"), direccion="Calle Secreta 999")
    assert "Calle Secreta 999" not in recolector.get("/recolector/ofertas").get_data(as_text=True)


def test_ca3_un_ciudadano_no_entra(entrar_como):
    ciudadano, _ = entrar_como("ciudadano")
    assert ciudadano.get("/recolector/ofertas").status_code == 403


def test_ca4_sin_ofertas_se_muestra_el_aviso(entrar_como):
    recolector, _ = entrar_como("recolector")
    assert "No hay ofertas disponibles" in recolector.get("/recolector/ofertas").get_data(as_text=True)
