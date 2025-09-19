#!/usr/bin/env python3
"""
Конфигурация PostgreSQL для UFC Ranker
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from database.models import Base

# Настройки PostgreSQL
POSTGRES_USER = os.getenv('POSTGRES_USER', 'ufc_ranker')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'ufc_ranker_password')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'ufc_ranker')

# URL подключения к PostgreSQL
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Настройки Redis
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_DB = int(os.getenv('REDIS_DB', '0'))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')

# URL подключения к Redis
REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}" if REDIS_PASSWORD else f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# Создаем движок PostgreSQL с оптимизациями
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,  # Количество соединений в пуле
    max_overflow=30,  # Максимальное количество дополнительных соединений
    pool_pre_ping=True,  # Проверка соединений перед использованием
    pool_recycle=3600,  # Переиспользование соединений каждый час
    echo=False,  # Логирование SQL запросов (включить для отладки)
    connect_args={
        "options": "-c timezone=UTC"  # Устанавливаем UTC временную зону
    }
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_database():
    """Инициализирует базу данных PostgreSQL"""
    try:
        # Создаем все таблицы
        Base.metadata.create_all(bind=engine)
        print("✅ База данных PostgreSQL инициализирована")
        
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
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_fighters_name_ru 
                ON fighters(name_ru);
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_fighters_country 
                ON fighters(country);
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_fighters_weight_class 
                ON fighters(weight_class);
            """)
            
            # Индексы для таблицы rankings
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_rankings_weight_class_id 
                ON rankings(weight_class_id);
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_rankings_rank_position 
                ON rankings(rank_position);
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_rankings_is_champion 
                ON rankings(is_champion);
            """)
            
            # Индексы для таблицы events
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_date 
                ON events(date);
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_is_upcoming 
                ON events(is_upcoming);
            """)
            
            # Индексы для таблицы fights
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_fights_event_id 
                ON fights(event_id);
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_fights_fighter1_id 
                ON fights(fighter1_id);
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_fights_fighter2_id 
                ON fights(fighter2_id);
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_fights_fight_date 
                ON fights(fight_date);
            """)
            
            # Индексы для таблицы fight_stats
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_fight_stats_fight_id 
                ON fight_stats(fight_id);
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_fight_stats_fighter_id 
                ON fight_stats(fighter_id);
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_fight_stats_round_number 
                ON fight_stats(round_number);
            """)
            
            # Составные индексы для часто используемых запросов
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_rankings_weight_class_rank 
                ON rankings(weight_class_id, rank_position);
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_fights_fighters 
                ON fights(fighter1_id, fighter2_id);
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_fight_stats_fight_round 
                ON fight_stats(fight_id, round_number);
            """)
            
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
            print("✅ Подключение к PostgreSQL успешно")
            return True
    except Exception as e:
        print(f"❌ Ошибка подключения к PostgreSQL: {e}")
        return False


def get_database_stats():
    """Возвращает статистику базы данных"""
    try:
        with engine.connect() as conn:
            # Размер базы данных
            size_result = conn.execute("""
                SELECT pg_size_pretty(pg_database_size(current_database())) as size;
            """).fetchone()
            
            # Количество записей в каждой таблице
            tables = ['fighters', 'weight_classes', 'rankings', 'events', 'fights', 'fight_stats']
            table_stats = {}
            
            for table in tables:
                count_result = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
                table_stats[table] = count_result[0] if count_result else 0
            
            return {
                'database_size': size_result[0] if size_result else 'Unknown',
                'table_counts': table_stats
            }
            
    except Exception as e:
        print(f"❌ Ошибка при получении статистики БД: {e}")
        return None


if __name__ == "__main__":
    # Тестируем подключение и инициализируем БД
    if test_connection():
        init_database()
        stats = get_database_stats()
        if stats:
            print(f"📊 Статистика базы данных:")
            print(f"  Размер: {stats['database_size']}")
            for table, count in stats['table_counts'].items():
                print(f"  {table}: {count} записей")

