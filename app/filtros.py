"""Filtros de plantilla para mostrar fechas y horas."""
from datetime import date, datetime, time, timedelta


def hora(valor):
    if valor is None or valor == "":
        return ""
    if isinstance(valor, timedelta):
        minutos = int(valor.total_seconds()) // 60
        return f"{minutos // 60:02d}:{minutos % 60:02d}"
    if isinstance(valor, (time, datetime)):
        return valor.strftime("%H:%M")
    return str(valor)[:5]


def fecha(valor):
    if not valor:
        return ""
    if isinstance(valor, (date, datetime)):
        return valor.strftime("%d/%m/%Y")
    return str(valor)


def registrar(app):
    app.jinja_env.filters["hora"] = hora
    app.jinja_env.filters["fecha"] = fecha
