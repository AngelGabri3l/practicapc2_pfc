"""Registro, inicio de sesión y perfil de usuario."""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from pymysql.err import IntegrityError
from werkzeug.security import generate_password_hash

from .. import db
from ..catalogos import DISTRITOS, EMAIL_RE, OPCIONES_DISTRITO, ROLES_REGISTRO, TELEFONO_RE
# [imports]

bp = Blueprint("auth", __name__)


def _validar_registro(datos, password):
    errores = {}
    if not 2 <= len(datos["nombre"]) <= 100:
        errores["nombre"] = "Escribe tu nombre (de 2 a 100 caracteres)."
    if not EMAIL_RE.match(datos["email"]):
        errores["email"] = "Escribe un correo válido."
    if len(password) < 8:
        errores["password"] = "La contraseña debe tener al menos 8 caracteres."
    if datos["rol"] not in ROLES_REGISTRO:
        errores["rol"] = "Elige si entregas reciclables o si los recolectas."
    if datos["distrito"] not in DISTRITOS:
        errores["distrito"] = "Elige tu distrito."
    if datos["telefono"] and not TELEFONO_RE.match(datos["telefono"]):
        errores["telefono"] = "Usa solo números (de 7 a 15 dígitos)."
    return errores


@bp.route("/registro", methods=["GET", "POST"])
def registro():
    datos = {"nombre": "", "email": "", "rol": "ciudadano", "distrito": "", "telefono": ""}
    errores = {}
    if request.method == "POST":
        datos = {campo: request.form.get(campo, "").strip() for campo in datos}
        datos["email"] = datos["email"].lower()
        password = request.form.get("password", "")
        errores = _validar_registro(datos, password)
        if not errores and db.query("SELECT id FROM usuarios WHERE email = %s", (datos["email"],), uno=True):
            errores["email"] = "Ya existe una cuenta con este correo."
        if not errores:
            try:
                db.execute(
                    "INSERT INTO usuarios (nombre, email, password_hash, rol, distrito, telefono) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    (datos["nombre"], datos["email"], generate_password_hash(password), datos["rol"],
                     datos["distrito"], datos["telefono"] or None),
                )
            except IntegrityError:
                errores["email"] = "Ya existe una cuenta con este correo."
            else:
                flash("¡Tu cuenta está lista! Ya puedes iniciar sesión.", "exito")
                return redirect(url_for("main.index"))
    codigo = 422 if errores else 200
    return render_template("auth/registro.html", datos=datos, errores=errores, distritos=OPCIONES_DISTRITO), codigo
# [rutas]
