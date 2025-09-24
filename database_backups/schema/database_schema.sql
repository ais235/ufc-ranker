-- Схема базы данных UFC Ranker
-- Создано: 2024-09-24
-- Версия: 2.0

-- Таблица весовых категорий
CREATE TABLE IF NOT EXISTS weight_classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name_ru TEXT NOT NULL,
    name_en TEXT NOT NULL,
    full_name TEXT,
    weight_limit REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица бойцов
CREATE TABLE IF NOT EXISTS fighters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    name_en TEXT,
    nickname TEXT,
    weight_class TEXT,
    height_cm INTEGER,
    reach_cm INTEGER,
    birth_date DATE,
    country TEXT,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    draws INTEGER DEFAULT 0,
    no_contests INTEGER DEFAULT 0,
    ufc_wins INTEGER DEFAULT 0,
    ufc_losses INTEGER DEFAULT 0,
    ufc_draws INTEGER DEFAULT 0,
    ufc_no_contests INTEGER DEFAULT 0,
    fighting_out_of TEXT,
    years_active TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица событий UFC
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    event_number TEXT,
    date DATE,
    location TEXT,
    venue TEXT,
    event_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица боев
CREATE TABLE IF NOT EXISTS fights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fighter1_id INTEGER,
    fighter2_id INTEGER,
    event_id INTEGER,
    weight_class TEXT,
    method TEXT,
    round INTEGER,
    time TEXT,
    winner_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fighter1_id) REFERENCES fighters(id),
    FOREIGN KEY (fighter2_id) REFERENCES fighters(id),
    FOREIGN KEY (event_id) REFERENCES events(id),
    FOREIGN KEY (winner_id) REFERENCES fighters(id)
);

-- Таблица рейтингов
CREATE TABLE IF NOT EXISTS rankings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fighter_id INTEGER,
    weight_class TEXT NOT NULL,
    position INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fighter_id) REFERENCES fighters(id)
);

-- Таблица предстоящих боев
CREATE TABLE IF NOT EXISTS upcoming_fights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fighter1_id INTEGER,
    fighter2_id INTEGER,
    event_id INTEGER,
    weight_class TEXT,
    scheduled_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fighter1_id) REFERENCES fighters(id),
    FOREIGN KEY (fighter2_id) REFERENCES fighters(id),
    FOREIGN KEY (event_id) REFERENCES events(id)
);

-- Таблица записей боев бойцов
CREATE TABLE IF NOT EXISTS fight_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fighter_id INTEGER,
    wins_by_ko INTEGER DEFAULT 0,
    losses_by_ko INTEGER DEFAULT 0,
    wins_by_submission INTEGER DEFAULT 0,
    losses_by_submission INTEGER DEFAULT 0,
    wins_by_decision INTEGER DEFAULT 0,
    losses_by_decision INTEGER DEFAULT 0,
    wins_by_dq INTEGER DEFAULT 0,
    losses_by_dq INTEGER DEFAULT 0,
    avg_fight_time_seconds INTEGER DEFAULT 0,
    total_fights INTEGER DEFAULT 0,
    total_nc INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fighter_id) REFERENCES fighters(id)
);

-- Таблица детальной информации о боях
CREATE TABLE IF NOT EXISTS fighter_fights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fighter_id INTEGER,
    opponent_name TEXT,
    result TEXT,
    method TEXT,
    round INTEGER,
    time TEXT,
    event_name TEXT,
    date DATE,
    weight_class TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fighter_id) REFERENCES fighters(id)
);

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_fighters_name ON fighters(name);
CREATE INDEX IF NOT EXISTS idx_fighters_weight_class ON fighters(weight_class);
CREATE INDEX IF NOT EXISTS idx_fights_fighter1 ON fights(fighter1_id);
CREATE INDEX IF NOT EXISTS idx_fights_fighter2 ON fights(fighter2_id);
CREATE INDEX IF NOT EXISTS idx_fights_event ON fights(event_id);
CREATE INDEX IF NOT EXISTS idx_rankings_weight_class ON rankings(weight_class);
CREATE INDEX IF NOT EXISTS idx_rankings_position ON rankings(position);

-- Триггеры для автоматического обновления updated_at
CREATE TRIGGER IF NOT EXISTS update_fighters_timestamp 
    AFTER UPDATE ON fighters
    BEGIN
        UPDATE fighters SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_events_timestamp 
    AFTER UPDATE ON events
    BEGIN
        UPDATE events SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_fights_timestamp 
    AFTER UPDATE ON fights
    BEGIN
        UPDATE fights SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_rankings_timestamp 
    AFTER UPDATE ON rankings
    BEGIN
        UPDATE rankings SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_upcoming_fights_timestamp 
    AFTER UPDATE ON upcoming_fights
    BEGIN
        UPDATE upcoming_fights SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_fight_records_timestamp 
    AFTER UPDATE ON fight_records
    BEGIN
        UPDATE fight_records SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

-- Вставка данных весовых категорий
INSERT OR IGNORE INTO weight_classes (name_ru, name_en, full_name, weight_limit) VALUES
('Тяжелый вес', 'Heavyweight', 'Heavyweights', 265),
('Полутяжелый вес', 'Light Heavyweight', 'Light Heavyweights', 205),
('Средний вес', 'Middleweight', 'Middleweights', 185),
('Полусредний вес', 'Welterweight', 'Welterweights', 170),
('Легкий вес', 'Lightweight', 'Lightweights', 155),
('Полулегкий вес', 'Featherweight', 'Featherweights', 145),
('Легчайший вес', 'Bantamweight', 'Bantamweights', 135),
('Наилегчайший вес', 'Flyweight', 'Flyweights', 125),
('Женский легчайший вес', 'Women''s Bantamweight', 'Women''s Bantamweights', 135),
('Женский наилегчайший вес', 'Women''s Flyweight', 'Women''s Flyweights', 125),
('Женский минимальный вес', 'Women''s Strawweight', 'Women''s Strawweights', 115);
