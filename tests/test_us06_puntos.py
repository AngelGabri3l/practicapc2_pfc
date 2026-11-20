"""US-06 · Registrar punto de acopio."""
DATOS = {"nombre": "Centro de acopio del parque", "direccion": "Calle Ficticia 123", "distrito": "Lince"}


def test_ca1_alta_valida_queda_activa(entrar_como, post, consultar):
    admin, _ = entrar_como("admin")
    respuesta = post(admin, "/admin/puntos/nuevo", DATOS)
    assert respuesta.status_code == 302
    punto = consultar("SELECT nombre, distrito, activo FROM puntos_acopio", uno=True)
    assert punto == {"nombre": "Centro de acopio del parque", "distrito": "Lince", "activo": 1}


def test_ca2_faltan_nombre_o_distrito(entrar_como, post, consultar):
    admin, _ = entrar_como("admin")
    for faltante in ("nombre", "distrito"):
        respuesta = post(admin, "/admin/puntos/nuevo", {**DATOS, faltante: ""})
        assert respuesta.status_code == 422
    assert consultar("SELECT COUNT(*) AS n FROM puntos_acopio", uno=True)["n"] == 0


def test_ca3_ciudadano_no_puede_registrar_puntos(entrar_como, post, consultar):
    ciudadano, _ = entrar_como("ciudadano")
    assert post(ciudadano, "/admin/puntos/nuevo", DATOS).status_code == 403
    assert consultar("SELECT COUNT(*) AS n FROM puntos_acopio", uno=True)["n"] == 0
