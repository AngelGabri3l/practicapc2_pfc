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
def intentar_aceptar(conexion, oferta_id, recolector_id, distrito):
    """Acepta la oferta solo si sigue «Disponible». El UPDATE condicional es atómico:
    si dos recolectores aceptan a la vez, solo uno modifica la fila."""
    with conexion.cursor() as cursor:
        filas = cursor.execute(
            "UPDATE ofertas SET estado = 'Aceptada', recolector_id = %s, aceptada_en = NOW() "
            "WHERE id = %s AND estado = 'Disponible' AND distrito = %s",
            (recolector_id, oferta_id, distrito),
        )
    return filas == 1


CONSULTA_DETALLE = (
    "SELECT o.id, m.nombre AS material, o.cantidad, o.direccion, o.distrito, o.fecha, o.hora_inicio, o.hora_fin, "
    "o.estado, o.recolector_id, o.recogida_en, u.nombre AS ciudadano, u.telefono AS telefono_ciudadano "
    "FROM ofertas o JOIN materiales m ON m.id = o.material_id JOIN usuarios u ON u.id = o.ciudadano_id "
    "WHERE o.id = %s"
)


@bp.post("/ofertas/<int:oferta_id>/aceptar")
@rol_requerido("recolector")
def aceptar(oferta_id):
    if intentar_aceptar(db.get_db(), oferta_id, g.usuario["id"], g.usuario["distrito"]):
        flash("¡La oferta es tuya! Aquí tienes la dirección para el recojo.", "exito")
        return redirect(url_for("recolector.detalle", oferta_id=oferta_id))
    flash("Esta oferta ya no está disponible: otro recolector la tomó o fue cancelada.", "error")
    return redirect(url_for("recolector.ofertas"))


@bp.route("/ofertas/<int:oferta_id>")
@rol_requerido("recolector")
def detalle(oferta_id):
    oferta = db.query(CONSULTA_DETALLE, (oferta_id,), uno=True)
    if oferta is None:
        abort(404)
    if oferta["recolector_id"] != g.usuario["id"]:
        abort(403)
    return render_template("recolector/detalle.html", oferta=oferta)


@bp.route("/recojos")
@rol_requerido("recolector")
def recojos():
    lista = db.query(
        "SELECT o.id, m.nombre AS material, o.cantidad, o.direccion, o.fecha, o.hora_inicio, o.hora_fin, o.estado "
        "FROM ofertas o JOIN materiales m ON m.id = o.material_id "
        "WHERE o.recolector_id = %s ORDER BY FIELD(o.estado, 'Aceptada', 'Recogida'), o.fecha, o.hora_inicio",
        (g.usuario["id"],),
    )
    return render_template("recolector/recojos.html", recojos=lista)
# [rutas]
