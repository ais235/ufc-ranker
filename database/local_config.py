#!/usr/bin/env python3
"""
Локальная конфигурация для разработки без Docker
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base

# Настройки для локальной разработки
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./ufc_ranker.db')

# Создаем движок SQLite с оптимизациями
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Логирование SQL запросов
    pool_pre_ping=True,
    connect_args={
        "check_same_thread": False  # Для SQLite
    } if "sqlite" in DATABASE_URL else {}
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_database():
    """Инициализирует базу данных"""
    try:
        # Создаем все таблицы
        Base.metadata.create_all(bind=engine)
        print("✅ База данных инициализирована")
        
        # Создаем индексы для оптимизации
        create_indexes()
        
    except Exception as e:
        print(f"❌ Ошибка при инициализации базы данных: {e}")
        raise


def create_indexes():
    """Создает индексы для оптимизации запросов"""
    try:
        with engine.connect() as conn:
            # Индексы для таблицы fighters
            conn.execute("CREATE INDEX IF NOT EXISTS idx_fighters_name_ru ON fighters(name_ru)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_fighters_country ON fighters(country)")
            
            # Индексы для таблицы rankings
            conn.execute("CREATE INDEX IF NOT EXISTS idx_rankings_weight_class_id ON rankings(weight_class_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_rankings_rank_position ON rankings(rank_position)")
            
            # Индексы для таблицы events
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_date ON events(date)")
            
            # Индексы для таблицы fights
            conn.execute("CREATE INDEX IF NOT EXISTS idx_fights_fighter1_id ON fights(fighter1_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_fights_fighter2_id ON fights(fighter2_id)")
            
        print("✅ Индексы созданы успешно")
        
    except Exception as e:
        print(f"❌ Ошибка при создании индексов: {e}")


def get_db():
    """Получает сессию базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    """Тестирует подключение к базе данных"""
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ Подключение к базе данных успешно")
            return True
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        return False


if __name__ == "__main__":
    # Тестируем подключение и инициализируем БД
    if test_connection():
        init_database()
        print("✅ Локальная конфигурация готова")
