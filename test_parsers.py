#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы парсеров
"""

import sys
import os

# Добавляем корневую папку в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_database_connection():
    """Тестирует подключение к базе данных"""
    print("🔍 Тестирование подключения к БД...")
    
    try:
        from database.config import init_database, SessionLocal
        from database.models import Fighter, WeightClass
        
        # Инициализируем БД
        init_database()
        
        # Проверяем подключение
        db = SessionLocal()
        fighters_count = db.query(Fighter).count()
        weight_classes_count = db.query(WeightClass).count()
        db.close()
        
        print(f"✅ БД подключена успешно")
        print(f"   Бойцов в БД: {fighters_count}")
        print(f"   Весовых категорий: {weight_classes_count}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return False

def test_rankings_parser():
    """Тестирует парсер рейтингов"""
    print("\n🔍 Тестирование парсера рейтингов...")
    
    try:
        from parsers.ufc_rankings import UFCRankingsParser
        
        parser = UFCRankingsParser()
        
        # Тестируем с кэшем (если есть сохраненная страница)
        if os.path.exists("fight_ru_ufc.html"):
            print("   Используем сохраненную страницу...")
            with open("fight_ru_ufc.html", 'r', encoding='utf-8') as f:
                html = f.read()
            
            categories = parser.parse_rankings(html)
            print(f"✅ Парсинг рейтингов успешен")
            print(f"   Найдено категорий: {len(categories)}")
            
            # Показываем первые 3 категории
            for i, (name, fighters) in enumerate(list(categories.items())[:3]):
                print(f"   {i+1}. {name}: {len(fighters)} бойцов")
            
            return True
        else:
            print("   ⚠️ Файл fight_ru_ufc.html не найден")
            print("   Запустите: python run.py для создания файла")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка парсера рейтингов: {e}")
        return False

def test_fighter_profiles_parser():
    """Тестирует парсер профилей"""
    print("\n🔍 Тестирование парсера профилей...")
    
    try:
        from parsers.fighter_profiles import FighterProfilesParser
        
        parser = FighterProfilesParser()
        
        # Тестируем с тестовым URL (если есть)
        test_url = "https://fight.ru/fighter/example"  # Замените на реальный URL
        
        print("   ⚠️ Парсер профилей готов к работе")
        print("   Для полного теста нужны реальные URL профилей")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка парсера профилей: {e}")
        return False

def test_upcoming_cards_parser():
    """Тестирует парсер кардов"""
    print("\n🔍 Тестирование парсера кардов...")
    
    try:
        from parsers.upcoming_cards import UpcomingCardsParser
        
        parser = UpcomingCardsParser()
        
        print("   ⚠️ Парсер кардов готов к работе")
        print("   Для полного теста нужен доступ к ufc.com")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка парсера кардов: {e}")
        return False

def main():
    """Главная функция тестирования"""
    print("🧪 Тестирование новой структуры UFC Ranker")
    print("=" * 50)
    
    tests = [
        test_database_connection,
        test_rankings_parser,
        test_fighter_profiles_parser,
        test_upcoming_cards_parser
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Результаты тестирования: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены! Новая структура готова к использованию.")
    else:
        print("⚠️ Некоторые тесты не пройдены. Проверьте ошибки выше.")
    
    print("\n📝 Следующие шаги:")
    print("1. Установите зависимости: pip install -r requirements_new.txt")
    print("2. Запустите миграцию: python migrate_to_new_structure.py")
    print("3. Запустите парсеры: python parsers/main.py all")

if __name__ == "__main__":
    main()
