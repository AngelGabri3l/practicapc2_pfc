"""Protección CSRF, sesión del usuario y control de acceso."""
import secrets

from flask import abort, request, session
from functools import wraps

from flask import flash, g, redirect, url_for

from . import db
# [imports]

CAMPO_CSRF = "csrf_token"


def csrf_token():
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_urlsafe(32)
    return session["_csrf"]


def validar_csrf():
    """Rechaza cualquier POST sin el token de la sesión (protección CSRF)."""
    if request.method != "POST":
        return
    esperado = session.get("_csrf")
    enviado = request.form.get(CAMPO_CSRF, "")
    if not esperado or not secrets.compare_digest(enviado, esperado):
        abort(400)
def cargar_usuario():
    """Carga en g.usuario al usuario de la sesión actual (o None)."""
    g.usuario = None
    usuario_id = session.get("usuario_id")
    if usuario_id is not None:
        g.usuario = db.query(
            "SELECT id, nombre, email, rol, distrito, telefono FROM usuarios WHERE id = %s", (usuario_id,), uno=True
        )
        if g.usuario is None:
            session.clear()


def login_requerido(vista):
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if g.get("usuario") is None:
            flash("Inicia sesión para continuar.", "info")
            return redirect(url_for("auth.login", next=request.path))
        return vista(*args, **kwargs)
    return envoltura
def rol_requerido(*roles):
    """Exige sesión iniciada y uno de los roles indicados; si no, responde 403."""
    def decorador(vista):
        @wraps(vista)
        @login_requerido
        def envoltura(*args, **kwargs):
            if g.usuario["rol"] not in roles:
                abort(403)
            return vista(*args, **kwargs)
        return envoltura
    return decorador
# [sesion]
