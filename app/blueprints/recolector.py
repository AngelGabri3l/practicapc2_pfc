"""Ofertas para recolectores: ver, aceptar y cerrar recojos."""
from flask import Blueprint, abort, flash, g, redirect, render_template, url_for

from .. import db
from ..security import rol_requerido
# [imports]

bp = Blueprint("recolector", __name__, url_prefix="/recolector")


@bp.route("/ofertas")
@rol_requerido("recolector")
def ofertas():
    # Privacidad: la dirección exacta no se consulta aquí; solo se revela a quien acepta la oferta.
    lista = db.query(
        "SELECT o.id, m.nombre AS material, o.cantidad, o.distrito, o.fecha, o.hora_inicio, o.hora_fin "
        "FROM ofertas o JOIN materiales m ON m.id = o.material_id "
        "WHERE o.estado = 'Disponible' AND o.distrito = %s ORDER BY o.fecha, o.hora_inicio",
        (g.usuario["distrito"],),
    )
    return render_template("recolector/ofertas.html", ofertas=lista)
# [rutas]
