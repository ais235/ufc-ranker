#!/usr/bin/env python3
"""
Скрипт для переключения на отладочную базу данных
"""

import os
import shutil
from datetime import datetime

def switch_to_debug_db():
    """Переключается на отладочную базу данных"""
    
    print("🔄 Переключение на отладочную базу данных...")
    print("="*50)
    
    # Создаем резервную копию текущей БД
    current_db = "ufc_ranker_v2.db"
    debug_db = "debug_ufc_ranker.db"
    backup_db = f"ufc_ranker_v2_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    try:
        # Проверяем существование отладочной БД
        if not os.path.exists(debug_db):
            print(f"❌ Отладочная база данных {debug_db} не найдена!")
            print("💡 Сначала запустите: python create_debug_database.py")
            return False
        
        # Создаем резервную копию текущей БД
        if os.path.exists(current_db):
            shutil.copy2(current_db, backup_db)
            print(f"✅ Резервная копия создана: {backup_db}")
        
        # Копируем отладочную БД как основную
        shutil.copy2(debug_db, current_db)
        print(f"✅ Переключено на отладочную БД: {debug_db} -> {current_db}")
        
        # Показываем статистику
        print("\n📊 Статистика отладочной базы данных:")
        print("-" * 30)
        
        # Подключаемся к БД для проверки
        import sqlite3
        conn = sqlite3.connect(current_db)
        cursor = conn.cursor()
        
        # Считаем записи в основных таблицах
        tables = [
            ("fighters", "Бойцы"),
            ("weight_classes", "Весовые категории"),
            ("rankings", "Рейтинги"),
            ("fight_records", "Боевые рекорды"),
            ("events", "События"),
            ("fights", "Исторические бои"),
            ("fight_stats", "Статистика боев"),
            ("upcoming_fights", "Предстоящие бои")
        ]
        
        for table, name in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {name}: {count}")
            except sqlite3.OperationalError:
                print(f"  {name}: таблица не найдена")
        
        conn.close()
        
        print("\n" + "="*50)
        print("✅ Успешно переключено на отладочную базу данных!")
        print("💡 Теперь вы можете тестировать страницу бойца с полными данными")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при переключении БД: {e}")
        return False

def main():
    """Главная функция"""
    success = switch_to_debug_db()
    if not success:
        print("\n💥 Не удалось переключиться на отладочную БД")
        return False
    
    return True

if __name__ == "__main__":
    main()





