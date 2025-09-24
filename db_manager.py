#!/usr/bin/env python3
"""
Менеджер баз данных для быстрого переключения между разными БД
"""

import os
import shutil
import sys
from datetime import datetime

def list_databases():
    """Показывает доступные базы данных"""
    print("🗄️ Доступные базы данных:")
    print("-" * 40)
    
    db_files = [
        ("ufc_ranker_v2.db", "Основная БД"),
        ("debug_ufc_ranker.db", "Отладочная БД"),
        ("test_ufc_ranker.db", "Тестовая БД"),
        ("ufc_stats.db", "UFC Stats БД")
    ]
    
    for db_file, description in db_files:
        if os.path.exists(db_file):
            size = os.path.getsize(db_file)
            size_mb = size / (1024 * 1024)
            print(f"  ✅ {db_file} - {description} ({size_mb:.1f} MB)")
        else:
            print(f"  ❌ {db_file} - {description} (не найдена)")
    
    print()

def switch_database(source_db, target_db="ufc_ranker_v2.db"):
    """Переключается на указанную базу данных"""
    
    if not os.path.exists(source_db):
        print(f"❌ База данных {source_db} не найдена!")
        return False
    
    try:
        # Создаем резервную копию текущей БД
        if os.path.exists(target_db):
            backup_name = f"{target_db.replace('.db', '')}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2(target_db, backup_name)
            print(f"✅ Резервная копия создана: {backup_name}")
        
        # Копируем новую БД
        shutil.copy2(source_db, target_db)
        print(f"✅ Переключено: {source_db} -> {target_db}")
        
        # Показываем статистику
        show_db_stats(target_db)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при переключении: {e}")
        return False

def show_db_stats(db_file):
    """Показывает статистику базы данных"""
    try:
        import sqlite3
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        print(f"\n📊 Статистика {db_file}:")
        print("-" * 30)
        
        tables = [
            ("fighters", "Бойцы"),
            ("weight_classes", "Весовые категории"),
            ("rankings", "Рейтинги"),
            ("events", "События"),
            ("fights", "Бои"),
            ("fight_stats", "Статистика боев"),
            ("upcoming_fights", "Предстоящие бои")
        ]
        
        for table, name in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {name}: {count}")
            except sqlite3.OperationalError:
                pass  # Таблица не существует
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка при получении статистики: {e}")

def main():
    """Главная функция"""
    if len(sys.argv) < 2:
        print("🗄️ Менеджер баз данных UFC Ranker")
        print("=" * 50)
        print("Использование:")
        print("  python db_manager.py list                    - Показать доступные БД")
        print("  python db_manager.py switch <source>         - Переключиться на БД")
        print("  python db_manager.py stats [db_file]         - Показать статистику")
        print()
        print("Примеры:")
        print("  python db_manager.py switch debug_ufc_ranker.db")
        print("  python db_manager.py switch test_ufc_ranker.db")
        print("  python db_manager.py stats")
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        list_databases()
    
    elif command == "switch":
        if len(sys.argv) < 3:
            print("❌ Укажите имя базы данных для переключения")
            print("Пример: python db_manager.py switch debug_ufc_ranker.db")
            return
        
        source_db = sys.argv[2]
        success = switch_database(source_db)
        if success:
            print("\n🎉 Переключение выполнено успешно!")
        else:
            print("\n💥 Не удалось переключиться на указанную БД")
    
    elif command == "stats":
        db_file = sys.argv[2] if len(sys.argv) > 2 else "ufc_ranker_v2.db"
        if os.path.exists(db_file):
            show_db_stats(db_file)
        else:
            print(f"❌ База данных {db_file} не найдена!")
    
    else:
        print(f"❌ Неизвестная команда: {command}")
        print("Используйте 'python db_manager.py' для справки")

if __name__ == "__main__":
    main()












