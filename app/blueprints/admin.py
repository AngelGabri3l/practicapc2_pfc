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
# [rutas]
