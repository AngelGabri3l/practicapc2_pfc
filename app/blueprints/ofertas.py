"""Ofertas de material reciclable publicadas por los ciudadanos."""
from datetime import date, timedelta

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from .. import db
from ..catalogos import DISTRITOS, OPCIONES_DISTRITO, leer_fecha, leer_hora
from ..security import rol_requerido
# [imports]

bp = Blueprint("ofertas", __name__, url_prefix="/ofertas")


def _validar_oferta(datos, ids_materiales):
    errores = {}
    if datos["material_id"] not in ids_materiales:
        errores["material_id"] = "Elige el material."
    if not 2 <= len(datos["cantidad"]) <= 60:
        errores["cantidad"] = "Indica la cantidad aproximada (por ejemplo, 2 bolsas)."
    if not 5 <= len(datos["direccion"]) <= 200:
        errores["direccion"] = "Escribe la dirección de recojo."
    if datos["distrito"] not in DISTRITOS:
        errores["distrito"] = "Elige el distrito."
    dia = leer_fecha(datos["fecha"])
    if dia is None:
        errores["fecha"] = "Elige la fecha de recojo."
    elif dia < date.today() - timedelta(days=1):  # tolera la diferencia horaria del servidor
        errores["fecha"] = "La fecha no puede estar en el pasado."
    inicio, fin = leer_hora(datos["hora_inicio"]), leer_hora(datos["hora_fin"])
    if inicio is None or fin is None:
        errores["hora_fin"] = "Indica la hora de inicio y la de fin."
    elif fin <= inicio:
        errores["hora_fin"] = "La hora de fin debe ser posterior a la de inicio."
    return errores


@bp.route("/nueva", methods=["GET", "POST"])
@rol_requerido("ciudadano")
def nueva():
    campos = ("material_id", "cantidad", "direccion", "distrito", "fecha", "hora_inicio", "hora_fin")
    datos = dict.fromkeys(campos, "")
    datos["distrito"] = g.usuario["distrito"]
    errores = {}
    materiales = db.query("SELECT id, nombre FROM materiales ORDER BY nombre")
    if request.method == "POST":
        datos = {campo: " ".join(request.form.get(campo, "").split()) for campo in campos}
        errores = _validar_oferta(datos, {str(material["id"]) for material in materiales})
        if not errores:
            db.execute(
                "INSERT INTO ofertas (ciudadano_id, material_id, cantidad, direccion, distrito, fecha, hora_inicio, hora_fin) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (g.usuario["id"], int(datos["material_id"]), datos["cantidad"], datos["direccion"], datos["distrito"],
                 datos["fecha"], datos["hora_inicio"], datos["hora_fin"]),
            )
            flash("¡Publicado! Los recolectores de tu distrito ya pueden ver tu oferta.", "exito")
            return redirect(url_for("main.inicio"))
    opciones = [(material["id"], material["nombre"]) for material in materiales]
    return render_template("ofertas/nueva.html", datos=datos, errores=errores, materiales=opciones,
                           distritos=OPCIONES_DISTRITO, hoy=date.today().isoformat()), (422 if errores else 200)
# [rutas]
