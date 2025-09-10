#!/usr/bin/env python3
"""
Скрипт для обновления данных ufc.stats
Аналог функции refresh_data() из R пакета ufc.stats
"""

import sys
import os
from datetime import datetime

# Добавляем корневую папку в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parsers.ufc_stats_importer import UFCStatsImporter
from database.config import init_database


def main():
    """Основная функция обновления данных"""
    print("🥊 UFC Stats Data Refresh")
    print("=" * 50)
    print(f"Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Инициализируем БД
    print("🔧 Инициализация базы данных...")
    init_database()
    print("✅ База данных инициализирована")
    print()
    
    # Создаем импортер
    importer = UFCStatsImporter()
    
    # Обновляем данные
    try:
        importer.refresh_data()
        print()
        print("🎉 Обновление данных завершено успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка при обновлении данных: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
