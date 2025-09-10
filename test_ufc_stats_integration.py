#!/usr/bin/env python3
"""
Тестовый скрипт для проверки интеграции ufc.stats
"""

import sys
import os
from datetime import datetime

# Добавляем корневую папку в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.config import init_database, SessionLocal
from parsers.ufc_stats_importer import UFCStatsImporter
from database.models import Fighter, Fight, FightStats, Event, WeightClass


def test_database_models():
    """Тестирует создание таблиц БД"""
    print("🔧 Тестирование моделей базы данных...")
    
    try:
        init_database()
        print("✅ База данных инициализирована")
        
        # Проверяем создание таблиц
        db = SessionLocal()
        
        # Проверяем количество записей
        fighters_count = db.query(Fighter).count()
        events_count = db.query(Event).count()
        fights_count = db.query(Fight).count()
        stats_count = db.query(FightStats).count()
        weight_classes_count = db.query(WeightClass).count()
        
        print(f"📊 Статистика БД:")
        print(f"   Бойцов: {fighters_count}")
        print(f"   Событий: {events_count}")
        print(f"   Боев: {fights_count}")
        print(f"   Записей статистики: {stats_count}")
        print(f"   Весовых категорий: {weight_classes_count}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании БД: {e}")
        return False


def test_ufc_stats_importer():
    """Тестирует импортер ufc.stats"""
    print("\n📥 Тестирование импортера ufc.stats...")
    
    try:
        importer = UFCStatsImporter()
        
        # Тестируем создание тестовых данных
        df = importer._create_sample_data()
        print(f"✅ Создано {len(df)} тестовых записей")
        
        # Тестируем импорт в БД
        importer.import_to_database(df)
        print("✅ Данные импортированы в БД")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании импортера: {e}")
        return False


def test_api_endpoints():
    """Тестирует API эндпоинты"""
    print("\n🌐 Тестирование API эндпоинтов...")
    
    try:
        import requests
        import time
        
        # Ждем запуска сервера
        print("⏳ Ожидание запуска сервера...")
        time.sleep(2)
        
        base_url = "http://localhost:8000"
        
        # Тестируем основные эндпоинты
        endpoints = [
            "/",
            "/api/stats",
            "/api/fighters?limit=5",
            "/api/weight-classes",
            "/api/events?limit=5",
            "/api/fights?limit=5"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {endpoint} - OK")
                else:
                    print(f"⚠️  {endpoint} - {response.status_code}")
            except requests.exceptions.RequestException:
                print(f"❌ {endpoint} - Недоступен")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании API: {e}")
        return False


def test_fighter_stats():
    """Тестирует статистику бойцов"""
    print("\n🥊 Тестирование статистики бойцов...")
    
    try:
        db = SessionLocal()
        
        # Получаем первого бойца со статистикой
        fighter = db.query(Fighter).join(FightStats).first()
        
        if fighter:
            print(f"✅ Найден боец: {fighter.name_ru}")
            
            # Получаем статистику
            stats = db.query(FightStats).filter(FightStats.fighter_id == fighter.id).all()
            print(f"   Записей статистики: {len(stats)}")
            
            if stats:
                total_strikes = sum(s.significant_strikes_landed for s in stats)
                avg_accuracy = sum(s.significant_strikes_rate for s in stats) / len(stats)
                print(f"   Всего ударов: {total_strikes}")
                print(f"   Средняя точность: {avg_accuracy:.1f}%")
        else:
            print("⚠️  Бойцы со статистикой не найдены")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании статистики: {e}")
        return False


def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование интеграции ufc.stats")
    print("=" * 50)
    print(f"Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Модели БД", test_database_models),
        ("Импортер ufc.stats", test_ufc_stats_importer),
        ("Статистика бойцов", test_fighter_stats),
        ("API эндпоинты", test_api_endpoints),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} - ПРОЙДЕН")
        else:
            print(f"❌ {test_name} - ПРОВАЛЕН")
    
    print(f"\n{'='*50}")
    print(f"Результаты: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены успешно!")
        return 0
    else:
        print("⚠️  Некоторые тесты провалены")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
