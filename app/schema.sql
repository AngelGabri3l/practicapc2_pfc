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
CREATE TABLE IF NOT EXISTS ofertas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  ciudadano_id INT NOT NULL,
  material_id INT NOT NULL,
  cantidad VARCHAR(60) NOT NULL,
  direccion VARCHAR(200) NOT NULL,
  distrito VARCHAR(60) NOT NULL,
  fecha DATE NOT NULL,
  hora_inicio TIME NOT NULL,
  hora_fin TIME NOT NULL,
  estado ENUM('Disponible', 'Aceptada', 'Recogida', 'Cancelada') NOT NULL DEFAULT 'Disponible',
  recolector_id INT NULL,
  aceptada_en DATETIME NULL,
  recogida_en DATETIME NULL,
  creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_ofertas_estado_distrito (estado, distrito),
  CONSTRAINT fk_oferta_ciudadano FOREIGN KEY (ciudadano_id) REFERENCES usuarios (id),
  CONSTRAINT fk_oferta_material FOREIGN KEY (material_id) REFERENCES materiales (id),
  CONSTRAINT fk_oferta_recolector FOREIGN KEY (recolector_id) REFERENCES usuarios (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS punto_material (
  punto_id INT NOT NULL,
  material_id INT NOT NULL,
  PRIMARY KEY (punto_id, material_id),
  CONSTRAINT fk_pm_punto FOREIGN KEY (punto_id) REFERENCES puntos_acopio (id) ON DELETE CASCADE,
  CONSTRAINT fk_pm_material FOREIGN KEY (material_id) REFERENCES materiales (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS horarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  punto_id INT NOT NULL,
  dia TINYINT NOT NULL,
  apertura TIME NOT NULL,
  cierre TIME NOT NULL,
  UNIQUE KEY uq_horario_dia (punto_id, dia),
  CONSTRAINT fk_horario_punto FOREIGN KEY (punto_id) REFERENCES puntos_acopio (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
-- [fin-esquema]
