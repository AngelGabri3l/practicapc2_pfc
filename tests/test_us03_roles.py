"""US-03 · Acceso según rol."""


def test_ca1_ciudadano_no_entra_a_administracion(client, crear_usuario, iniciar_sesion):
    crear_usuario("ana@example.com", rol="ciudadano")
    iniciar_sesion(client, "ana@example.com")
    respuesta = client.get("/admin/")
    assert respuesta.status_code == 403
    assert "Acceso denegado" in respuesta.get_data(as_text=True)


def test_ca2_recolector_no_entra_a_administracion(client, crear_usuario, iniciar_sesion):
    crear_usuario("luis@example.com", rol="recolector")
    iniciar_sesion(client, "luis@example.com")
    assert client.get("/admin/").status_code == 403


def test_ca3_sin_sesion_redirige_al_inicio_de_sesion(client):
    respuesta = client.get("/admin/")
    assert respuesta.status_code == 302
    assert "/login" in respuesta.headers["Location"]


def test_ca4_administrador_accede_con_normalidad(client, crear_usuario, iniciar_sesion):
    crear_usuario("admin@example.com", rol="admin")
    iniciar_sesion(client, "admin@example.com")
    respuesta = client.get("/admin/")
    assert respuesta.status_code == 200
    assert "Panel de administración" in respuesta.get_data(as_text=True)


def test_administrador_inicial_se_crea_desde_variables_de_entorno(app, consultar):
    from app.seed import crear_admin_inicial
    app.config.update(ADMIN_EMAIL="jefa@example.com", ADMIN_PASSWORD="clave-larga-de-prueba")
    try:
        with app.app_context():
            crear_admin_inicial()
            crear_admin_inicial()  # idempotente: no duplica
    finally:
        app.config.update(ADMIN_EMAIL="", ADMIN_PASSWORD="")
    filas = consultar("SELECT rol FROM usuarios WHERE email = %s", ("jefa@example.com",))
    assert filas == [{"rol": "admin"}]
