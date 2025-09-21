CREATE DATABASE IF NOT EXISTS quadra;
USE quadra;

CREATE TABLE IF NOT EXISTS puestos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255),
    descripcion TEXT,
    latitud VARCHAR(50),
    longitud VARCHAR(50),
    foto VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS comentarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    puesto_id INT,
    comentario TEXT,
    calificacion INT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (puesto_id) REFERENCES puestos(id)
);

