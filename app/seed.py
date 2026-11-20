"""Datos iniciales: administrador desde variables de entorno."""
from flask import current_app
from werkzeug.security import generate_password_hash

from . import db
from .catalogos import DISTRITOS
# [imports]


def crear_admin_inicial():
    """Crea el administrador si ADMIN_EMAIL y ADMIN_PASSWORD están definidos y aún no existe."""
    email = (current_app.config.get("ADMIN_EMAIL") or "").strip().lower()
    password = current_app.config.get("ADMIN_PASSWORD") or ""
    if not email or not password:
        return
    if len(password) < 12:
        current_app.logger.warning("ADMIN_PASSWORD debe tener al menos 12 caracteres; no se creó el administrador.")
        return
    db.execute(
        "INSERT IGNORE INTO usuarios (nombre, email, password_hash, rol, distrito) VALUES (%s, %s, %s, 'admin', %s)",
        ("Administración", email, generate_password_hash(password), DISTRITOS[0]),
    )
# [semillas]
