"""Configuración común de las pruebas: base de datos MySQL real y utilidades."""
import os

import pytest

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
# [fixtures]
