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
# Datos ficticios para demostración (direcciones inventadas).
PUNTOS_DEMO = [
    ("Punto Verde del Parque (demo)", "Calle Ficticia 101", "Miraflores", ["Papel", "Cartón", "Plástico"],
     {1: ("08:00", "17:00"), 3: ("08:00", "17:00"), 5: ("08:00", "17:00")}),
    ("Centro de Acopio Municipal (demo)", "Av. de Ejemplo 230", "San Isidro", ["Vidrio", "Metal", "Papel"],
     {2: ("09:00", "18:00"), 4: ("09:00", "18:00"), 6: ("09:00", "13:00")}),
    ("Eco Estación Lince (demo)", "Jr. Imaginario 45", "Lince", ["Plástico", "Vidrio", "Electrónicos"],
     {1: ("10:00", "16:00"), 2: ("10:00", "16:00"), 3: ("10:00", "16:00")}),
    ("Reciclaje Comunitario Surquillo (demo)", "Pasaje Modelo 12", "Surquillo", ["Cartón", "Metal"],
     {6: ("08:00", "12:00"), 7: ("08:00", "12:00")}),
    ("Acopio Electrónico San Borja (demo)", "Av. Supuesta 890", "San Borja", ["Electrónicos", "Metal"],
     {1: ("09:00", "17:00"), 4: ("09:00", "17:00")}),
    ("Punto Limpio Surco (demo)", "Calle Inventada 77", "Santiago de Surco", ["Papel", "Cartón", "Plástico", "Vidrio"],
     {1: ("07:00", "15:00"), 2: ("07:00", "15:00"), 3: ("07:00", "15:00"), 4: ("07:00", "15:00"), 5: ("07:00", "15:00")}),
]


def crear_datos_demo():
    """Carga puntos de acopio ficticios si SEED_DEMO está activo y aún no hay puntos."""
    if not current_app.config.get("SEED_DEMO"):
        return
    bloqueo = db.query("SELECT GET_LOCK('reciclared_demo', 10) AS ok", uno=True)
    try:
        if not bloqueo or not bloqueo["ok"] or db.query("SELECT id FROM puntos_acopio LIMIT 1", uno=True):
            return
        materiales = {fila["nombre"]: fila["id"] for fila in db.query("SELECT id, nombre FROM materiales")}
        for nombre, direccion, distrito, recibe, horario in PUNTOS_DEMO:
            _, punto_id = db.execute("INSERT INTO puntos_acopio (nombre, direccion, distrito) VALUES (%s, %s, %s)",
                                     (nombre, direccion, distrito))
            for material in recibe:
                db.execute("INSERT IGNORE INTO punto_material (punto_id, material_id) VALUES (%s, %s)",
                           (punto_id, materiales[material]))
            for dia, (apertura, cierre) in horario.items():
                db.execute("INSERT IGNORE INTO horarios (punto_id, dia, apertura, cierre) VALUES (%s, %s, %s, %s)",
                           (punto_id, dia, apertura, cierre))
    finally:
        db.query("SELECT RELEASE_LOCK('reciclared_demo') AS ok")
# [semillas]
