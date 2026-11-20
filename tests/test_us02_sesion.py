"""US-02 · Inicio y cierre de sesión."""
import pytest


@pytest.mark.parametrize("rol, panel", [("ciudadano", "Panel del ciudadano"),
                                        ("recolector", "Panel del recolector"),
                                        ("admin", "Panel de administración")])
def test_ca1_credenciales_correctas_llevan_al_panel_del_rol(client, crear_usuario, iniciar_sesion, rol, panel):
    crear_usuario("persona@example.com", rol=rol)
    respuesta = iniciar_sesion(client, "persona@example.com")
    assert respuesta.headers["Location"].endswith("/inicio")
    assert panel in client.get("/inicio").get_data(as_text=True)


def test_ca2_error_generico_no_revela_el_dato_incorrecto(client, post, crear_usuario):
    crear_usuario("ana@example.com")
    clave_mala = post(client, "/login", {"email": "ana@example.com", "password": "no-es-la-clave"})
    correo_malo = post(client, "/login", {"email": "nadie@example.com", "password": "no-es-la-clave"})
    for respuesta in (clave_mala, correo_malo):
        assert respuesta.status_code == 401
        assert "Correo o contraseña incorrectos." in respuesta.get_data(as_text=True)


def test_ca3_tras_cerrar_sesion_no_se_abren_paginas_privadas(client, post, crear_usuario, iniciar_sesion):
    crear_usuario("ana@example.com")
    iniciar_sesion(client, "ana@example.com")
    assert client.get("/inicio").status_code == 200
    post(client, "/logout")
    respuesta = client.get("/inicio")
    assert respuesta.status_code == 302
    assert "/login" in respuesta.headers["Location"]


def test_registro_completo_permite_iniciar_sesion(client, post):
    """Completa el criterio 1 de US-01: tras registrarse, la persona puede iniciar sesión."""
    post(client, "/registro", {"nombre": "Luis Rojas", "email": "luis@example.com", "password": "clave-de-prueba",
                               "rol": "recolector", "distrito": "Lince", "telefono": ""})
    respuesta = post(client, "/login", {"email": "luis@example.com", "password": "clave-de-prueba"})
    assert respuesta.status_code == 302


def test_redireccion_externa_tras_login_se_ignora(client, post, crear_usuario):
    crear_usuario("ana@example.com")
    respuesta = post(client, "/login?next=//sitio-malicioso.example", {"email": "ana@example.com", "password": "clave-de-prueba"})
    assert respuesta.headers["Location"].endswith("/inicio")
