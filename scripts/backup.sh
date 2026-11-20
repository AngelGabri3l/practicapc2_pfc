#!/usr/bin/env bash
# Respaldo de MySQL (contenedor db) hacia OCI Object Storage.
# Autenticación: instance principal (no se guardan llaves ni contraseñas de Oracle en la VM).
# Uso: BACKUP_BUCKET=nombre-del-bucket OCI_BIN=$HOME/oci-venv/bin/oci bash scripts/backup.sh
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUCKET="${BACKUP_BUCKET:?Define BACKUP_BUCKET con el nombre del bucket}"
OCI_BIN="${OCI_BIN:-oci}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
FILE="$(mktemp "/tmp/backup-${STAMP}-XXXXXX.sql.gz")"   # mktemp crea el archivo con permisos 600
OBJECT="mysql/backup-${STAMP}.sql.gz"
trap 'rm -f "$FILE"' EXIT

cd "$APP_DIR"

echo "[$(date -u +%FT%TZ)] Generando dump..."
# La contraseña se lee dentro del contenedor; no aparece en la línea de comandos de la VM.
docker compose exec -T db sh -c \
  'exec mysqldump --single-transaction --routines -uroot -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE"' \
  | gzip > "$FILE"

# Verificación mínima: un dump real pesa más que un gzip vacío.
[ "$(stat -c %s "$FILE")" -gt 200 ] || { echo "ERROR: el dump salió vacío o incompleto" >&2; exit 1; }

echo "[$(date -u +%FT%TZ)] Subiendo a Object Storage..."
NS="${OCI_NAMESPACE:-$("$OCI_BIN" os ns get --auth instance_principal --query data --raw-output)}"
"$OCI_BIN" os object put --auth instance_principal --namespace-name "$NS" \
  --bucket-name "$BUCKET" --file "$FILE" --name "$OBJECT" --force

echo "[$(date -u +%FT%TZ)] OK: ${BUCKET}/${OBJECT}"
