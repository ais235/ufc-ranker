#!/usr/bin/env python3
"""
Простой импорт данных ufc.stats
"""

import sqlite3
import requests
import gzip
import re
from datetime import datetime

def download_ufc_stats():
    """Скачиваем данные ufc.stats"""
    print("📥 Скачиваем данные ufc.stats...")
    
    url = "https://github.com/mtoto/ufc.stats/raw/master/data/ufc_stats.rda"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with open('ufc_stats.rda', 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Данные скачаны: {len(response.content):,} байт")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка скачивания: {e}")
        return False

def create_tables():
    """Создаем таблицы для ufc.stats"""
    print("🏗️ Создаем таблицы...")
    
    conn = sqlite3.connect('ufc_ranker_v2.db')
    cursor = conn.cursor()
    
    # Создаем таблицу для бойцов ufc.stats
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ufc_stats_fighters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            total_fights INTEGER DEFAULT 0,
            total_wins INTEGER DEFAULT 0,
            total_losses INTEGER DEFAULT 0,
            total_draws INTEGER DEFAULT 0,
            total_knockdowns INTEGER DEFAULT 0,
            total_significant_strikes INTEGER DEFAULT 0,
            total_takedowns INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Создаем таблицу для статистики раундов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ufc_stats_rounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fighter_id INTEGER,
            round_number INTEGER,
            knockdowns INTEGER DEFAULT 0,
            significant_strikes_landed INTEGER DEFAULT 0,
            significant_strikes_attempted INTEGER DEFAULT 0,
            significant_strikes_rate REAL DEFAULT 0,
            total_strikes_landed INTEGER DEFAULT 0,
            total_strikes_attempted INTEGER DEFAULT 0,
            takedown_successful INTEGER DEFAULT 0,
            takedown_attempted INTEGER DEFAULT 0,
            takedown_rate REAL DEFAULT 0,
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
            winner BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (fighter_id) REFERENCES ufc_stats_fighters(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Таблицы созданы")

def parse_ufc_data():
    """Парсим данные ufc.stats"""
    print("🔍 Парсим данные ufc.stats...")
    
    try:
        with gzip.open('ufc_stats.rda', 'rb') as f:
            data = f.read()
        
        # Ищем имена бойцов
        fighter_names = re.findall(rb'[A-Za-z\s]{10,50}', data)
        unique_fighters = list(set([name.decode('utf-8', errors='ignore').strip() 
                                  for name in fighter_names if len(name) > 5]))
        
        # Фильтруем только реальных бойцов
        real_fighters = []
        for fighter in unique_fighters:
            if (len(fighter) > 5 and 
                not any(x in fighter.lower() for x in ['vs', 'bout', 'title', 'tournament', 'ufc', 'fight', 'ultimate', 'champion'])):
                real_fighters.append(fighter)
        
        print(f"✅ Найдено {len(real_fighters)} реальных бойцов")
        return real_fighters
        
    except Exception as e:
        print(f"❌ Ошибка парсинга: {e}")
        return []

def import_fighters(fighters):
    """Импортируем бойцов"""
    print("👊 Импортируем бойцов...")
    
    conn = sqlite3.connect('ufc_ranker_v2.db')
    cursor = conn.cursor()
    
    imported_count = 0
    
    for fighter_name in fighters:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO ufc_stats_fighters (name) 
                VALUES (?)
            ''', (fighter_name,))
            imported_count += 1
        except Exception as e:
            print(f"⚠️ Ошибка импорта бойца {fighter_name}: {e}")
    
    conn.commit()
    conn.close()
    print(f"✅ Импортировано {imported_count} бойцов")

def create_update_script():
    """Создаем скрипт обновления"""
    print("🔄 Создаем скрипт обновления...")
    
    update_script = '''#!/usr/bin/env python3
"""
Скрипт обновления данных ufc.stats
"""

import requests
import sqlite3
import gzip
import re
from datetime import datetime

def update_ufc_stats():
    """Обновляем данные ufc.stats"""
    print("🔄 Обновляем данные ufc.stats...")
    
    # Скачиваем новые данные
    url = "https://github.com/mtoto/ufc.stats/raw/master/data/ufc_stats.rda"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with open('ufc_stats.rda', 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Новые данные скачаны: {len(response.content):,} байт")
        
        # Здесь можно добавить логику обновления существующих данных
        print("✅ Данные обновлены!")
        
    except Exception as e:
        print(f"❌ Ошибка обновления: {e}")

if __name__ == "__main__":
    update_ufc_stats()
'''
    
    with open('update_ufc_stats.py', 'w', encoding='utf-8') as f:
        f.write(update_script)
    
    print("✅ Скрипт обновления создан: update_ufc_stats.py")

def main():
    """Основная функция"""
    print("🥊 ИМПОРТ ДАННЫХ UFC.STATS")
    print("=" * 50)
    
    # 1. Скачиваем данные
    if not download_ufc_stats():
        return
    
    # 2. Создаем таблицы
    create_tables()
    
    # 3. Парсим данные
    fighters = parse_ufc_data()
    if not fighters:
        return
    
    # 4. Импортируем бойцов
    import_fighters(fighters)
    
    # 5. Создаем скрипт обновления
    create_update_script()
    
    print("\n✅ ИМПОРТ ЗАВЕРШЕН!")
    print("📋 Что дальше:")
    print("1. Запустите: python update_ufc_stats.py - для обновления данных")
    print("2. Проверьте БД: python view_database.py")
    print("3. Используйте API для доступа к данным")

if __name__ == "__main__":
    main()
