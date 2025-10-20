#!/usr/bin/env python3
"""
Миграционный скрипт для исправления схемы БД
"""

import shutil
import os
from datetime import datetime
from database.config import init_database

def create_backup():
    """Создает бекап БД"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'ufc_ranker_v2_backup_migration_{timestamp}.db'
    shutil.copy2('ufc_ranker_v2.db', backup_name)
    print(f'Бекап создан: {backup_name}')
    return backup_name

def test_database():
    """Тестирует БД после миграции"""
    try:
        from database.config import SessionLocal
        from database.models import Fighter, Event, Fight, UpcomingFight
        
        db = SessionLocal()
        
        # Тест бойцов
        fighters = db.query(Fighter).limit(3).all()
        print(f'Бойцы: {len(fighters)} записей')
        if fighters:
            print(f'   Пример: {fighters[0].name_ru} - {fighters[0].wins}-{fighters[0].losses}-{fighters[0].draws}')
        
        # Тест событий
        events = db.query(Event).limit(3).all()
        print(f'События: {len(events)} записей')
        if events:
            print(f'   Пример: {events[0].name}')
        
        # Тест боев
        fights = db.query(Fight).limit(3).all()
        print(f'Бои: {len(fights)} записей')
        if fights:
            print(f'   Пример: {fights[0].fighter1_name} vs {fights[0].fighter2_name}')
        
        # Тест предстоящих боев
        upcoming = db.query(UpcomingFight).limit(3).all()
        print(f'Предстоящие бои: {len(upcoming)} записей')
        
        db.close()
        return True
        
    except Exception as e:
        print(f'Ошибка тестирования БД: {e}')
        return False

def main():
    """Основная функция миграции"""
    print("Начинаем миграцию БД...")
    
    # 1. Создаем бекап
    backup_file = create_backup()
    
    # 2. Инициализируем БД (создаем таблицы если нужно)
    print("Инициализируем БД...")
    init_database()
    
    # 3. Тестируем БД
    print("Тестируем БД...")
    if test_database():
        print("Миграция успешно завершена!")
        print(f"Бекап сохранен как: {backup_file}")
    else:
        print("Ошибка миграции!")
        print(f"Для восстановления используйте: {backup_file}")

if __name__ == "__main__":
    main()
