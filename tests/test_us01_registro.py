"""US-01 · Registro de usuario."""
from werkzeug.security import check_password_hash

DATOS = {"nombre": "Ana Torres", "email": "ana@example.com", "password": "clave-de-prueba",
         "rol": "ciudadano", "distrito": "Miraflores", "telefono": "987654321"}


def registrar(post, client, **cambios):
    return post(client, "/registro", {**DATOS, **cambios})


def test_ca1_registro_valido_crea_la_cuenta(client, post, consultar):
    respuesta = registrar(post, client)
    assert respuesta.status_code == 302
    usuario = consultar("SELECT nombre, rol, distrito FROM usuarios WHERE email = %s", ("ana@example.com",), uno=True)
    assert usuario == {"nombre": "Ana Torres", "rol": "ciudadano", "distrito": "Miraflores"}


def test_ca2_correo_duplicado_se_rechaza(client, post, consultar):
    registrar(post, client)
    respuesta = registrar(post, client, nombre="Otra Persona", email="ANA@example.com")
    assert respuesta.status_code == 422
    assert "Ya existe una cuenta con este correo" in respuesta.get_data(as_text=True)
    assert consultar("SELECT COUNT(*) AS n FROM usuarios", uno=True)["n"] == 1


def test_ca3_contrasena_corta_se_rechaza(client, post, consultar):
    respuesta = registrar(post, client, password="corta")
    assert respuesta.status_code == 422
    assert "al menos 8 caracteres" in respuesta.get_data(as_text=True)
    assert consultar("SELECT COUNT(*) AS n FROM usuarios", uno=True)["n"] == 0


def test_ca4_contrasena_guardada_con_hash(client, post, consultar):
    registrar(post, client)
    fila = consultar("SELECT password_hash FROM usuarios WHERE email = %s", ("ana@example.com",), uno=True)
    assert fila["password_hash"] != DATOS["password"]
    assert check_password_hash(fila["password_hash"], DATOS["password"])


def test_registro_sin_token_csrf_se_rechaza(client):
    assert client.post("/registro", data=DATOS).status_code == 400
