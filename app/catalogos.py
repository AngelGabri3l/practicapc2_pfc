"""Catálogos y validaciones compartidas."""
import re
from datetime import date, datetime

DISTRITOS = [
    "Barranco", "Breña", "Callao", "Chorrillos", "Jesús María", "La Molina", "La Victoria", "Lince",
    "Los Olivos", "Magdalena del Mar", "Miraflores", "Pueblo Libre", "San Borja", "San Isidro",
    "San Juan de Lurigancho", "San Miguel", "Santiago de Surco", "Surquillo",
]
OPCIONES_DISTRITO = [(d, d) for d in DISTRITOS]
ROLES_REGISTRO = ("ciudadano", "recolector")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
TELEFONO_RE = re.compile(r"^\+?\d{7,15}$")
def leer_hora(texto):
    """Convierte 'HH:MM' en un objeto time; devuelve None si no es válido."""
    try:
        return datetime.strptime(texto, "%H:%M").time()
    except ValueError:
        return None


def leer_fecha(texto):
    try:
        return date.fromisoformat(texto)
    except ValueError:
        return None
# [catalogos]
