"""Administración: catálogo de materiales y puntos de acopio (solo rol admin)."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from pymysql.err import IntegrityError

from .. import db
from ..security import rol_requerido
from ..catalogos import DIAS, DISTRITOS, OPCIONES_DISTRITO, leer_hora
from ..filtros import hora as formato_hora
# [imports]

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/")
@rol_requerido("admin")
def inicio():
    return render_template("admin/inicio.html")
@bp.route("/materiales", methods=["GET", "POST"])
@rol_requerido("admin")
def materiales():
    nombre, error = "", None
    if request.method == "POST":
        nombre = " ".join(request.form.get("nombre", "").split())
        if not 2 <= len(nombre) <= 40:
            error = "Escribe un nombre de 2 a 40 caracteres."
        elif db.query("SELECT id FROM materiales WHERE LOWER(nombre) = LOWER(%s)", (nombre,), uno=True):
            error = "Ese material ya existe en el catálogo."
        else:
            try:
                db.execute("INSERT INTO materiales (nombre) VALUES (%s)", (nombre,))
            except IntegrityError:
                error = "Ese material ya existe en el catálogo."
            else:
                flash(f"Agregaste «{nombre}» al catálogo.", "exito")
                return redirect(url_for("admin.materiales"))
    lista = db.query("SELECT id, nombre FROM materiales ORDER BY nombre")
    return render_template("admin/materiales.html", materiales=lista, nombre=nombre, error=error), (422 if error else 200)
def _datos_punto():
    return {campo: " ".join(request.form.get(campo, "").split()) for campo in ("nombre", "direccion", "distrito")}


def _validar_punto(datos):
    errores = {}
    if not 3 <= len(datos["nombre"]) <= 120:
        errores["nombre"] = "Escribe el nombre del punto (de 3 a 120 caracteres)."
    if not 5 <= len(datos["direccion"]) <= 200:
        errores["direccion"] = "Escribe la dirección (de 5 a 200 caracteres)."
    if datos["distrito"] not in DISTRITOS:
        errores["distrito"] = "Elige el distrito."
    return errores


@bp.route("/puntos")
@rol_requerido("admin")
def puntos():
    lista = db.query("SELECT id, nombre, direccion, distrito, activo FROM puntos_acopio ORDER BY activo DESC, nombre")
    return render_template("admin/puntos.html", puntos=lista)


@bp.route("/puntos/nuevo", methods=["GET", "POST"])
@rol_requerido("admin")
def punto_nuevo():
    datos, errores = {"nombre": "", "direccion": "", "distrito": ""}, {}
    if request.method == "POST":
        datos = _datos_punto()
        errores = _validar_punto(datos)
        if not errores:
            _, punto_id = db.execute(
                "INSERT INTO puntos_acopio (nombre, direccion, distrito) VALUES (%s, %s, %s)",
                (datos["nombre"], datos["direccion"], datos["distrito"]),
            )
            flash(f"Registraste «{datos['nombre']}». Ahora indica qué materiales recibe y su horario.", "exito")
            return redirect(url_for("admin.punto_materiales_horarios", punto_id=punto_id))
    return render_template("admin/punto_form.html", datos=datos, errores=errores, distritos=OPCIONES_DISTRITO,
                           modo="nuevo"), (422 if errores else 200)
def _leer_materiales_y_horarios(ids_validos):
    elegidos = {int(v) for v in request.form.getlist("materiales") if v.isdigit() and int(v) in ids_validos}
    horas, horarios, errores = {}, {}, []
    for numero, nombre in DIAS:
        apertura = request.form.get(f"apertura_{numero}", "").strip()
        cierre = request.form.get(f"cierre_{numero}", "").strip()
        horas[numero] = (apertura, cierre)
        if not apertura and not cierre:
            continue
        inicio, fin = leer_hora(apertura), leer_hora(cierre)
        if inicio is None or fin is None:
            errores.append(f"{nombre}: indica la hora de apertura y la de cierre.")
        elif fin <= inicio:
            errores.append(f"{nombre}: la hora de cierre debe ser posterior a la de apertura.")
        else:
            horarios[numero] = (apertura, cierre)
    return elegidos, horas, horarios, errores


def _guardar_materiales_y_horarios(punto_id, elegidos, horarios):
    """Reemplaza materiales y horarios del punto en una sola transacción."""
    conexion = db.get_db()
    conexion.begin()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM punto_material WHERE punto_id = %s", (punto_id,))
            cursor.execute("DELETE FROM horarios WHERE punto_id = %s", (punto_id,))
            for material_id in sorted(elegidos):
                cursor.execute("INSERT INTO punto_material (punto_id, material_id) VALUES (%s, %s)", (punto_id, material_id))
            for dia, (apertura, cierre) in sorted(horarios.items()):
                cursor.execute("INSERT INTO horarios (punto_id, dia, apertura, cierre) VALUES (%s, %s, %s, %s)",
                               (punto_id, dia, apertura, cierre))
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise


@bp.route("/puntos/<int:punto_id>/materiales-horarios", methods=["GET", "POST"])
@rol_requerido("admin")
def punto_materiales_horarios(punto_id):
    punto = db.query("SELECT id, nombre, distrito FROM puntos_acopio WHERE id = %s", (punto_id,), uno=True)
    if punto is None:
        abort(404)
    materiales = db.query("SELECT id, nombre FROM materiales ORDER BY nombre")
    errores = []
    if request.method == "POST":
        elegidos, horas, horarios, errores = _leer_materiales_y_horarios({mat["id"] for mat in materiales})
        if not errores:
            _guardar_materiales_y_horarios(punto_id, elegidos, horarios)
            flash("Guardaste los materiales y el horario del punto.", "exito")
            return redirect(url_for("admin.punto_materiales_horarios", punto_id=punto_id))
    else:
        elegidos = {fila["material_id"] for fila in db.query(
            "SELECT material_id FROM punto_material WHERE punto_id = %s", (punto_id,))}
        horas = {fila["dia"]: (formato_hora(fila["apertura"]), formato_hora(fila["cierre"])) for fila in db.query(
            "SELECT dia, apertura, cierre FROM horarios WHERE punto_id = %s", (punto_id,))}
    return render_template("admin/punto_materiales.html", punto=punto, materiales=materiales, dias=DIAS,
                           elegidos=elegidos, horas=horas, errores=errores), (422 if errores else 200)
@bp.route("/puntos/<int:punto_id>/editar", methods=["GET", "POST"])
@rol_requerido("admin")
def punto_editar(punto_id):
    punto = db.query("SELECT id, nombre, direccion, distrito FROM puntos_acopio WHERE id = %s", (punto_id,), uno=True)
    if punto is None:
        abort(404)
    datos, errores = {campo: punto[campo] for campo in ("nombre", "direccion", "distrito")}, {}
    if request.method == "POST":
        datos = _datos_punto()
        errores = _validar_punto(datos)
        if not errores:
            db.execute("UPDATE puntos_acopio SET nombre = %s, direccion = %s, distrito = %s WHERE id = %s",
                       (datos["nombre"], datos["direccion"], datos["distrito"], punto_id))
            flash("Guardaste los cambios del punto.", "exito")
            return redirect(url_for("admin.puntos"))
    return render_template("admin/punto_form.html", datos=datos, errores=errores, distritos=OPCIONES_DISTRITO,
                           modo="editar"), (422 if errores else 200)


@bp.post("/puntos/<int:punto_id>/estado")
@rol_requerido("admin")
def punto_estado(punto_id):
    if db.query("SELECT id FROM puntos_acopio WHERE id = %s", (punto_id,), uno=True) is None:
        abort(404)
    activo = 1 if request.form.get("activo") == "1" else 0
    # Baja lógica: el registro se conserva y solo cambia su estado.
    db.execute("UPDATE puntos_acopio SET activo = %s WHERE id = %s", (activo, punto_id))
    if activo:
        flash("Reactivaste el punto: vuelve a aparecer en el directorio.", "exito")
    else:
        flash("Desactivaste el punto: ya no aparece en el directorio.", "info")
    return redirect(url_for("admin.puntos"))
# [rutas]
