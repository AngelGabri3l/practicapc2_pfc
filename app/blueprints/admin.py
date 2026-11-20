"""Administración: catálogo de materiales y puntos de acopio (solo rol admin)."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from pymysql.err import IntegrityError

from .. import db
from ..security import rol_requerido
# [imports]

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/")
@rol_requerido("admin")
def inicio():
    return render_template("admin/inicio.html")
@bp.route("/materiales", methods=["GET", "POST"])
@rol_requerido("admin")
def materiales():
    nombre, error = "", None
    if request.method == "POST":
        nombre = " ".join(request.form.get("nombre", "").split())
        if not 2 <= len(nombre) <= 40:
            error = "Escribe un nombre de 2 a 40 caracteres."
        elif db.query("SELECT id FROM materiales WHERE LOWER(nombre) = LOWER(%s)", (nombre,), uno=True):
            error = "Ese material ya existe en el catálogo."
        else:
            try:
                db.execute("INSERT INTO materiales (nombre) VALUES (%s)", (nombre,))
            except IntegrityError:
                error = "Ese material ya existe en el catálogo."
            else:
                flash(f"Agregaste «{nombre}» al catálogo.", "exito")
                return redirect(url_for("admin.materiales"))
    lista = db.query("SELECT id, nombre FROM materiales ORDER BY nombre")
    return render_template("admin/materiales.html", materiales=lista, nombre=nombre, error=error), (422 if error else 200)
# [rutas]
