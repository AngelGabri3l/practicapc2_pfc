"""Portada, panel y verificación de salud."""
from flask import Blueprint, jsonify, render_template

from .. import db
from ..catalogos import OPCIONES_DISTRITO
from ..security import login_requerido
# [imports]

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    materiales = [(fila["id"], fila["nombre"]) for fila in db.query("SELECT id, nombre FROM materiales ORDER BY nombre")]
    return render_template("index.html", materiales=materiales, distritos=OPCIONES_DISTRITO)


@bp.route("/health")
def health():
    try:
        db.query("SELECT 1")
    except Exception:  # cualquier fallo de la base se informa como 503
        return jsonify(status="error", db="down"), 503
    return jsonify(status="ok", db="ok")
@bp.route("/inicio")
@login_requerido
def inicio():
    return render_template("inicio.html")
# [rutas]
