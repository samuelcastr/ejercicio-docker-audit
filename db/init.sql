CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    email VARCHAR(120) NOT NULL
);

INSERT INTO usuarios (nombre, email) VALUES
    ('Ana Pérez', 'ana@techova.co'),
    ('Luis Gómez', 'luis@techova.co'),
    ('Carla Ruiz', 'carla@techova.co');