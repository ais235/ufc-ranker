#!/usr/bin/env python3
"""
Скрипт для восстановления базы данных UFC Ranker
"""

import os
import sqlite3
import sys
from datetime import datetime

def create_database_from_schema():
    """Создает новую базу данных из схемы"""
    
    db_path = "ufc_ranker_v2.db"
    schema_path = "database_backups/schema/database_schema.sql"
    
    # Проверяем существование файла схемы
    if not os.path.exists(schema_path):
        print(f"❌ Файл схемы {schema_path} не найден!")
        return False
    
    try:
        # Удаляем старую базу данных если она существует
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"🗑️ Удалена старая база данных: {db_path}")
        
        # Создаем новую базу данных
        conn = sqlite3.connect(db_path)
        
        # Читаем и выполняем схему
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Выполняем SQL команды
        conn.executescript(schema_sql)
        conn.commit()
        conn.close()
        
        print(f"✅ База данных создана: {db_path}")
        
        # Проверяем созданные таблицы
        verify_database_structure(db_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при создании базы данных: {e}")
        return False

def verify_database_structure(db_path):
    """Проверяет структуру созданной базы данных"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Получаем список таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("\n📋 Созданные таблицы:")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  ✅ {table_name}: {count} записей")
        
        # Проверяем индексы
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
        indexes = cursor.fetchall()
        
        print(f"\n🔍 Создано индексов: {len(indexes)}")
        
        conn.close()
        
    except Exception as e:
        print(f"⚠️ Ошибка при проверке структуры: {e}")

def run_parsers():
    """Запускает парсеры для заполнения базы данных"""
    print("\n🚀 Запуск парсеров для заполнения базы данных...")
    
    parsers = [
        "parse_ufc_rankings_correct.py",
        "parse_past_events.py", 
        "parse_scheduled_events.py",
        "parse_fighter_detailed_stats.py",
        "parse_fighter_fights.py",
        "parse_event_details.py"
    ]
    
    for parser in parsers:
        if os.path.exists(parser):
            print(f"📊 Запуск {parser}...")
            try:
                os.system(f"python {parser}")
                print(f"✅ {parser} завершен успешно")
            except Exception as e:
                print(f"❌ Ошибка в {parser}: {e}")
        else:
            print(f"⚠️ Парсер {parser} не найден")

def main():
    """Основная функция восстановления"""
    print("🔄 Восстановление базы данных UFC Ranker")
    print("=" * 50)
    
    # Создаем базу данных из схемы
    if not create_database_from_schema():
        return False
    
    # Спрашиваем пользователя о запуске парсеров
    response = input("\n❓ Запустить парсеры для заполнения данными? (y/n): ")
    if response.lower() in ['y', 'yes', 'да']:
        run_parsers()
        
        # Создаем резервную копию после заполнения
        print("\n💾 Создание резервной копии...")
        os.system("python database_backups/backup_database.py")
    
    print("\n✅ Восстановление базы данных завершено!")
    return True

if __name__ == "__main__":
    main()
