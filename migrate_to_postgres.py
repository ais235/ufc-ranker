#!/usr/bin/env python3
"""
Миграция данных из SQLite в PostgreSQL
"""

import sqlite3
import pandas as pd
from sqlalchemy import create_engine
import os
import sys

def migrate_database():
    """Мигрирует данные из SQLite в PostgreSQL"""
    
    # Подключение к SQLite
    sqlite_path = "ufc_ranker_v2.db"
    if not os.path.exists(sqlite_path):
        print(f"❌ Файл {sqlite_path} не найден!")
        return False
    
    sqlite_conn = sqlite3.connect(sqlite_path)
    print(f"✅ Подключен к SQLite: {sqlite_path}")
    
    # Подключение к PostgreSQL
    database_url = os.environ.get("DATABASE_URL", "postgresql://ufcranker:password@localhost/ufc_ranker")
    
    try:
        pg_engine = create_engine(database_url)
        pg_engine.connect()
        print(f"✅ Подключен к PostgreSQL")
    except Exception as e:
        print(f"❌ Ошибка подключения к PostgreSQL: {e}")
        return False
    
    # Список таблиц для миграции
    tables = [
        'weight_classes',
        'fighters', 
        'rankings',
        'events',
        'fights',
        'fight_records',
        'upcoming_fights',
        'fight_stats'
    ]
    
    migrated_count = 0
    
    for table in tables:
        try:
            # Проверяем существует ли таблица в SQLite
            cursor = sqlite_conn.cursor()
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if not cursor.fetchone():
                print(f"⚠️ Таблица {table} не найдена в SQLite, пропускаем")
                continue
            
            # Читаем данные из SQLite
            df = pd.read_sql_query(f"SELECT * FROM {table}", sqlite_conn)
            
            if len(df) == 0:
                print(f"⚠️ Таблица {table} пуста, пропускаем")
                continue
            
            # Записываем в PostgreSQL
            df.to_sql(table, pg_engine, if_exists='replace', index=False)
            print(f"✅ Мигрирована таблица {table}: {len(df)} записей")
            migrated_count += 1
            
        except Exception as e:
            print(f"❌ Ошибка миграции таблицы {table}: {e}")
    
    sqlite_conn.close()
    
    print(f"\n🎉 Миграция завершена! Обработано таблиц: {migrated_count}")
    return True

if __name__ == "__main__":
    print("🔄 Начинаем миграцию базы данных...")
    success = migrate_database()
    
    if success:
        print("✅ Миграция выполнена успешно!")
    else:
        print("❌ Миграция завершилась с ошибками!")
        sys.exit(1)
