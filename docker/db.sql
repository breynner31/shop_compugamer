CREATE DATABASE db_compugamer;
USE db_compugamer;

-- Crear la tabla 'users'
CREATE TABLE users (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
    email VARCHAR(50) NOT NULL,
    password TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Insertar un registro en la tabla 'users'
INSERT INTO users (id, name, email, password) 
VALUES (1, 'jimena', 'jimena3108@gmail.com', '123');

-- Crear la tabla 'productos'
CREATE TABLE productos (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    descripcion TEXT,
    precio FLOAT NOT NULL,
    imagen LONGBLOB,
    user_id INT DEFAULT NULL,
    PRIMARY KEY (id),
    KEY user_id (user_id),
    CONSTRAINT productos_ibfk_1 FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Crear la tabla 'productos_vendidos'
CREATE TABLE productos_vendidos (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    descripcion VARCHAR(100) DEFAULT NULL,
    precio FLOAT DEFAULT NULL,
    imagen LONGBLOB,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
