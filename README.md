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


## Flujo de trabajo (ramas y Pull Requests)

| Rama | Uso |
|---|---|
| `main` | Producción. Solo recibe Pull Requests desde `test` al cierre de cada sprint. Cada merge despliega en Oracle Cloud. |
| `test` | Integración y pruebas. Recibe el Pull Request de cada historia de usuario. |
| `feature/US-xx-descripcion` | Una rama por historia, creada desde `test`. |

- **Commits:** `tipo(US-xx): descripción`, con tipo `feat`, `fix`, `test`, `docs`, `ci`, `build`, `chore` o `style`.
- **Pull Requests:** usan la plantilla de `.github/pull_request_template.md`, con los criterios de aceptación y la Definition of Done.
- **Protección:** `main` y `test` exigen Pull Request y el pipeline en verde; nadie hace push directo.


## Despliegue (CI/CD)

Cada push a `main` (es decir, cada Pull Request de release desde `test`) ejecuta el pipeline completo y, si todo pasa, despliega en Oracle Cloud:

1. Gitleaks, Bandit, pip-audit y pruebas con MySQL real.
2. Hadolint, build de la imagen y Trivy; publicación en GHCR.
3. Deploy por SSH en la VM (`/opt/app`), `docker compose up` y smoke test a `/health` por el balanceador.
4. OWASP ZAP (DAST) contra la URL pública.

### Secrets requeridos (Settings → Secrets and variables → Actions)

| Secret | Contenido |
|---|---|
| `OCI_HOST` | IP pública de la VM |
| `OCI_USER` | Usuario SSH (`ubuntu`) |
| `OCI_SSH_KEY` | Llave privada completa (formato PEM) |
| `OCI_KNOWN_HOSTS` | `IP ssh-ed25519 AAAA...` en una línea |
| `LB_HOST` | IP pública del balanceador |
| `MYSQL_ROOT_PASSWORD`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Datos de la base (solo letras y números) |
| `SECRET_KEY` | Cadena aleatoria larga para firmar sesiones |
| `ADMIN_PASSWORD` | Contraseña del administrador inicial (mínimo 12 caracteres) |

El administrador inicial se crea con el correo `admin@reciclared.local` (configurable con `ADMIN_EMAIL`).

<!-- [secciones] -->
