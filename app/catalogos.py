"""Catálogos y validaciones compartidas."""
import re

DISTRITOS = [
    "Barranco", "Breña", "Callao", "Chorrillos", "Jesús María", "La Molina", "La Victoria", "Lince",
    "Los Olivos", "Magdalena del Mar", "Miraflores", "Pueblo Libre", "San Borja", "San Isidro",
    "San Juan de Lurigancho", "San Miguel", "Santiago de Surco", "Surquillo",
]
OPCIONES_DISTRITO = [(d, d) for d in DISTRITOS]
ROLES_REGISTRO = ("ciudadano", "recolector")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
TELEFONO_RE = re.compile(r"^\+?\d{7,15}$")
# [catalogos]
