"""Configuración leída de variables de entorno (nunca de valores fijos en el código)."""
import os
from datetime import timedelta


def _booleano(nombre, defecto="false"):
    return os.environ.get(nombre, defecto).strip().lower() in ("1", "true", "si", "sí", "yes")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.environ.get("DB_PORT", "3306"))
    DB_NAME = os.environ.get("DB_NAME", "")
    DB_USER = os.environ.get("DB_USER", "")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _booleano("SESSION_COOKIE_SECURE")
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    MAX_CONTENT_LENGTH = 1024 * 1024
    # [config]
