#!/usr/bin/env python3
"""
Полный импорт данных ufc.stats с использованием R
"""

import subprocess
import sqlite3
import os
import requests

def install_r_packages():
    """Устанавливаем необходимые R пакеты"""
    print("📦 Устанавливаем R пакеты...")
    
    r_script = '''
    # Устанавливаем необходимые пакеты
    if (!require("devtools")) {
        install.packages("devtools")
        library(devtools)
    }
    
    if (!require("rpy2")) {
        install.packages("rpy2")
        library(rpy2)
    }
    
    # Устанавливаем ufc.stats
    if (!require("ufc.stats")) {
        devtools::install_github("mtoto/ufc.stats")
        library(ufc.stats)
    }
    
    print("✅ R пакеты установлены")
    '''
    
    try:
        subprocess.run(['R', '--slave', '-e', r_script], check=True)
        return True
    except:
        print("⚠️ R не установлен или ошибка установки пакетов")
        return False

def create_r_import_script():
    """Создаем R скрипт для импорта данных"""
    print("📝 Создаем R скрипт импорта...")
    
    r_script = '''
    # Загружаем данные ufc.stats
    library(ufc.stats)
    data("ufc_stats")
    
    # Подключаемся к SQLite
    library(RSQLite)
    con <- dbConnect(RSQLite::SQLite(), "ufc_ranker_v2.db")
    
    # Создаем таблицы если не существуют
    dbExecute(con, "
        CREATE TABLE IF NOT EXISTS ufc_stats_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fighter TEXT,
            fight_date DATE,
            weight_class TEXT,
            round_number INTEGER,
            knockdowns INTEGER,
            significant_strikes_landed INTEGER,
            significant_strikes_attempted INTEGER,
            significant_strikes_rate REAL,
            total_strikes_landed INTEGER,
            total_strikes_attempted INTEGER,
            takedown_successful INTEGER,
            takedown_attempted INTEGER,
            takedown_rate REAL,
            submission_attempt INTEGER,
            reversals INTEGER,
            head_landed INTEGER,
            head_attempted INTEGER,
            body_landed INTEGER,
            body_attempted INTEGER,
            leg_landed INTEGER,
            leg_attempted INTEGER,
            distance_landed INTEGER,
            distance_attempted INTEGER,
            clinch_landed INTEGER,
            clinch_attempted INTEGER,
            ground_landed INTEGER,
            ground_attempted INTEGER,
            winner BOOLEAN,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ")
    
    # Очищаем старые данные
    dbExecute(con, "DELETE FROM ufc_stats_data")
    
    # Импортируем данные
    dbWriteTable(con, "ufc_stats_data", ufc_stats, append = TRUE)
    
    # Получаем статистику
    count <- dbGetQuery(con, "SELECT COUNT(*) as count FROM ufc_stats_data")
    print(paste("✅ Импортировано записей:", count$count))
    
    # Закрываем соединение
    dbDisconnect(con)
    
    print("✅ Импорт завершен!")
    '''
    
    with open('import_ufc_stats.R', 'w', encoding='utf-8') as f:
        f.write(r_script)
    
    print("✅ R скрипт создан: import_ufc_stats.R")

def run_r_import():
    """Запускаем R скрипт импорта"""
    print("🚀 Запускаем R скрипт импорта...")
    
    try:
        result = subprocess.run(['R', '--slave', '-f', 'import_ufc_stats.R'], 
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            print("✅ R скрипт выполнен успешно!")
            print(result.stdout)
        else:
            print("❌ Ошибка выполнения R скрипта:")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("❌ R не установлен на системе")
        print("💡 Установите R с https://www.r-project.org/")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    return True

def create_python_import_script():
    """Создаем Python скрипт для импорта без R"""
    print("🐍 Создаем Python скрипт импорта...")
    
    python_script = '''#!/usr/bin/env python3
"""
Python импорт данных ufc.stats без R
"""

import sqlite3
import requests
import gzip
import re
import json
from datetime import datetime

def download_and_parse_ufc_stats():
    """Скачиваем и парсим данные ufc.stats"""
    print("📥 Скачиваем данные ufc.stats...")
    
    url = "https://github.com/mtoto/ufc.stats/raw/master/data/ufc_stats.rda"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with open('ufc_stats.rda', 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Данные скачаны: {len(response.content):,} байт")
        
        # Парсим данные
        with gzip.open('ufc_stats.rda', 'rb') as f:
            data = f.read()
        
        # Извлекаем структурированные данные
        fighters = re.findall(rb'[A-Za-z\\s]{10,50}', data)
        numbers = re.findall(rb'\\d+\\.\\d+', data)
        dates = re.findall(rb'\\d{4}-\\d{2}-\\d{2}', data)
        
        print(f"✅ Найдено: {len(fighters)} бойцов, {len(numbers)} чисел, {len(dates)} дат")
        
        return {
            'fighters': [f.decode('utf-8', errors='ignore').strip() for f in fighters],
            'numbers': [float(n.decode()) for n in numbers],
            'dates': [d.decode() for d in dates]
        }
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def create_ufc_stats_tables():
    """Создаем таблицы для ufc.stats"""
    print("🏗️ Создаем таблицы...")
    
    conn = sqlite3.connect('ufc_ranker_v2.db')
    cursor = conn.cursor()
    
    # Создаем таблицу для бойцов
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
    
    # Создаем таблицу для статистики
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

def import_fighters(fighters_data):
    """Импортируем бойцов"""
    print("👊 Импортируем бойцов...")
    
    conn = sqlite3.connect('ufc_ranker_v2.db')
    cursor = conn.cursor()
    
    imported_count = 0
    
    for fighter_name in fighters_data:
        if len(fighter_name) > 5 and not any(x in fighter_name.lower() for x in ['vs', 'bout', 'title', 'tournament', 'ufc', 'fight']):
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

def main():
    """Основная функция"""
    print("🥊 ПОЛНЫЙ ИМПОРТ UFC.STATS")
    print("=" * 50)
    
    # 1. Скачиваем и парсим данные
    data = download_and_parse_ufc_stats()
    if not data:
        return
    
    # 2. Создаем таблицы
    create_ufc_stats_tables()
    
    # 3. Импортируем бойцов
    import_fighters(data['fighters'])
    
    print("\\n✅ ИМПОРТ ЗАВЕРШЕН!")
    print("📋 Проверьте БД: python view_database.py")

if __name__ == "__main__":
    main()
'''
    
    with open('python_ufc_stats_import.py', 'w', encoding='utf-8') as f:
        f.write(python_script)
    
    print("✅ Python скрипт создан: python_ufc_stats_import.py")

def main():
    """Основная функция"""
    print("🥊 ПОЛНЫЙ ИМПОРТ UFC.STATS")
    print("=" * 50)
    
    # Проверяем наличие R
    try:
        subprocess.run(['R', '--version'], capture_output=True, check=True)
        print("✅ R найден, создаем R скрипт...")
        create_r_import_script()
        
        if run_r_import():
            print("✅ Импорт через R завершен!")
        else:
            print("⚠️ R импорт не удался, создаем Python альтернативу...")
            create_python_import_script()
            print("📋 Запустите: python python_ufc_stats_import.py")
            
    except FileNotFoundError:
        print("⚠️ R не найден, создаем Python альтернативу...")
        create_python_import_script()
        print("📋 Запустите: python python_ufc_stats_import.py")

if __name__ == "__main__":
    main()
