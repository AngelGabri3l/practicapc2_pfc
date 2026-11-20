# Operación de ReciclaRed en Oracle Cloud

## Alarma de salud (US-22)

Objetivo: recibir un correo si el balanceador detecta que la aplicación dejó de responder en `/health`.

1. Networking → Load balancers → tu balanceador → Backend sets → tu backend set → Metrics.
2. En el gráfico **Unhealthy backend servers**: Options → **Create an alarm on this query**.
3. Nombre `reciclared-backend-no-saludable`, severidad **Critical**, estadística **Max**.
4. Regla de disparo: **more than 0**, con un retraso de **2 minutos** (evita falsas alarmas durante un deploy).
5. En Notifications crea el tema `alertas-reciclared` con una suscripción **Email** y confirma el correo que llega.

### Prueba y evidencia

```bash
cd /opt/app
docker compose stop web     # en unos 3 minutos debe llegar el correo de alerta
docker compose start web    # al recuperarse debe llegar el correo de recuperación
```

Guarda tres capturas: la alarma activa en la consola, el correo de alerta y el de recuperación.


## Respaldo diario de la base de datos (US-23)

`scripts/backup.sh` hace un `mysqldump` del contenedor `db`, lo comprime y lo sube a Object Storage. Se autentica con
**instance principal**: la VM tiene permiso por IAM y no guarda llaves ni contraseñas de Oracle.

### Permisos (una sola vez, en el compartment raíz)

- *Dynamic group* `vm-backups`: `ALL {instance.compartment.id = 'OCID_DEL_COMPARTMENT'}`
- Política: `Allow dynamic-group vm-backups to manage objects in compartment NOMBRE where target.bucket.name = 'NOMBRE_DEL_BUCKET'`

### En la VM

```bash
python3 -m venv ~/oci-venv && ~/oci-venv/bin/pip install oci-cli
BACKUP_BUCKET=NOMBRE_DEL_BUCKET OCI_BIN=$HOME/oci-venv/bin/oci bash /opt/app/scripts/backup.sh   # prueba manual
crontab -e   # agrega la línea de abajo (respaldo diario, hora UTC)
0 3 * * * BACKUP_BUCKET=NOMBRE_DEL_BUCKET OCI_BIN=/home/ubuntu/oci-venv/bin/oci bash /opt/app/scripts/backup.sh >> /home/ubuntu/backup.log 2>&1
```

### Prueba de restauración (evidencia)

```bash
cd /opt/app
~/oci-venv/bin/oci os object get --auth instance_principal --bucket-name NOMBRE_DEL_BUCKET \
  --name mysql/backup-XXXX.sql.gz --file /tmp/restore.sql.gz
docker compose exec -T db sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -e "CREATE DATABASE restore_test"'
gunzip -c /tmp/restore.sql.gz | docker compose exec -T db sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" restore_test'
docker compose exec -T db sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" restore_test -e "SELECT COUNT(*) FROM ofertas;"'
docker compose exec -T db sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -e "DROP DATABASE restore_test"'
```

El conteo debe coincidir con el de la base en producción.
