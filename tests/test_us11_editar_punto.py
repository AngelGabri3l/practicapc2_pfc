"""US-11 · Editar o desactivar un punto."""


def test_ca1_los_cambios_se_guardan(entrar_como, post, consultar, crear_punto):
    admin, _ = entrar_como("admin")
    punto = crear_punto()
    post(admin, f"/admin/puntos/{punto}/editar", {"nombre": "Punto renovado", "direccion": "Av. Nueva 500", "distrito": "Barranco"})
    fila = consultar("SELECT nombre, direccion, distrito FROM puntos_acopio WHERE id = %s", (punto,), uno=True)
    assert fila == {"nombre": "Punto renovado", "direccion": "Av. Nueva 500", "distrito": "Barranco"}


def test_ca2_punto_desactivado_no_aparece_en_el_directorio(client, entrar_como, post, consultar, crear_punto):
    admin, _ = entrar_como("admin")
    punto = crear_punto("Punto a desactivar")
    post(admin, f"/admin/puntos/{punto}/estado", {"activo": "0"})
    assert consultar("SELECT activo FROM puntos_acopio WHERE id = %s", (punto,), uno=True)["activo"] == 0
    assert "Punto a desactivar" not in client.get("/puntos/").get_data(as_text=True)


def test_ca3_un_ciudadano_no_puede_editar(entrar_como, post, crear_punto):
    ciudadano, _ = entrar_como("ciudadano")
    punto = crear_punto()
    assert post(ciudadano, f"/admin/puntos/{punto}/editar", {"nombre": "X", "direccion": "Y", "distrito": "Lince"}).status_code == 403
    assert post(ciudadano, f"/admin/puntos/{punto}/estado", {"activo": "0"}).status_code == 403
