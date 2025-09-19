#!/usr/bin/env python3
"""
Главный скрипт для запуска всех парсеров UFC с улучшенной архитектурой
"""

import sys
import os
from typing import List, Dict, Any

# Добавляем корневую папку в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsers.ufc_rankings import UFCRankingsParser
from parsers.fighter_profiles import FighterProfilesParser
from parsers.upcoming_cards import UpcomingCardsParser
from parsers.ufc_official_api import UFCOfficialAPIParser
from parsers.ufc_stats_enhanced import UFCStatsEnhanced
from parsers.data_source_manager import DataSourceManager
from database.config import init_database


def run_all_parsers():
    """Запускает все парсеры по порядку с улучшенной архитектурой"""
    print("🥊 UFC Data Parser - Запуск всех парсеров (улучшенная версия)")
    print("=" * 60)
    
    # Инициализируем базу данных
    print("📊 Инициализация базы данных...")
    init_database()
    
    # Используем менеджер источников данных
    print("\n🔄 Инициализация менеджера источников данных...")
    manager = DataSourceManager()
    
    # Получаем все данные с приоритетных источников
    print("\n📥 Получение данных с приоритетных источников...")
    results = manager.update_all_data()
    
    # Показываем статистику
    print("\n📊 Статистика обновления:")
    for data_type, data in results.items():
        if isinstance(data, dict) and 'status' in data:
            print(f"  ✅ {data_type}: {data.get('status', 'unknown')}")
        elif isinstance(data, list):
            print(f"  ✅ {data_type}: {len(data)} записей")
        elif isinstance(data, dict):
            print(f"  ✅ {data_type}: {len(data)} категорий")
    
    # Показываем статус источников
    print("\n🔍 Статус источников данных:")
    sources_status = results.get('sources_status', {})
    for source_name, status in sources_status.items():
        enabled = "✅" if status.get('enabled') else "❌"
        success_rate = status.get('success_rate', 0)
        print(f"  {enabled} {source_name}: {success_rate:.1%} успешность")
    
    print("\n🎉 Все парсеры завершены успешно!")


def run_enhanced_parsers():
    """Запускает улучшенные парсеры с официальными источниками"""
    print("🥊 UFC Enhanced Parser - Официальные источники")
    print("=" * 50)
    
    init_database()
    
    # 1. Официальный UFC API
    print("\n1️⃣ Парсинг с официального UFC API...")
    official_parser = UFCOfficialAPIParser()
    official_data = official_parser.parse()
    
    # 2. Расширенная интеграция с ufc.stats
    print("\n2️⃣ Интеграция с ufc.stats...")
    stats_parser = UFCStatsEnhanced()
    stats_data = stats_parser.parse()
    
    print("\n🎉 Улучшенные парсеры завершены успешно!")
    print(f"📊 Официальные данные: {len(official_data)} источников")
    print(f"📈 Статистика ufc.stats: {len(stats_data)} наборов данных")


def run_rankings_only():
    """Запускает только парсер рейтингов"""
    print("🥊 UFC Rankings Parser")
    print("=" * 30)
    
    init_database()
    
    parser = UFCRankingsParser()
    rankings = parser.parse()
    
    print(f"\n✅ Парсинг рейтингов завершен!")
    print(f"📊 Обработано категорий: {len(rankings)}")


def run_profiles_only():
    """Запускает только парсер профилей"""
    print("🥊 UFC Profiles Parser")
    print("=" * 30)
    
    init_database()
    
    parser = FighterProfilesParser()
    parser.parse()
    
    print("\n✅ Обновление профилей завершено!")


def run_cards_only():
    """Запускает только парсер кардов"""
    print("🥊 UFC Cards Parser")
    print("=" * 30)
    
    init_database()
    
    parser = UpcomingCardsParser()
    cards = parser.parse()
    
    print(f"\n✅ Парсинг кардов завершен!")
    print(f"🎫 Обработано событий: {len(cards)}")


def main():
    """Главная функция"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "rankings":
            run_rankings_only()
        elif command == "profiles":
            run_profiles_only()
        elif command == "cards":
            run_cards_only()
        elif command == "all":
            run_all_parsers()
        elif command == "enhanced":
            run_enhanced_parsers()
        elif command == "official":
            # Только официальные источники
            print("🥊 UFC Official Sources Parser")
            init_database()
            official_parser = UFCOfficialAPIParser()
            official_parser.parse()
        elif command == "stats":
            # Только ufc.stats
            print("🥊 UFC Stats Parser")
            init_database()
            stats_parser = UFCStatsEnhanced()
            stats_parser.parse()
        else:
            print("❌ Неизвестная команда. Доступные команды:")
            print("  python main.py all       - запустить все парсеры (улучшенная версия)")
            print("  python main.py enhanced  - запустить улучшенные парсеры")
            print("  python main.py official  - только официальный UFC API")
            print("  python main.py stats     - только ufc.stats")
            print("  python main.py rankings  - только рейтинги")
            print("  python main.py profiles  - только профили")
            print("  python main.py cards     - только карды")
    else:
        # По умолчанию запускаем улучшенные парсеры
        run_enhanced_parsers()


if __name__ == "__main__":
    main()













