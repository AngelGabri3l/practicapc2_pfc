"""US-23 · Respaldo diario de la base de datos (verificaciones estáticas del script)."""
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "backup.sh"


def test_el_script_tiene_sintaxis_valida():
    assert subprocess.run(["bash", "-n", str(SCRIPT)], check=False).returncode == 0


def test_usa_instance_principal_y_no_guarda_credenciales():
    texto = SCRIPT.read_text(encoding="utf-8")
    assert "--auth instance_principal" in texto
    assert "set -euo pipefail" in texto
    for prohibido in ("BEGIN RSA", "BEGIN PRIVATE KEY", "password=", "key_file"):
        assert prohibido not in texto


def test_el_bucket_es_obligatorio():
    resultado = subprocess.run(["bash", str(SCRIPT)], capture_output=True, text=True, check=False,
                               env={"PATH": "/usr/bin:/bin"})
    assert resultado.returncode != 0
    assert "BACKUP_BUCKET" in resultado.stderr
