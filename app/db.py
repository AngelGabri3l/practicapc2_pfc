"""Acceso a MySQL: conexiones por petición y consultas siempre parametrizadas."""
import time
from pathlib import Path

import pymysql
from flask import current_app, g

ESQUEMA = Path(__file__).with_name("schema.sql")


def _conectar():
    c = current_app.config
    return pymysql.connect(
        host=c["DB_HOST"], port=c["DB_PORT"], user=c["DB_USER"], password=c["DB_PASSWORD"],
        database=c["DB_NAME"], charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor,
        autocommit=True, connect_timeout=5,
    )


def get_db():
    if "db" not in g:
        g.db = _conectar()
    return g.db


def close_db(_error=None):
    conexion = g.pop("db", None)
    if conexion is not None:
        conexion.close()


def query(sql, params=(), uno=False):
    with get_db().cursor() as cursor:
        cursor.execute(sql, params)
        filas = cursor.fetchall()
    if uno:
        return filas[0] if filas else None
    return filas


def execute(sql, params=()):
    """Ejecuta una sentencia y devuelve (filas_afectadas, último_id)."""
    with get_db().cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.rowcount, cursor.lastrowid


def _sentencias():
    texto = ESQUEMA.read_text(encoding="utf-8")
    sin_comentarios = "\n".join(l for l in texto.splitlines() if not l.strip().startswith("--"))
    return [s.strip() for s in sin_comentarios.split(";") if s.strip()]


def init_schema(intentos=20, espera=2):
    """Crea las tablas que falten y carga los datos semilla. Es idempotente."""
    ultimo_error = None
    for _ in range(intentos):
        try:
            for sentencia in _sentencias():
                execute(sentencia)
            return
        except pymysql.err.OperationalError as error:
            ultimo_error = error
            close_db()
            time.sleep(espera)
    raise RuntimeError(f"No se pudo preparar la base de datos: {ultimo_error}")
