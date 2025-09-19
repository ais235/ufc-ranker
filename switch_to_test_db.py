#!/usr/bin/env python3
"""
Скрипт для переключения на тестовую базу данных
"""

import os
import shutil
from pathlib import Path

def switch_to_test_database():
    """Переключается на тестовую базу данных"""
    
    # Пути к базам данных
    current_db = "ufc_stats.db"
    test_db = "test_ufc_ranker.db"
    
    # Проверяем, существует ли тестовая база
    if not os.path.exists(test_db):
        print(f"❌ Тестовая база данных {test_db} не найдена!")
        print("Запустите сначала: python create_test_database.py")
        return False
    
    # Создаем резервную копию текущей базы
    if os.path.exists(current_db):
        backup_name = f"{current_db}.backup"
        shutil.copy2(current_db, backup_name)
        print(f"💾 Создана резервная копия: {backup_name}")
    
    # Копируем тестовую базу как основную
    shutil.copy2(test_db, current_db)
    print(f"✅ Переключено на тестовую базу данных: {current_db}")
    
    return True

def switch_back_to_original():
    """Возвращается к оригинальной базе данных"""
    
    current_db = "ufc_stats.db"
    backup_db = f"{current_db}.backup"
    
    if not os.path.exists(backup_db):
        print(f"❌ Резервная копия {backup_db} не найдена!")
        return False
    
    # Восстанавливаем оригинальную базу
    shutil.copy2(backup_db, current_db)
    print(f"✅ Восстановлена оригинальная база данных: {current_db}")
    
    return True

def main():
    """Главная функция"""
    print("🔄 Переключение базы данных")
    print("="*40)
    print("1. Переключиться на тестовую базу")
    print("2. Вернуться к оригинальной базе")
    print("3. Выход")
    print("="*40)
    
    choice = input("Выберите опцию (1-3): ").strip()
    
    if choice == "1":
        if switch_to_test_database():
            print("\n🎉 Теперь используется тестовая база данных!")
            print("Запустите бэкенд для проверки: python start_backend.py")
    elif choice == "2":
        if switch_back_to_original():
            print("\n🎉 Восстановлена оригинальная база данных!")
    elif choice == "3":
        print("👋 До свидания!")
    else:
        print("❌ Неверный выбор!")

if __name__ == "__main__":
    main()

