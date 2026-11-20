"""US-04 · Editar mi perfil."""


def test_ca1_cambios_validos_se_guardan(entrar_como, post, consultar):
    cliente, usuario_id = entrar_como("ciudadano")
    post(cliente, "/perfil", {"nombre": "Ana María Torres", "telefono": "987654321", "distrito": "Lince"})
    fila = consultar("SELECT nombre, telefono, distrito FROM usuarios WHERE id = %s", (usuario_id,), uno=True)
    assert fila == {"nombre": "Ana María Torres", "telefono": "987654321", "distrito": "Lince"}
    assert "Lince" in cliente.get("/perfil").get_data(as_text=True)


def test_ca2_telefono_invalido_no_cambia_los_datos(entrar_como, post, consultar):
    cliente, usuario_id = entrar_como("ciudadano")
    respuesta = post(cliente, "/perfil", {"nombre": "Ana", "telefono": "abc-123", "distrito": "Lince"})
    assert respuesta.status_code == 422
    assert consultar("SELECT distrito FROM usuarios WHERE id = %s", (usuario_id,), uno=True)["distrito"] == "Miraflores"


def test_ca3_sin_sesion_redirige_al_inicio_de_sesion(client):
    respuesta = client.get("/perfil")
    assert respuesta.status_code == 302
    assert "/login" in respuesta.headers["Location"]


def test_no_se_puede_editar_el_perfil_de_otro_usuario(entrar_como, crear_usuario, post, consultar):
    cliente, _ = entrar_como("ciudadano")
    otro_id = crear_usuario("otra@example.com", nombre="Otra Persona")
    post(cliente, "/perfil", {"id": str(otro_id), "usuario_id": str(otro_id), "nombre": "Cambiado", "distrito": "Lince"})
    assert consultar("SELECT nombre FROM usuarios WHERE id = %s", (otro_id,), uno=True)["nombre"] == "Otra Persona"
