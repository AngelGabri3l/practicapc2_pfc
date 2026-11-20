"""Administración: catálogo de materiales y puntos de acopio (solo rol admin)."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from pymysql.err import IntegrityError

from .. import db
from ..security import rol_requerido
from ..catalogos import DISTRITOS, OPCIONES_DISTRITO
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
def _datos_punto():
    return {campo: " ".join(request.form.get(campo, "").split()) for campo in ("nombre", "direccion", "distrito")}


def _validar_punto(datos):
    errores = {}
    if not 3 <= len(datos["nombre"]) <= 120:
        errores["nombre"] = "Escribe el nombre del punto (de 3 a 120 caracteres)."
    if not 5 <= len(datos["direccion"]) <= 200:
        errores["direccion"] = "Escribe la dirección (de 5 a 200 caracteres)."
    if datos["distrito"] not in DISTRITOS:
        errores["distrito"] = "Elige el distrito."
    return errores


@bp.route("/puntos")
@rol_requerido("admin")
def puntos():
    lista = db.query("SELECT id, nombre, direccion, distrito, activo FROM puntos_acopio ORDER BY activo DESC, nombre")
    return render_template("admin/puntos.html", puntos=lista)


@bp.route("/puntos/nuevo", methods=["GET", "POST"])
@rol_requerido("admin")
def punto_nuevo():
    datos, errores = {"nombre": "", "direccion": "", "distrito": ""}, {}
    if request.method == "POST":
        datos = _datos_punto()
        errores = _validar_punto(datos)
        if not errores:
            _, punto_id = db.execute(
                "INSERT INTO puntos_acopio (nombre, direccion, distrito) VALUES (%s, %s, %s)",
                (datos["nombre"], datos["direccion"], datos["distrito"]),
            )
            flash(f"Registraste «{datos['nombre']}» en el directorio.", "exito")
            return redirect(url_for("admin.puntos"))
    return render_template("admin/punto_form.html", datos=datos, errores=errores, distritos=OPCIONES_DISTRITO,
                           modo="nuevo"), (422 if errores else 200)
# [rutas]
