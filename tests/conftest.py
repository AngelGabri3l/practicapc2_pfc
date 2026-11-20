"""Configuración común de las pruebas: base de datos MySQL real y utilidades."""
import os

import pytest
from werkzeug.security import generate_password_hash

os.environ.setdefault("SECRET_KEY", "pruebas")

from app import create_app  # noqa: E402
from app import db as bd  # noqa: E402


@pytest.fixture(scope="session")
def app():
    return create_app({"TESTING": True})


@pytest.fixture(autouse=True)
def base_limpia(app):
    """Vacía todas las tablas y recarga los datos semilla antes de cada prueba."""
    with app.app_context():
        conexion = bd.get_db()
        with conexion.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            cursor.execute("SHOW TABLES")
            for fila in cursor.fetchall():
                cursor.execute(f"DELETE FROM `{list(fila.values())[0]}`")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        bd.init_schema()
    yield


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def post():
    """Envía un formulario incluyendo el token CSRF de la sesión."""
    def enviar(cliente, url, datos=None, **kwargs):
        with cliente.session_transaction() as sesion:
            token = sesion.setdefault("_csrf", "token-de-prueba")
        datos = dict(datos or {})
        datos["csrf_token"] = token
        return cliente.post(url, data=datos, **kwargs)
    return enviar


@pytest.fixture
def consultar(app):
    """Consulta directa a la base para verificar resultados."""
    def ejecutar(sql, params=(), uno=False):
        with app.app_context():
            return bd.query(sql, params, uno=uno)
    return ejecutar
CLAVE_PRUEBA = "clave-de-prueba"


@pytest.fixture
def crear_usuario(app):
    """Crea un usuario directamente en la base y devuelve su id."""
    def crear(email, rol="ciudadano", distrito="Miraflores", nombre="Persona de Prueba", telefono=None):
        with app.app_context():
            _, nuevo_id = bd.execute(
                "INSERT INTO usuarios (nombre, email, password_hash, rol, distrito, telefono) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (nombre, email, generate_password_hash(CLAVE_PRUEBA), rol, distrito, telefono),
            )
        return nuevo_id
    return crear


@pytest.fixture
def iniciar_sesion(post):
    def entrar(cliente, email, clave=CLAVE_PRUEBA):
        respuesta = post(cliente, "/login", {"email": email, "password": clave})
        assert respuesta.status_code == 302, "no se pudo iniciar sesión"
        return respuesta
    return entrar
@pytest.fixture
def entrar_como(app, crear_usuario, iniciar_sesion):
    """Crea un usuario con el rol indicado, inicia sesión y devuelve (cliente, id)."""
    contador = {"n": 0}

    def entrar(rol, distrito="Miraflores", **datos):
        contador["n"] += 1
        email = datos.pop("email", f"{rol}{contador['n']}@example.com")
        usuario_id = crear_usuario(email, rol=rol, distrito=distrito, **datos)
        cliente = app.test_client()
        iniciar_sesion(cliente, email)
        return cliente, usuario_id
    return entrar


@pytest.fixture
def crear_punto(app):
    def crear(nombre="Punto de prueba", direccion="Calle Ficticia 100", distrito="Miraflores", activo=1):
        with app.app_context():
            _, punto_id = bd.execute(
                "INSERT INTO puntos_acopio (nombre, direccion, distrito, activo) VALUES (%s, %s, %s, %s)",
                (nombre, direccion, distrito, activo),
            )
        return punto_id
    return crear
@pytest.fixture
def crear_oferta(app):
    """Crea una oferta directamente en la base y devuelve su id."""
    from datetime import date, timedelta

    def crear(ciudadano_id, material="Cartón", distrito="Miraflores", estado="Disponible", recolector_id=None,
              direccion="Calle Ficticia 742"):
        manana = date.today() + timedelta(days=1)
        with app.app_context():
            material_id = bd.query("SELECT id FROM materiales WHERE nombre = %s", (material,), uno=True)["id"]
            _, oferta_id = bd.execute(
                "INSERT INTO ofertas (ciudadano_id, material_id, cantidad, direccion, distrito, fecha, hora_inicio, "
                "hora_fin, estado, recolector_id) VALUES (%s, %s, '2 bolsas', %s, %s, %s, '09:00', '12:00', %s, %s)",
                (ciudadano_id, material_id, direccion, distrito, manana, estado, recolector_id),
            )
        return oferta_id
    return crear
# [fixtures]
