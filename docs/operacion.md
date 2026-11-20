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

<!-- [operacion] -->
