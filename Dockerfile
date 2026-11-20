FROM python:3.15-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Parches de seguridad del sistema y de pip; se elimina setuptools (la aplicación no lo usa en ejecución)
# hadolint ignore=DL3005,DL3013
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip \
    && pip uninstall -y setuptools wheel \
    && find /usr/local/lib -type f -name 'setuptools-*.whl' -delete

WORKDIR /srv

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY wsgi.py .
COPY app/ app/

# Seguridad: el proceso no corre como root
RUN useradd --create-home --uid 10001 appuser
USER 10001

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"]

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "4", "--worker-class", "gthread", "--access-logfile", "-", "wsgi:app"]
