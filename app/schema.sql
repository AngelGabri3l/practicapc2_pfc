-- Esquema de ReciclaRed. Cada sentencia es idempotente (IF NOT EXISTS / INSERT IGNORE):
-- la aplicación lo ejecuta al arrancar, así que cada versión desplegada agrega lo que falte.
-- Las tablas se crean completas desde su primera versión (no se usan ALTER).

-- [fin-esquema]
