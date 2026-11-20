"""Directorio público de puntos de acopio con búsqueda por material y distrito."""
from flask import Blueprint, abort, render_template, request

from .. import db
from ..catalogos import DIAS, DISTRITOS, OPCIONES_DISTRITO
# [imports]

bp = Blueprint("directorio", __name__, url_prefix="/puntos")

# Consulta fija con parámetros opcionales: el texto SQL nunca se arma con datos del usuario.
CONSULTA_BUSQUEDA = (
    "SELECT p.id, p.nombre, p.direccion, p.distrito, "
    "GROUP_CONCAT(m.nombre ORDER BY m.nombre SEPARATOR ', ') AS materiales "
    "FROM puntos_acopio p "
    "LEFT JOIN punto_material pm ON pm.punto_id = p.id "
    "LEFT JOIN materiales m ON m.id = pm.material_id "
    "WHERE p.activo = 1 "
    "AND (%s = '' OR p.distrito = %s) "
    "AND (%s = 0 OR EXISTS (SELECT 1 FROM punto_material f WHERE f.punto_id = p.id AND f.material_id = %s)) "
    "GROUP BY p.id, p.nombre, p.direccion, p.distrito "
    "ORDER BY p.distrito, p.nombre"
)


@bp.route("/")
def listado():
    distrito = request.args.get("distrito", "").strip()
    if distrito not in DISTRITOS:
        distrito = ""
    material = request.args.get("material", "").strip()
    material_id = int(material) if material.isdigit() else 0
    puntos = db.query(CONSULTA_BUSQUEDA, (distrito, distrito, material_id, material_id))
    materiales = [(fila["id"], fila["nombre"]) for fila in db.query("SELECT id, nombre FROM materiales ORDER BY nombre")]
    return render_template("directorio/listado.html", puntos=puntos, materiales=materiales, distritos=OPCIONES_DISTRITO,
                           distrito=distrito, material=str(material_id or ""), filtrando=bool(distrito or material_id))
@bp.route("/<int:punto_id>")
def detalle(punto_id):
    punto = db.query("SELECT id, nombre, direccion, distrito FROM puntos_acopio WHERE id = %s AND activo = 1",
                     (punto_id,), uno=True)
    if punto is None:
        abort(404)
    materiales = db.query(
        "SELECT m.nombre FROM punto_material pm JOIN materiales m ON m.id = pm.material_id "
        "WHERE pm.punto_id = %s ORDER BY m.nombre", (punto_id,))
    horarios = {fila["dia"]: fila for fila in db.query(
        "SELECT dia, apertura, cierre FROM horarios WHERE punto_id = %s ORDER BY dia", (punto_id,))}
    return render_template("directorio/detalle.html", punto=punto, materiales=materiales, horarios=horarios, dias=DIAS)
# [rutas]
