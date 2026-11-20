# ReciclaRed

Plataforma web que conecta a quienes separan residuos reciclables con los **puntos de acopio** y los **recolectores** de su distrito.

## Stack

- **Python 3.12 + Flask**, plantillas Jinja2 y CSS propio (responsive, modo claro y oscuro, sin JavaScript).
- **MySQL 8.4**, con consultas siempre parametrizadas.
- **pytest** contra una base MySQL real.
- **GitHub Actions** para CI/CD y **Oracle Cloud** para el despliegue.

## Ejecutar en local

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
export SECRET_KEY=una-clave-larga DB_HOST=127.0.0.1 DB_NAME=reciclared DB_USER=usuario DB_PASSWORD=clave
flask --app wsgi run
pytest -v
```

## Estructura

```
app/            aplicación Flask (blueprints, plantillas, estilos y esquema SQL)
tests/          pruebas automatizadas por historia de usuario
.github/        pipeline de GitHub Actions
```

<!-- [secciones] -->
