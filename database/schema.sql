DROP DATABASE IF EXISTS sigb_learning_commons;
CREATE DATABASE sigb_learning_commons
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE sigb_learning_commons;

CREATE TABLE category (
    category_id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name_category            VARCHAR(60) NOT NULL UNIQUE,
    maximum_time_minute      INT UNSIGNED NOT NULL,
    requires_physical_return BOOLEAN NOT NULL DEFAULT FALSE,
    created_at               TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at               TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT chk_category_max_time CHECK (maximum_time_minute > 0)
);

CREATE TABLE inventory_resource (
    bar_code          VARCHAR(40) PRIMARY KEY,
    category_id       INT UNSIGNED NOT NULL,
    description_title VARCHAR(150) NOT NULL,
    author            VARCHAR(120) NULL,
    capacity          INT UNSIGNED NULL,
    status            ENUM('disponible', 'en_uso', 'mantenimiento', 'extraviado') NOT NULL DEFAULT 'disponible',
    shelf_location    VARCHAR(60) NULL,
    created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_resource_category
        FOREIGN KEY (category_id) REFERENCES category(category_id)
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT chk_resource_capacity CHECK (capacity IS NULL OR capacity > 0)
);

CREATE TABLE user (
    user_id         INT UNSIGNED PRIMARY KEY,
    full_name       VARCHAR(120) NOT NULL,
    user_type       ENUM('alumno', 'docente', 'administrativo', 'externo', 'administrador') NOT NULL,
    gender          ENUM('F', 'M') NULL,
    password        VARCHAR(100) NULL,
    major           ENUM(
        'DDAA', 'AACH', 'DNAM', 'MTAA', 'MTMF',
        'TISDM', 'LI', 'LGIEC', 'ITI', 'IMT',
        'CDIA', 'LINM', 'LGCH', 'TMSL', 'TMEI',
        'THCM', 'TMKT', 'TMAT', 'TMFM', 'TCDD',
        'TELT', 'TDSM', 'TDAD', 'LDPA', 'LITD',
        'LIAD', 'LIMK', 'LIED', 'LIMT', 'IDGS'
    ) NULL,
    quarter         INT UNSIGNED NULL,
    teacher_type    ENUM('PTC', 'PA') NULL,
    department_area VARCHAR(80) NULL,
    phone           VARCHAR(20) NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT chk_password_by_rol CHECK (
        (user_type = 'externo' AND password IS NULL) OR
        (user_type <> 'externo' AND password IS NOT NULL)
    ),
    CONSTRAINT chk_gender_by_rol CHECK (
        user_type IN ('externo', 'administrador') OR gender IS NOT NULL
    ),
    CONSTRAINT chk_alumno_fields CHECK (
        (user_type = 'alumno' AND major IS NOT NULL AND quarter BETWEEN 1 AND 11) OR
        (user_type <> 'alumno' AND major IS NULL AND quarter IS NULL)
    ),
    CONSTRAINT chk_docente_fields CHECK (
        (user_type = 'docente' AND teacher_type IS NOT NULL) OR
        (user_type <> 'docente' AND teacher_type IS NULL)
    ),
    CONSTRAINT chk_admin_area CHECK (
        (user_type = 'administrativo' AND department_area IS NOT NULL) OR
        (user_type <> 'administrativo' AND department_area IS NULL)
    ),
    CONSTRAINT chk_externo_phone CHECK (
        user_type <> 'externo' OR phone IS NOT NULL
    )
);

CREATE TABLE active_usage (
    usage_id        INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id         INT UNSIGNED NOT NULL,
    category_id     INT UNSIGNED NULL,
    bar_code        VARCHAR(40) NULL UNIQUE,
    attendees_count INT UNSIGNED NOT NULL DEFAULT 1,
    starting_date   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    due_at          DATETIME NOT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_active_user
        FOREIGN KEY (user_id) REFERENCES user(user_id)
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_active_category
        FOREIGN KEY (category_id) REFERENCES category(category_id)
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_active_resource
        FOREIGN KEY (bar_code) REFERENCES inventory_resource(bar_code)
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT chk_active_resource_or_category CHECK (
        (bar_code IS NOT NULL AND category_id IS NULL) OR
        (bar_code IS NULL AND category_id IS NOT NULL)
    ),
    CONSTRAINT chk_active_dates CHECK (due_at > starting_date),
    CONSTRAINT chk_active_attendees CHECK (attendees_count >= 1)
);

CREATE TABLE usage_history (
    history_id      INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id         INT UNSIGNED NOT NULL,
    category_id     INT UNSIGNED NULL,
    bar_code        VARCHAR(40) NULL,
    attendees_count INT UNSIGNED NOT NULL DEFAULT 1,
    starting_date   DATETIME NOT NULL,
    due_at          DATETIME NOT NULL,
    end_date        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    close_reason    ENUM('completado', 'cierre_automatico') NOT NULL,
    closed_by       INT UNSIGNED NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_history_user
        FOREIGN KEY (user_id) REFERENCES user(user_id)
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_history_category
        FOREIGN KEY (category_id) REFERENCES category(category_id)
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_history_resource
        FOREIGN KEY (bar_code) REFERENCES inventory_resource(bar_code)
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_history_closed_by
        FOREIGN KEY (closed_by) REFERENCES user(user_id)
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT chk_history_resource_or_category CHECK (
        (bar_code IS NOT NULL AND category_id IS NULL) OR
        (bar_code IS NULL AND category_id IS NOT NULL)
    ),
    CONSTRAINT chk_history_dates CHECK (
        due_at > starting_date AND end_date >= starting_date
    ),
    CONSTRAINT chk_history_close_by_reason CHECK (
        (close_reason = 'completado' AND closed_by IS NOT NULL) OR
        (close_reason = 'cierre_automatico' AND closed_by IS NULL)
    ),
    CONSTRAINT chk_history_attendees CHECK (attendees_count >= 1)
);


CREATE TABLE lost_item (
    item_id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    title                VARCHAR(120) NOT NULL,
    description          TEXT NOT NULL,
    found_location       VARCHAR(100) NULL,
    found_by_user_id     INT UNSIGNED NULL,
    finder_name          VARCHAR(120) NULL,
    found_date           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status               ENUM('en_custodia', 'entregado') NOT NULL DEFAULT 'en_custodia',
    delivered_at         DATETIME NULL,
    delivered_by         INT UNSIGNED NULL,
    delivered_to_user_id INT UNSIGNED NULL,
    delivered_to_name    VARCHAR(120) NULL,
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_lost_found_by
        FOREIGN KEY (found_by_user_id) REFERENCES user(user_id)
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_lost_delivered_by
        FOREIGN KEY (delivered_by) REFERENCES user(user_id)
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_lost_delivered_to
        FOREIGN KEY (delivered_to_user_id) REFERENCES user(user_id)
        ON DELETE RESTRICT ON UPDATE RESTRICT,

    -- Quien encontró el objeto: usuario registrado o nombre libre
    CONSTRAINT chk_lost_finder CHECK (
        found_by_user_id IS NOT NULL OR finder_name IS NOT NULL
    ),
    CONSTRAINT chk_lost_delivery CHECK (
        (status = 'en_custodia'
            AND delivered_at IS NULL
            AND delivered_by IS NULL
            AND delivered_to_user_id IS NULL
            AND delivered_to_name IS NULL) OR
        (status = 'entregado'
            AND delivered_at IS NOT NULL
            AND delivered_at >= found_date
            AND delivered_by IS NOT NULL
            AND (delivered_to_user_id IS NOT NULL OR delivered_to_name IS NOT NULL))
    )
);


INSERT INTO category (name_category, maximum_time_minute, requires_physical_return) VALUES
    ('Computadora',      120, FALSE),
    ('Cubículo',         120, FALSE),
    ('Sala General',     180, FALSE),
    ('Clase de idiomas', 120, FALSE),
    ('Libro',            480, TRUE),
    ('Utilería',         180, TRUE);

INSERT INTO inventory_resource (bar_code, category_id, description_title, author, capacity, status, shelf_location) VALUES
    ('PC-01',   1, 'Computadora Dell OptiPlex 01',  NULL,               1,    'disponible',    'Zona Cómputo'),
    ('PC-02',   1, 'Computadora Dell OptiPlex 02',  NULL,               1,    'en_uso',        'Zona Cómputo'),
    ('CUB-01',  2, 'Cubículo 01',                   NULL,               6,    'disponible',    'Planta Baja'),
    ('CUB-02',  2, 'Cubículo 02',                   NULL,               6,    'en_uso',        'Planta Baja'),
    ('LIB-001', 5, 'Clean Code',                    'Robert C. Martin', NULL, 'disponible',    'Estante A1'),
    ('LIB-002', 5, 'Fundamentos de Bases de Datos', 'Silberschatz',     NULL, 'en_uso',        'Estante A2'),
    ('LIB-003', 5, 'Python Crash Course',           'Eric Matthes',     NULL, 'mantenimiento', 'Estante A1'),
    ('UTL-001', 6, 'Audífonos Sony WH',             NULL,               NULL, 'disponible',    'Recepción');

INSERT INTO user (user_id, full_name, user_type, gender, password, major, quarter, teacher_type, department_area, phone) VALUES
    (1001, 'Carlos Méndez',            'administrador',  NULL, 'admin123', NULL,   NULL, NULL,  NULL,   NULL),
    (5479, 'José Javier López Chávez', 'alumno',         'M',  '1234',     'TDSM', 4,    NULL,  NULL,   NULL),
    (5480, 'Ana Sofía Pérez',          'alumno',         'F',  '1234',     'CDIA', 3,    NULL,  NULL,   NULL),
    (5481, 'Diego Ruiz García',        'alumno',         'M',  '1234',     'IMT',  5,    NULL,  NULL,   NULL),
    (5482, 'Valeria Morales',          'alumno',         'F',  '1234',     'TMKT', 2,    NULL,  NULL,   NULL),
    (686,  'Laura Elena Torres',       'docente',        'F',  'doc123',   NULL,   NULL, 'PTC', NULL,   NULL),
    (2001, 'María Fernanda Cruz',      'administrativo', 'F',  'adm123',   NULL,   NULL, NULL,  'TICs', NULL),
    (9001, 'Roberto Hernández',        'externo',        NULL, NULL,       NULL,   NULL, NULL,  NULL,   '4491234567');

INSERT INTO active_usage (user_id, category_id, bar_code, attendees_count, starting_date, due_at) VALUES
    (5479, NULL, 'CUB-02',  3,  NOW() - INTERVAL 30 MINUTE,  NOW() + INTERVAL 90 MINUTE),
    (5480, NULL, 'PC-02',   1,  NOW() - INTERVAL 150 MINUTE, NOW() - INTERVAL 30 MINUTE),
    (5481, NULL, 'LIB-002', 1,  NOW() - INTERVAL 2 HOUR,     NOW() + INTERVAL 6 HOUR),
    (686,  4,    NULL,      15, NOW() - INTERVAL 40 MINUTE,  NOW() + INTERVAL 80 MINUTE);

INSERT INTO usage_history (user_id, category_id, bar_code, attendees_count, starting_date, due_at, end_date, close_reason, closed_by) VALUES
    (5479, NULL, 'CUB-01',  4, NOW() - INTERVAL 5 DAY, NOW() - INTERVAL 5 DAY + INTERVAL 2 HOUR, NOW() - INTERVAL 5 DAY + INTERVAL 110 MINUTE, 'completado',        1001),
    (5480, NULL, 'PC-01',   1, NOW() - INTERVAL 4 DAY, NOW() - INTERVAL 4 DAY + INTERVAL 2 HOUR, NOW() - INTERVAL 4 DAY + INTERVAL 2 HOUR,     'cierre_automatico', NULL),
    (5479, NULL, 'LIB-001', 1, NOW() - INTERVAL 3 DAY, NOW() - INTERVAL 3 DAY + INTERVAL 8 HOUR, NOW() - INTERVAL 3 DAY + INTERVAL 3 HOUR,     'completado',        1001),
    (5481, NULL, 'CUB-01',  3, NOW() - INTERVAL 2 DAY, NOW() - INTERVAL 2 DAY + INTERVAL 2 HOUR, NOW() - INTERVAL 2 DAY + INTERVAL 2 HOUR,     'cierre_automatico', NULL),
    (5482, 3,    NULL,      1, NOW() - INTERVAL 1 DAY, NOW() - INTERVAL 1 DAY + INTERVAL 3 HOUR, NOW() - INTERVAL 1 DAY + INTERVAL 95 MINUTE,  'completado',        1001),
    (5480, NULL, 'UTL-001', 1, NOW() - INTERVAL 1 DAY, NOW() - INTERVAL 1 DAY + INTERVAL 3 HOUR, NOW() - INTERVAL 1 DAY + INTERVAL 2 HOUR,     'completado',        1001),
    (2001, NULL, 'PC-01',   1, NOW() - INTERVAL 6 HOUR, NOW() - INTERVAL 4 HOUR,                 NOW() - INTERVAL 5 HOUR,                      'completado',        1001);

INSERT INTO lost_item (
    title, description, found_location,
    found_by_user_id, finder_name, found_date,
    status, delivered_at, delivered_by, delivered_to_user_id, delivered_to_name
) VALUES
    ('Termo metálico azul', 'Encontrado debajo de la mesa central, marca Yeti.', 'Sala General',
     5479, NULL, NOW() - INTERVAL 1 DAY,
     'en_custodia', NULL, NULL, NULL, NULL),

    ('Calculadora científica Casio', 'Modelo fx-991 con etiqueta borrosa atrás.', 'Cubículo 02',
     686, NULL, NOW() - INTERVAL 2 DAY,
     'en_custodia', NULL, NULL, NULL, NULL),

    ('Credencial UTR', 'Encontrada junto a la impresora de recepción.', 'Recepción',
     NULL, 'Personal de limpieza', NOW() - INTERVAL 4 HOUR,
     'en_custodia', NULL, NULL, NULL, NULL),

    ('Cargador USB-C blanco', 'Dejado conectado tras cerrar turno.', 'Cubículo 01',
     NULL, 'Personal de limpieza', NOW() - INTERVAL 3 DAY,
     'entregado', NOW() - INTERVAL 2 DAY, 1001, 5480, NULL);
     
     
     USE sigb_learning_commons;

INSERT INTO inventory_resource (bar_code, category_id, description_title, author, capacity, status, shelf_location) VALUES
    ('LIB-004', 5, 'Introducción a los Algoritmos',        'Thomas H. Cormen',    NULL, 'disponible', 'Estante A1'),
    ('LIB-005', 5, 'Redes de Computadoras',                'Andrew S. Tanenbaum', NULL, 'disponible', 'Estante B1'),
    ('LIB-006', 5, 'Sistemas Operativos Modernos',         'Andrew S. Tanenbaum', NULL, 'disponible', 'Estante B2'),
    ('LIB-007', 5, 'Ingeniería de Software',               'Ian Sommerville',     NULL, 'disponible', 'Estante A3'),
    ('LIB-008', 5, 'Cálculo de una Variable',              'James Stewart',       NULL, 'disponible', 'Estante C1'),
    ('LIB-009', 5, 'Probabilidad y Estadística',           'Ronald E. Walpole',   NULL, 'disponible', 'Estante C2'),
    ('LIB-010', 5, 'Fundamentos de Marketing',             'Philip Kotler',       NULL, 'disponible', 'Estante D1'),
    ('LIB-011', 5, 'Electrónica: Teoría de Circuitos',     'Robert L. Boylestad', NULL, 'disponible', 'Estante E1'),

    ('LIB-012', 5, 'Automate the Boring Stuff with Python','Al Sweigart',         NULL, 'en_uso',     'Estante A1'),
    ('LIB-013', 5, 'SQL Antipatterns',                     'Bill Karwin',         NULL, 'en_uso',     'Estante A2'),
    ('LIB-014', 5, 'Diseño de Bases de Datos',             'Thomas Connolly',     NULL, 'en_uso',     'Estante A2'),
    ('LIB-015', 5, 'Inteligencia Artificial: Un Enfoque',  'Stuart Russell',      NULL, 'en_uso',     'Estante B3'),
    ('LIB-016', 5, 'Álgebra Lineal y sus Aplicaciones',    'David C. Lay',        NULL, 'en_uso',     'Estante C1'),
    ('LIB-017', 5, 'Mecatrónica: Sistemas de Control',     'W. Bolton',           NULL, 'en_uso',     'Estante E2'),

    ('LIB-018', 5, 'Patrones de Diseño',                   'Erich Gamma',         NULL, 'extraviado', 'Estante A3');

INSERT INTO active_usage (user_id, category_id, bar_code, attendees_count, starting_date, due_at) VALUES
    (5479, NULL, 'LIB-012', 1, NOW() - INTERVAL 1 HOUR,   NOW() + INTERVAL 7 HOUR),
    (5480, NULL, 'LIB-013', 1, NOW() - INTERVAL 3 HOUR,   NOW() + INTERVAL 5 HOUR),
    (686,  NULL, 'LIB-014', 1, NOW() - INTERVAL 30 MINUTE, NOW() + INTERVAL 7 HOUR),

    (5481, NULL, 'LIB-015', 1, NOW() - INTERVAL 48 HOUR,  NOW() - INTERVAL 40 HOUR),
    (5482, NULL, 'LIB-016', 1, NOW() - INTERVAL 24 HOUR,  NOW() - INTERVAL 16 HOUR),
    (2001, NULL, 'LIB-017', 1, NOW() - INTERVAL 12 HOUR,  NOW() - INTERVAL 4 HOUR);

INSERT INTO usage_history (
    user_id, category_id, bar_code, attendees_count,
    starting_date, due_at, end_date, close_reason, closed_by
) VALUES
    (5479, NULL, 'LIB-004', 1, NOW() - INTERVAL 1 DAY, NOW() - INTERVAL 1 DAY + INTERVAL 8 HOUR, NOW() - INTERVAL 1 DAY + INTERVAL 4 HOUR,  'completado', 1001),
    (5480, NULL, 'LIB-005', 1, NOW() - INTERVAL 2 DAY, NOW() - INTERVAL 2 DAY + INTERVAL 8 HOUR, NOW() - INTERVAL 2 DAY + INTERVAL 6 HOUR,  'completado', 1001),
    (5482, NULL, 'LIB-008', 1, NOW() - INTERVAL 3 DAY, NOW() - INTERVAL 3 DAY + INTERVAL 8 HOUR, NOW() - INTERVAL 3 DAY + INTERVAL 5 HOUR,  'completado', 1001),
    (686,  NULL, 'LIB-009', 1, NOW() - INTERVAL 5 DAY, NOW() - INTERVAL 5 DAY + INTERVAL 8 HOUR, NOW() - INTERVAL 5 DAY + INTERVAL 7 HOUR,  'completado', 1001),

    (5481, NULL, 'LIB-006', 1, NOW() - INTERVAL 4 DAY, NOW() - INTERVAL 4 DAY + INTERVAL 8 HOUR, NOW() - INTERVAL 4 DAY + INTERVAL 12 HOUR, 'completado', 1001),
    (2001, NULL, 'LIB-010', 1, NOW() - INTERVAL 6 DAY, NOW() - INTERVAL 6 DAY + INTERVAL 8 HOUR, NOW() - INTERVAL 6 DAY + INTERVAL 15 HOUR, 'completado', 1001),

    (5479, NULL, 'LIB-007', 1, NOW() - INTERVAL 10 DAY, NOW() - INTERVAL 10 DAY + INTERVAL 8 HOUR, NOW() - INTERVAL 10 DAY + INTERVAL 5 HOUR, 'completado', 1001),
    (5480, NULL, 'LIB-011', 1, NOW() - INTERVAL 14 DAY, NOW() - INTERVAL 14 DAY + INTERVAL 8 HOUR, NOW() - INTERVAL 14 DAY + INTERVAL 9 HOUR, 'completado', 1001);