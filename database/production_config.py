#!/usr/bin/env python3
"""
Конфигурация базы данных для продакшена
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Получаем URL базы данных из переменных окружения
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://ufcranker:password@localhost/ufc_ranker")

# Создаем движок базы данных
if DATABASE_URL.startswith("sqlite"):
    # Для SQLite (разработка)
    engine = create_engine(
        DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )
else:
    # Для PostgreSQL (продакшен)
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False  # Отключаем логи SQL в продакшене
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Получение сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Инициализация базы данных"""
    from database.models import Base
    
    try:
        # Создаем все таблицы
        Base.metadata.create_all(bind=engine)
        print("✅ База данных инициализирована успешно")
        return True
    except Exception as e:
        print(f"❌ Ошибка инициализации базы данных: {e}")
        return False

def test_connection():
    """Тестирование подключения к базе данных"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        print("✅ Подключение к базе данных успешно")
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Тестирование подключения к базе данных...")
    if test_connection():
        print("🔄 Инициализация базы данных...")
        init_database()
    else:
        print("❌ Не удалось подключиться к базе данных")
