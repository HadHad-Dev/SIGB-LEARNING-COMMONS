DROP DATABASE IF EXISTS sigb_learning_commons;

CREATE DATABASE sigb_learning_commons
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE sigb_learning_commons;

CREATE TABLE category (
    category_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name_category VARCHAR(50) NOT NULL,
    maximum_time_minute INT UNSIGNED NOT NULL DEFAULT 120,
    requires_physical_return BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_category_name UNIQUE (name_category),
    CONSTRAINT chk_category_max_time CHECK (maximum_time_minute > 0)
);

CREATE TABLE inventory_resource (
    bar_code VARCHAR(100) PRIMARY KEY,
    category_id INT UNSIGNED NOT NULL,
    description_title VARCHAR(200) NOT NULL,
    author VARCHAR(150) NULL,
    capacity INT UNSIGNED NULL,
    status ENUM('disponible', 'en_uso', 'mantenimiento', 'extraviado') NOT NULL DEFAULT 'disponible',
    shelf_location VARCHAR(50) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_resource_category FOREIGN KEY (category_id)
        REFERENCES category(category_id) ON DELETE RESTRICT,
    CONSTRAINT chk_resource_capacity CHECK (capacity IS NULL OR capacity > 0)
);

CREATE TABLE user (
    user_id VARCHAR(50) PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    user_type ENUM('alumno', 'docente', 'externo', 'administrador') NOT NULL DEFAULT 'alumno',
    password_hash VARCHAR(255) NULL,
    major ENUM(
        'Tecnologías de la Información',
        'Ciencia de Datos',
        'Negocios Internacionales',
        'Mecatrónica',
        'Diseño Digital'
    ) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_password_by_rol CHECK (
        (user_type = 'externo' AND password_hash IS NULL) OR
        (user_type != 'externo' AND password_hash IS NOT NULL)
    )
);

CREATE TABLE sanction (
    sanction_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    reason VARCHAR(255) NOT NULL,
    started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ends_at DATETIME NULL,
    applied_by VARCHAR(50) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_sanction_user FOREIGN KEY (user_id)
        REFERENCES user(user_id) ON DELETE RESTRICT,
    CONSTRAINT fk_sanction_admin FOREIGN KEY (applied_by)
        REFERENCES user(user_id) ON DELETE RESTRICT,
    CONSTRAINT chk_sanction_dates CHECK (ends_at IS NULL OR ends_at > started_at)
);

CREATE TABLE active_usage (
    usage_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    category_id INT UNSIGNED NULL,
    bar_code VARCHAR(100) NULL,
    starting_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    due_at DATETIME NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_active_barcode UNIQUE (bar_code),
    CONSTRAINT fk_active_user FOREIGN KEY (user_id)
        REFERENCES user(user_id) ON DELETE RESTRICT,
    CONSTRAINT fk_active_category FOREIGN KEY (category_id)
        REFERENCES category(category_id) ON DELETE RESTRICT,
    CONSTRAINT fk_active_resource FOREIGN KEY (bar_code)
        REFERENCES inventory_resource(bar_code) ON DELETE RESTRICT,
    CONSTRAINT chk_active_target CHECK (
        (bar_code IS NOT NULL AND category_id IS NULL) OR
        (bar_code IS NULL AND category_id IS NOT NULL)
    ),
    CONSTRAINT chk_active_due_date CHECK (due_at > starting_date)
);

CREATE TABLE usage_history (
    history_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    category_id INT UNSIGNED NULL,
    bar_code VARCHAR(100) NULL,
    starting_date DATETIME NOT NULL,
    due_at DATETIME NOT NULL,
    end_date DATETIME NOT NULL,
    close_reason ENUM('completado', 'cierre_automatico') NOT NULL,
    closed_by VARCHAR(50) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_history_user FOREIGN KEY (user_id)
        REFERENCES user(user_id) ON DELETE RESTRICT,
    CONSTRAINT fk_history_category FOREIGN KEY (category_id)
        REFERENCES category(category_id) ON DELETE RESTRICT,
    CONSTRAINT fk_history_resource FOREIGN KEY (bar_code)
        REFERENCES inventory_resource(bar_code) ON DELETE RESTRICT,
    CONSTRAINT fk_history_closed_by FOREIGN KEY (closed_by)
        REFERENCES user(user_id) ON DELETE RESTRICT,
    CONSTRAINT chk_history_target CHECK (
        (bar_code IS NOT NULL AND category_id IS NULL) OR
        (bar_code IS NULL AND category_id IS NOT NULL)
    ),
    CONSTRAINT chk_history_due_date CHECK (due_at > starting_date),
    CONSTRAINT chk_history_end_date CHECK (end_date >= starting_date)
);

CREATE TABLE incident_report (
    incident_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    bar_code VARCHAR(100) NULL,
    incident_type ENUM('falla_equipo', 'objeto_perdido', 'libro_danado') NOT NULL,
    title VARCHAR(150) NOT NULL,
    incident_description TEXT NOT NULL,
    incident_location VARCHAR(100) NULL,
    reported_by_user_id VARCHAR(50) NULL,
    reporter_name VARCHAR(100) NULL,
    image_path VARCHAR(255) NULL,
    report_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status_resolution ENUM('pendiente', 'en_custodia', 'resuelto', 'entregado') NOT NULL DEFAULT 'pendiente',
    resolved_at DATETIME NULL,
    resolved_by VARCHAR(50) NULL,
    delivered_to_user_id VARCHAR(50) NULL,
    delivered_to_name VARCHAR(150) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_incident_resource FOREIGN KEY (bar_code)
        REFERENCES inventory_resource(bar_code) ON DELETE RESTRICT,
    CONSTRAINT fk_incident_reporter FOREIGN KEY (reported_by_user_id)
        REFERENCES user(user_id) ON DELETE RESTRICT,
    CONSTRAINT fk_incident_resolver FOREIGN KEY (resolved_by)
        REFERENCES user(user_id) ON DELETE RESTRICT,
    CONSTRAINT chk_incident_reporter CHECK (
        reported_by_user_id IS NOT NULL OR reporter_name IS NOT NULL
    ),
    CONSTRAINT chk_incident_barcode CHECK (
        (incident_type = 'objeto_perdido' AND bar_code IS NULL) OR
        (incident_type IN ('falla_equipo', 'libro_danado') AND bar_code IS NOT NULL)
    ),
    CONSTRAINT chk_incident_type_status CHECK (
        (incident_type = 'objeto_perdido' AND status_resolution IN ('en_custodia', 'entregado')) OR
        (incident_type IN ('falla_equipo', 'libro_danado') AND status_resolution IN ('pendiente', 'resuelto'))
    ),
    CONSTRAINT chk_incident_resolution_date CHECK (
        (status_resolution IN ('resuelto', 'entregado') AND resolved_at IS NOT NULL) OR
        (status_resolution IN ('pendiente', 'en_custodia') AND resolved_at IS NULL)
    ),
    CONSTRAINT chk_incident_delivery CHECK (
        (status_resolution = 'entregado' AND (delivered_to_user_id IS NOT NULL OR delivered_to_name IS NOT NULL)) OR
        (status_resolution != 'entregado' AND delivered_to_user_id IS NULL AND delivered_to_name IS NULL))
        );


INSERT INTO category (category_id, name_category, maximum_time_minute, requires_physical_return) VALUES
(1, 'Libro', 4320, TRUE),
(2, 'Computadora', 120, FALSE),
(3, 'Cubículo', 120, FALSE),
(4, 'Utilería', 180, TRUE),
(5, 'Sala General', 240, FALSE);

INSERT INTO inventory_resource (bar_code, category_id, description_title, author, capacity, status, shelf_location) VALUES
('LIB-001', 1, 'Clean Code: Manual de desarrollo ágil', 'Robert C. Martin', NULL, 'disponible', 'Estante A-01'),
('LIB-002', 1, 'Fundamentos de Bases de Datos', 'Abraham Silberschatz', NULL, 'en_uso', 'Estante A-02'),
('LIB-003', 1, 'Python Crash Course', 'Eric Matthes', NULL, 'disponible', 'Estante A-03'),
('LIB-004', 1, 'Redes de Computadoras', 'Andrew S. Tanenbaum', NULL, 'en_uso', 'Estante A-04'),
('LIB-005', 1, 'Introducción a la Ciencia de Datos', 'Rafael Irizarry', NULL, 'disponible', 'Estante B-01'),
('LIB-006', 1, 'El Mito de Sísifo', 'Albert Camus', NULL, 'disponible', 'Estante C-05'),
('LIB-007', 1, 'Cálculo de una Variable', 'James Stewart', NULL, 'mantenimiento', 'Estante D-02'),
('PC-001',  2, 'Estación Dell OptiPlex #1', NULL, NULL, 'en_uso', 'Zona Digital Norte'),
('PC-002',  2, 'Estación Dell OptiPlex #2', NULL, NULL, 'disponible', 'Zona Digital Norte'),
('PC-003',  2, 'Estación Dell OptiPlex #3', NULL, NULL, 'mantenimiento', 'Zona Digital Sur'),
('PC-004',  2, 'Estación HP ProDesk #4', NULL, NULL, 'disponible', 'Zona Digital Sur'),
('CUB-001', 3, 'Cubículo Grupal 1', NULL, 6, 'en_uso', 'Planta Baja'),
('CUB-002', 3, 'Cubículo Grupal 2', NULL, 6, 'disponible', 'Planta Baja'),
('CUB-003', 3, 'Cubículo Individual 3', NULL, 1, 'disponible', 'Planta Alta'),
('UTI-001', 4, 'Adaptador HDMI a USB-C', NULL, NULL, 'disponible', 'Mostrador Principal'),
('UTI-002', 4, 'Kit de Marcadores para Pintarrón', NULL, NULL, 'en_uso', 'Mostrador Principal'),
('UTI-003', 4, 'Calculadora Científica Casio FX-991', NULL, NULL, 'disponible', 'Mostrador Principal');

INSERT INTO user (user_id, full_name, user_type, password_hash, major) VALUES
('202400101', 'Ana Sofía Herrera Ruiz', 'alumno', 'pendiente_hash', 'Tecnologías de la Información'),
('202400102', 'Carlos Eduardo Méndez Lara', 'alumno', 'pendiente_hash', 'Ciencia de Datos'),
('202400103', 'Mariana Guadalupe Torres Silva', 'alumno', 'pendiente_hash', 'Negocios Internacionales'),
('202400104', 'Diego Alejandro Vargas Cruz', 'alumno', 'pendiente_hash', 'Mecatrónica'),
('202400105', 'Valeria Fernanda Soto Gómez', 'alumno', 'pendiente_hash', 'Tecnologías de la Información'),
('202400106', 'Luis Fernando Ramírez Ortiz', 'alumno', 'pendiente_hash', 'Diseño Digital'),
('202400107', 'Camila Estefanía Navarro Díaz', 'alumno', 'pendiente_hash', 'Ciencia de Datos'),
('202400108', 'Jorge Iván Castillo Morales', 'alumno', 'pendiente_hash', 'Mecatrónica'),
('DOC-001',   'Mtro. Ricardo Morales Vega', 'docente', 'pendiente_hash', 'Tecnologías de la Información'),
('ADM-001',   'Administrador Learning Commons', 'administrador', 'pendiente_hash', NULL),
('EXT-001',   'Laura Patricia Gómez', 'externo', NULL, NULL);

INSERT INTO sanction (user_id, reason, started_at, ends_at, applied_by) VALUES
('202400106', 'Entrega tardía de material bibliográfico', DATE_SUB(NOW(), INTERVAL 3 DAY), DATE_ADD(NOW(), INTERVAL 4 DAY), 'ADM-001');

INSERT INTO active_usage (user_id, category_id, bar_code, starting_date, due_at) VALUES
('202400101', NULL, 'LIB-002', DATE_SUB(NOW(), INTERVAL 1 DAY),    DATE_ADD(NOW(), INTERVAL 2 DAY)),
('202400102', NULL, 'LIB-004', DATE_SUB(NOW(), INTERVAL 2 HOUR),   DATE_ADD(NOW(), INTERVAL 70 HOUR)),
('202400105', NULL, 'PC-001',  DATE_SUB(NOW(), INTERVAL 3 HOUR),   DATE_SUB(NOW(), INTERVAL 1 HOUR)),
('202400103', NULL, 'CUB-001', DATE_SUB(NOW(), INTERVAL 30 MINUTE), DATE_ADD(NOW(), INTERVAL 90 MINUTE)),
('202400103', NULL, 'UTI-002', DATE_SUB(NOW(), INTERVAL 30 MINUTE), DATE_ADD(NOW(), INTERVAL 150 MINUTE)),
('EXT-001',   5,    NULL,      DATE_SUB(NOW(), INTERVAL 1 HOUR),   DATE_ADD(NOW(), INTERVAL 3 HOUR));

INSERT INTO usage_history (user_id, category_id, bar_code, starting_date, due_at, end_date, close_reason, closed_by) VALUES
('202400101', NULL, 'CUB-002', DATE_SUB(NOW(), INTERVAL 1 DAY),  DATE_SUB(NOW(), INTERVAL 22 HOUR),  DATE_SUB(NOW(), INTERVAL 22 HOUR),  'completado', 'ADM-001'),
('202400104', NULL, 'PC-002',  DATE_SUB(NOW(), INTERVAL 2 DAY),  DATE_SUB(NOW(), INTERVAL 46 HOUR),  DATE_SUB(NOW(), INTERVAL 46 HOUR),  'completado', 'ADM-001'),
('202400102', 5,    NULL,      DATE_SUB(NOW(), INTERVAL 2 DAY),  DATE_SUB(NOW(), INTERVAL 44 HOUR),  DATE_SUB(NOW(), INTERVAL 44 HOUR),  'cierre_automatico', NULL),
('DOC-001',   NULL, 'LIB-001', DATE_SUB(NOW(), INTERVAL 3 DAY),  NOW(),                              DATE_SUB(NOW(), INTERVAL 1 DAY),    'completado', 'ADM-001'),
('202400105', NULL, 'PC-004',  DATE_SUB(NOW(), INTERVAL 4 DAY),  DATE_SUB(NOW(), INTERVAL 94 HOUR),  DATE_SUB(NOW(), INTERVAL 94 HOUR),  'completado', 'ADM-001'),
('202400107', NULL, 'CUB-003', DATE_SUB(NOW(), INTERVAL 5 DAY),  DATE_SUB(NOW(), INTERVAL 118 HOUR), DATE_SUB(NOW(), INTERVAL 118 HOUR), 'completado', 'ADM-001'),
('202400108', NULL, 'UTI-001', DATE_SUB(NOW(), INTERVAL 6 DAY),  DATE_SUB(NOW(), INTERVAL 141 HOUR), DATE_SUB(NOW(), INTERVAL 142 HOUR), 'completado', 'ADM-001');
INSERT INTO incident_report (bar_code, incident_type, title, incident_description, incident_location, reported_by_user_id, reporter_name, image_path, report_date, status_resolution, resolved_at, resolved_by, delivered_to_user_id, delivered_to_name) VALUES
(NULL, 'objeto_perdido', 'Termo metálico azul', 'Termo marca Yeti color azul marino con calcomanías.', 'Cubículo 2 - Planta Baja', '202400101', NULL, 'img/objetos/termo.png', DATE_SUB(NOW(), INTERVAL 20 HOUR), 'en_custodia', NULL, NULL, NULL, NULL),
(NULL, 'objeto_perdido', 'Audífonos Bluetooth blancos', 'Estuche de carga blanco con ambos auriculares adentro.', 'Zona Digital Norte', NULL, 'Personal de limpieza', 'img/objetos/audifonos.png', DATE_SUB(NOW(), INTERVAL 1 DAY), 'en_custodia', NULL, NULL, NULL, NULL),
(NULL, 'objeto_perdido', 'Llaves con llavero rojo', 'Juego de 3 llaves y control de auto.', 'Sala General', '202400102', NULL, 'img/objetos/llaves.png', DATE_SUB(NOW(), INTERVAL 4 DAY), 'entregado', DATE_SUB(NOW(), INTERVAL 3 DAY), 'ADM-001', '202400108', NULL),
(NULL, 'objeto_perdido', 'Cargador laptop USB-C 65W', 'Cargador negro enrollado con velcro.', 'Mesa de estudio 4', '202400104', NULL, 'img/objetos/cargador.png', DATE_SUB(NOW(), INTERVAL 5 HOUR), 'en_custodia', NULL, NULL, NULL, NULL),
('PC-003', 'falla_equipo', 'Monitor sin señal de video', 'La pantalla parpadea y no detecta el cable DisplayPort.', 'Zona Digital Sur', '202400105', NULL, NULL, DATE_SUB(NOW(), INTERVAL 1 DAY), 'pendiente', NULL, NULL, NULL, NULL),
('LIB-007', 'libro_danado', 'Lomo desprendido', 'Las primeras 20 páginas se despegaron del encuadernado.', 'Mostrador de devoluciones', 'ADM-001', NULL, NULL, DATE_SUB(NOW(), INTERVAL 3 DAY), 'pendiente', NULL, NULL, NULL, NULL);