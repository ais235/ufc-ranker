-- АКТУАЛЬНАЯ СХЕМА БАЗЫ ДАННЫХ UFC RANKER
-- Создано: 2024-09-24
-- Версия: 2.1 (соответствует models.py)
-- Источник: database/models.py

-- Таблица весовых категорий
CREATE TABLE IF NOT EXISTS weight_classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name_ru TEXT NOT NULL,
    name_en TEXT,
    weight_min INTEGER,
    weight_max INTEGER,
    gender TEXT DEFAULT 'male',
    is_p4p BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Таблица бойцов
CREATE TABLE IF NOT EXISTS fighters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name_ru TEXT NOT NULL,
    name_en TEXT,
    nickname TEXT,
    country TEXT,
    country_flag_url TEXT,
    image_url TEXT,
    profile_url TEXT,
    height INTEGER,
    weight INTEGER,
    reach INTEGER,
    age INTEGER,
    birth_date DATE,
    weight_class TEXT,
    win INTEGER DEFAULT 0,
    draw INTEGER DEFAULT 0,
    lose INTEGER DEFAULT 0,
    career TEXT,
    full_name TEXT,
    birth_place TEXT,
    stance TEXT,
    team TEXT,
    trainer TEXT,
    belt_rank TEXT,
    years_active TEXT,
    current_division TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Таблица рейтингов
CREATE TABLE IF NOT EXISTS rankings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fighter_id INTEGER NOT NULL,
    weight_class_id INTEGER NOT NULL,
    rank_position INTEGER,
    is_champion BOOLEAN DEFAULT 0,
    rank_change INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fighter_id) REFERENCES fighters(id),
    FOREIGN KEY (weight_class_id) REFERENCES weight_classes(id)
);

-- Таблица боевых рекордов
CREATE TABLE IF NOT EXISTS fight_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fighter_id INTEGER NOT NULL UNIQUE,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    draws INTEGER DEFAULT 0,
    no_contests INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fighter_id) REFERENCES fighters(id)
);

-- Таблица предстоящих боев
CREATE TABLE IF NOT EXISTS upcoming_fights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fighter1_id INTEGER NOT NULL,
    fighter2_id INTEGER NOT NULL,
    weight_class_id INTEGER NOT NULL,
    event_name TEXT,
    event_date DATE,
    location TEXT,
    is_main_event BOOLEAN DEFAULT 0,
    is_title_fight BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fighter1_id) REFERENCES fighters(id),
    FOREIGN KEY (fighter2_id) REFERENCES fighters(id),
    FOREIGN KEY (weight_class_id) REFERENCES weight_classes(id)
);

-- Таблица событий UFC
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    date DATE,
    location TEXT,
    venue TEXT,
    description TEXT,
    image_url TEXT,
    is_upcoming BOOLEAN DEFAULT 1,
    attendance INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Таблица боев UFC
CREATE TABLE IF NOT EXISTS fights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    fighter1_id INTEGER NOT NULL,
    fighter2_id INTEGER NOT NULL,
    weight_class_id INTEGER NOT NULL,
    scheduled_rounds INTEGER DEFAULT 3,
    result TEXT,
    winner_id INTEGER,
    fight_date DATE,
    is_title_fight BOOLEAN DEFAULT 0,
    is_main_event BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id),
    FOREIGN KEY (fighter1_id) REFERENCES fighters(id),
    FOREIGN KEY (fighter2_id) REFERENCES fighters(id),
    FOREIGN KEY (winner_id) REFERENCES fighters(id),
    FOREIGN KEY (weight_class_id) REFERENCES weight_classes(id)
);

-- Таблица детальной статистики боев
CREATE TABLE IF NOT EXISTS fight_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fight_id INTEGER NOT NULL,
    fighter_id INTEGER NOT NULL,
    round_number INTEGER NOT NULL,
    knockdowns INTEGER DEFAULT 0,
    significant_strikes_landed INTEGER DEFAULT 0,
    significant_strikes_attempted INTEGER DEFAULT 0,
    significant_strikes_rate REAL DEFAULT 0.0,
    total_strikes_landed INTEGER DEFAULT 0,
    total_strikes_attempted INTEGER DEFAULT 0,
    takedown_successful INTEGER DEFAULT 0,
    takedown_attempted INTEGER DEFAULT 0,
    takedown_rate REAL DEFAULT 0.0,
    submission_attempt INTEGER DEFAULT 0,
    reversals INTEGER DEFAULT 0,
    head_landed INTEGER DEFAULT 0,
    head_attempted INTEGER DEFAULT 0,
    body_landed INTEGER DEFAULT 0,
    body_attempted INTEGER DEFAULT 0,
    leg_landed INTEGER DEFAULT 0,
    leg_attempted INTEGER DEFAULT 0,
    distance_landed INTEGER DEFAULT 0,
    distance_attempted INTEGER DEFAULT 0,
    clinch_landed INTEGER DEFAULT 0,
    clinch_attempted INTEGER DEFAULT 0,
    ground_landed INTEGER DEFAULT 0,
    ground_attempted INTEGER DEFAULT 0,
    result TEXT,
    last_round BOOLEAN DEFAULT 0,
    time TEXT,
    winner TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fight_id) REFERENCES fights(id),
    FOREIGN KEY (fighter_id) REFERENCES fighters(id)
);

-- Индексы для оптимизации
CREATE INDEX IF NOT EXISTS idx_fighters_name_ru ON fighters(name_ru);
CREATE INDEX IF NOT EXISTS idx_fighters_name_en ON fighters(name_en);
CREATE INDEX IF NOT EXISTS idx_fighters_weight_class ON fighters(weight_class);
CREATE INDEX IF NOT EXISTS idx_rankings_fighter ON rankings(fighter_id);
CREATE INDEX IF NOT EXISTS idx_rankings_weight_class ON rankings(weight_class_id);
CREATE INDEX IF NOT EXISTS idx_rankings_position ON rankings(rank_position);
CREATE INDEX IF NOT EXISTS idx_fights_event ON fights(event_id);
CREATE INDEX IF NOT EXISTS idx_fights_fighter1 ON fights(fighter1_id);
CREATE INDEX IF NOT EXISTS idx_fights_fighter2 ON fights(fighter2_id);
CREATE INDEX IF NOT EXISTS idx_fights_date ON fights(fight_date);
CREATE INDEX IF NOT EXISTS idx_fight_stats_fight ON fight_stats(fight_id);
CREATE INDEX IF NOT EXISTS idx_fight_stats_fighter ON fight_stats(fighter_id);

-- Триггеры для обновления updated_at
CREATE TRIGGER IF NOT EXISTS update_fighters_timestamp 
    AFTER UPDATE ON fighters
    BEGIN
        UPDATE fighters SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_rankings_timestamp 
    AFTER UPDATE ON rankings
    BEGIN
        UPDATE rankings SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_fight_records_timestamp 
    AFTER UPDATE ON fight_records
    BEGIN
        UPDATE fight_records SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_upcoming_fights_timestamp 
    AFTER UPDATE ON upcoming_fights
    BEGIN
        UPDATE upcoming_fights SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
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

CREATE TRIGGER IF NOT EXISTS update_fight_stats_timestamp 
    AFTER UPDATE ON fight_stats
    BEGIN
        UPDATE fight_stats SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

-- Вставка данных весовых категорий
INSERT OR IGNORE INTO weight_classes (name_ru, name_en, weight_min, weight_max, gender) VALUES
('Тяжелый вес', 'Heavyweight', 93, 120, 'male'),
('Полутяжелый вес', 'Light Heavyweight', 84, 93, 'male'),
('Средний вес', 'Middleweight', 77, 84, 'male'),
('Полусредний вес', 'Welterweight', 70, 77, 'male'),
('Легкий вес', 'Lightweight', 66, 70, 'male'),
('Полулегкий вес', 'Featherweight', 61, 66, 'male'),
('Легчайший вес', 'Bantamweight', 57, 61, 'male'),
('Наилегчайший вес', 'Flyweight', 52, 57, 'male'),
('Женский легчайший вес', 'Women''s Bantamweight', 57, 61, 'female'),
('Женский наилегчайший вес', 'Women''s Flyweight', 52, 57, 'female'),
('Женский минимальный вес', 'Women''s Strawweight', 48, 52, 'female');
