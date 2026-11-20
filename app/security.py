"""Protección CSRF, sesión del usuario y control de acceso."""
import secrets

from flask import abort, request, session
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
# [sesion]
