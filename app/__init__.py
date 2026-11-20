"""Fábrica de la aplicación ReciclaRed."""
from flask import Flask, render_template

from . import db, filtros, seed
from .config import Config
from .security import cargar_usuario, csrf_token, validar_csrf
# [imports]

CSP = ("default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; "
       "object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'")

ERRORES = {
    400: ("Solicitud inválida", "El formulario expiró o no es válido. Vuelve a intentarlo."),
    403: ("Acceso denegado", "No tienes permiso para ver esta página."),
    404: ("Página no encontrada", "Lo que buscas no existe o ya no está disponible."),
    500: ("Algo salió mal", "Tuvimos un problema. Inténtalo de nuevo en unos minutos."),
}


def _registrar_errores(app):
    for codigo, (titulo, mensaje) in ERRORES.items():
        def manejador(_error, codigo=codigo, titulo=titulo, mensaje=mensaje):
            return render_template("errores/error.html", codigo=codigo, titulo=titulo, mensaje=mensaje), codigo
        app.register_error_handler(codigo, manejador)


def create_app(ajustes=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if ajustes:
        app.config.update(ajustes)
    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("Falta la variable de entorno SECRET_KEY")

    app.teardown_appcontext(db.close_db)
    app.before_request(validar_csrf)
    app.before_request(cargar_usuario)
    # [antes-de-peticion]
    app.jinja_env.globals["csrf_token"] = csrf_token
    filtros.registrar(app)

    from .blueprints import main
    app.register_blueprint(main.bp)
    from .blueprints import auth
    app.register_blueprint(auth.bp)
    from .blueprints import admin
    app.register_blueprint(admin.bp)
    from .blueprints import ofertas
    app.register_blueprint(ofertas.bp)
    # [blueprints]

    @app.after_request
    def cabeceras_de_seguridad(respuesta):
        respuesta.headers.setdefault("Content-Security-Policy", CSP)
        respuesta.headers.setdefault("X-Content-Type-Options", "nosniff")
        respuesta.headers.setdefault("X-Frame-Options", "DENY")
        respuesta.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        respuesta.headers.setdefault("Permissions-Policy", "geolocation=(), camera=(), microphone=()")
        return respuesta

    _registrar_errores(app)

    with app.app_context():
        db.init_schema()
        seed.crear_admin_inicial()
        # [semillas]
    return app
