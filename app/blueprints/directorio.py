"""Directorio público de puntos de acopio."""
from flask import Blueprint, abort, render_template, request

from .. import db
# [imports]

bp = Blueprint("directorio", __name__, url_prefix="/puntos")

CONSULTA_LISTADO = (
    "SELECT p.id, p.nombre, p.direccion, p.distrito, "
    "GROUP_CONCAT(m.nombre ORDER BY m.nombre SEPARATOR ', ') AS materiales "
    "FROM puntos_acopio p "
    "LEFT JOIN punto_material pm ON pm.punto_id = p.id "
    "LEFT JOIN materiales m ON m.id = pm.material_id "
    "WHERE p.activo = 1 "
    "GROUP BY p.id, p.nombre, p.direccion, p.distrito "
    "ORDER BY p.distrito, p.nombre"
)


@bp.route("/")
def listado():
    return render_template("directorio/listado.html", puntos=db.query(CONSULTA_LISTADO))
# [rutas]
