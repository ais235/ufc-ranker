#!/usr/bin/env python3
"""
Главный скрипт для запуска всех парсеров UFC
"""

import sys
import os
from typing import List

# Добавляем корневую папку в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsers.ufc_rankings import UFCRankingsParser
from parsers.fighter_profiles import FighterProfilesParser
from parsers.upcoming_cards import UpcomingCardsParser
from database.config import init_database


def run_all_parsers():
    """Запускает все парсеры по порядку"""
    print("🥊 UFC Data Parser - Запуск всех парсеров")
    print("=" * 50)
    
    # Инициализируем базу данных
    print("📊 Инициализация базы данных...")
    init_database()
    
    # 1. Парсинг рейтингов
    print("\n1️⃣ Парсинг рейтингов UFC...")
    rankings_parser = UFCRankingsParser()
    rankings = rankings_parser.parse()
    
    # 2. Обновление профилей бойцов
    print("\n2️⃣ Обновление профилей бойцов...")
    profiles_parser = FighterProfilesParser()
    profiles_parser.parse()
    
    # 3. Парсинг предстоящих кардов
    print("\n3️⃣ Парсинг предстоящих кардов...")
    cards_parser = UpcomingCardsParser()
    cards = cards_parser.parse()
    
    print("\n🎉 Все парсеры завершены успешно!")
    print(f"📊 Обработано категорий: {len(rankings)}")
    print(f"🎫 Обработано событий: {len(cards)}")


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
        else:
            print("❌ Неизвестная команда. Доступные команды:")
            print("  python main.py all       - запустить все парсеры")
            print("  python main.py rankings  - только рейтинги")
            print("  python main.py profiles  - только профили")
            print("  python main.py cards     - только карды")
    else:
        # По умолчанию запускаем все парсеры
        run_all_parsers()


if __name__ == "__main__":
    main()
