
DROP DATABASE IF EXISTS sigb_learning_commons;
CREATE DATABASE sigb_learning_commons
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE sigb_learning_commons;

-- CATEGORY
CREATE TABLE category (
    category_id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name_category            VARCHAR(60) NOT NULL UNIQUE,
    maximum_time_minute      INT UNSIGNED NOT NULL,
    requires_physical_return BOOLEAN NOT NULL DEFAULT FALSE,
    created_at               TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at               TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT chk_category_max_time CHECK (maximum_time_minute > 0)
);

--INVENTORY_RESOURCE
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

--  SANCTION
CREATE TABLE sanction (
    sanction_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id     INT UNSIGNED NOT NULL,
    reason      VARCHAR(255) NOT NULL,
    started_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ends_at     DATETIME NOT NULL,
    applied_by  INT UNSIGNED NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_sanction_user
        FOREIGN KEY (user_id) REFERENCES user(user_id)
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_sanction_applied_by
        FOREIGN KEY (applied_by) REFERENCES user(user_id)
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT chk_sanction_dates CHECK (ends_at > started_at)
);

--  ACTIVE_USAGE
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

--  USAGE_HISTORY
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

-- INCIDENT_REPORT
CREATE TABLE incident_report (
    incident_id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    bar_code             VARCHAR(40) NULL,
    incident_type        ENUM('falla_equipo', 'objeto_perdido', 'libro_danado') NOT NULL,
    title                VARCHAR(120) NOT NULL,
    incident_description TEXT NOT NULL,
    incident_location    VARCHAR(100) NULL,
    reported_by_user_id  INT UNSIGNED NULL,
    reporter_name        VARCHAR(120) NULL,
    image_path           VARCHAR(255) NULL,
    report_date          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status_resolution    ENUM('pendiente', 'en_custodia', 'resuelto', 'entregado') NOT NULL,
    resolved_at          DATETIME NULL,
    resolved_by          INT UNSIGNED NULL,
    delivered_to_user_id INT UNSIGNED NULL,
    delivered_to_name    VARCHAR(120) NULL,
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_incident_resource
        FOREIGN KEY (bar_code) REFERENCES inventory_resource(bar_code)
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_incident_reported_by
        FOREIGN KEY (reported_by_user_id) REFERENCES user(user_id)
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_incident_resolved_by
        FOREIGN KEY (resolved_by) REFERENCES user(user_id)
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_incident_delivered_to
        FOREIGN KEY (delivered_to_user_id) REFERENCES user(user_id)
        ON DELETE RESTRICT ON UPDATE RESTRICT,

    CONSTRAINT chk_incident_reporter CHECK (
        reported_by_user_id IS NOT NULL OR reporter_name IS NOT NULL
    ),
    CONSTRAINT chk_incident_barcode_coherence CHECK (
        (incident_type = 'objeto_perdido' AND bar_code IS NULL) OR
        (incident_type <> 'objeto_perdido' AND bar_code IS NOT NULL)
    ),
    CONSTRAINT chk_incident_status_by_type CHECK (
        (incident_type = 'objeto_perdido' AND status_resolution IN ('en_custodia', 'entregado')) OR
        (incident_type <> 'objeto_perdido' AND status_resolution IN ('pendiente', 'resuelto'))
    ),
    CONSTRAINT chk_incident_resolution_info CHECK (
        (status_resolution IN ('resuelto', 'entregado')
            AND resolved_at IS NOT NULL
            AND resolved_at >= report_date
            AND resolved_by IS NOT NULL) OR
        (status_resolution IN ('pendiente', 'en_custodia')
            AND resolved_at IS NULL
            AND resolved_by IS NULL)
    ),
    CONSTRAINT chk_incident_delivery_info CHECK (
        (status_resolution = 'entregado'
            AND (delivered_to_user_id IS NOT NULL OR delivered_to_name IS NOT NULL)) OR
        (status_resolution <> 'entregado'
            AND delivered_to_user_id IS NULL
            AND delivered_to_name IS NULL)
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

INSERT INTO sanction (user_id, reason, started_at, ends_at, applied_by) VALUES
    (5481, 'Devolución tardía de libro', NOW() - INTERVAL 2 DAY, NOW() + INTERVAL 5 DAY, 1001);


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

INSERT INTO incident_report (
    bar_code, incident_type, title, incident_description, incident_location,
    reported_by_user_id, reporter_name, image_path, report_date,
    status_resolution, resolved_at, resolved_by, delivered_to_user_id, delivered_to_name
) VALUES
    (NULL, 'objeto_perdido', 'Termo metálico azul', 'Encontrado debajo de la mesa central.', 'Sala General',
     5479, NULL, NULL, NOW() - INTERVAL 1 DAY,
     'en_custodia', NULL, NULL, NULL, NULL),

    (NULL, 'objeto_perdido', 'Cargador USB-C blanco', 'Dejado conectado tras cerrar turno.', 'Cubículo 01',
     NULL, 'Personal de limpieza', NULL, NOW() - INTERVAL 3 DAY,
     'entregado', NOW() - INTERVAL 2 DAY, 1001, 5480, NULL),

    ('PC-01', 'falla_equipo', 'Monitor parpadea', 'El cable HDMI parece flojo al mover la pantalla.', 'Zona Cómputo',
     686, NULL, NULL, NOW() - INTERVAL 5 HOUR,
     'pendiente', NULL, NULL, NULL, NULL),

    ('LIB-003', 'libro_danado', 'Portada despegada', 'Lomo dañado al recibir devolución; enviado a reparación.', 'Recepción',
     1001, NULL, NULL, NOW() - INTERVAL 4 DAY,
     'resuelto', NOW() - INTERVAL 1 DAY, 1001, NULL, NULL);