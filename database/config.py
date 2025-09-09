#!/usr/bin/env python3
"""
Конфигурация базы данных
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# Настройки БД
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ufc_ranker.db")

# Создаем движок БД
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Установите True для отладки SQL запросов
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Создает все таблицы в БД"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Получает сессию БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """Инициализирует базу данных"""
    create_tables()
    print("✅ База данных инициализирована")
