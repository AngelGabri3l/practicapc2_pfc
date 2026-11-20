-- Esquema de ReciclaRed. Cada sentencia es idempotente (IF NOT EXISTS / INSERT IGNORE):
-- la aplicación lo ejecuta al arrancar, así que cada versión desplegada agrega lo que falte.
-- Las tablas se crean completas desde su primera versión (no se usan ALTER).

CREATE TABLE IF NOT EXISTS usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  rol ENUM('ciudadano', 'recolector', 'admin') NOT NULL,
  distrito VARCHAR(60) NOT NULL,
  telefono VARCHAR(20) NULL,
  creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS materiales (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(40) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT IGNORE INTO materiales (nombre) VALUES
  ('Papel'), ('Cartón'), ('Plástico'), ('Vidrio'), ('Metal'), ('Electrónicos');
CREATE TABLE IF NOT EXISTS puntos_acopio (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(120) NOT NULL,
  direccion VARCHAR(200) NOT NULL,
  distrito VARCHAR(60) NOT NULL,
  activo TINYINT(1) NOT NULL DEFAULT 1,
  creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_puntos_distrito (distrito, activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
-- [fin-esquema]
