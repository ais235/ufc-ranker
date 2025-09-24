#!/usr/bin/env python3
"""
Скрипт для автоматического резервного копирования базы данных UFC Ranker
"""

import os
import shutil
import sqlite3
from datetime import datetime
import sys

def create_backup():
    """Создает резервную копию базы данных"""
    
    # Путь к основной базе данных
    main_db_path = "ufc_ranker_v2.db"
    backup_dir = "database_backups"
    
    # Проверяем существование основной БД
    if not os.path.exists(main_db_path):
        print(f"❌ Основная база данных {main_db_path} не найдена!")
        return False
    
    # Создаем папку для бэкапов если её нет
    os.makedirs(backup_dir, exist_ok=True)
    
    # Генерируем имя файла с временной меткой
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"ufc_ranker_v2_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        # Копируем базу данных
        shutil.copy2(main_db_path, backup_path)
        
        # Проверяем целостность скопированной БД
        conn = sqlite3.connect(backup_path)
        cursor = conn.cursor()
        
        # Проверяем основные таблицы
        tables_to_check = ['fighters', 'fights', 'events', 'rankings']
        for table in tables_to_check:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"✅ Таблица {table}: {count} записей")
        
        conn.close()
        
        # Получаем размер файла
        file_size = os.path.getsize(backup_path)
        size_mb = file_size / (1024 * 1024)
        
        print(f"✅ Резервная копия создана: {backup_path}")
        print(f"📊 Размер файла: {size_mb:.2f} MB")
        
        # Удаляем старые бэкапы (оставляем только последние 5)
        cleanup_old_backups(backup_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при создании резервной копии: {e}")
        return False

def cleanup_old_backups(backup_dir):
    """Удаляет старые резервные копии, оставляя только последние 5"""
    try:
        backup_files = []
        for filename in os.listdir(backup_dir):
            if filename.startswith("ufc_ranker_v2_backup_") and filename.endswith(".db"):
                file_path = os.path.join(backup_dir, filename)
                backup_files.append((file_path, os.path.getmtime(file_path)))
        
        # Сортируем по времени модификации (новые первыми)
        backup_files.sort(key=lambda x: x[1], reverse=True)
        
        # Удаляем старые бэкапы (оставляем только последние 5)
        for file_path, _ in backup_files[5:]:
            os.remove(file_path)
            print(f"🗑️ Удален старый бэкап: {os.path.basename(file_path)}")
            
    except Exception as e:
        print(f"⚠️ Ошибка при очистке старых бэкапов: {e}")

def restore_from_backup(backup_filename):
    """Восстанавливает базу данных из резервной копии"""
    backup_path = os.path.join("database_backups", backup_filename)
    main_db_path = "ufc_ranker_v2.db"
    
    if not os.path.exists(backup_path):
        print(f"❌ Резервная копия {backup_filename} не найдена!")
        return False
    
    try:
        # Создаем бэкап текущей БД перед восстановлением
        if os.path.exists(main_db_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            current_backup = f"ufc_ranker_v2_current_backup_{timestamp}.db"
            shutil.copy2(main_db_path, os.path.join("database_backups", current_backup))
            print(f"📋 Создан бэкап текущей БД: {current_backup}")
        
        # Восстанавливаем из резервной копии
        shutil.copy2(backup_path, main_db_path)
        print(f"✅ База данных восстановлена из {backup_filename}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при восстановлении: {e}")
        return False

def list_backups():
    """Показывает список доступных резервных копий"""
    backup_dir = "database_backups"
    if not os.path.exists(backup_dir):
        print("❌ Папка с резервными копиями не найдена!")
        return
    
    backup_files = []
    for filename in os.listdir(backup_dir):
        if filename.startswith("ufc_ranker_v2_backup_") and filename.endswith(".db"):
            file_path = os.path.join(backup_dir, filename)
            file_size = os.path.getsize(file_path)
            mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            backup_files.append((filename, file_size, mod_time))
    
    if not backup_files:
        print("📭 Резервные копии не найдены")
        return
    
    print("📋 Доступные резервные копии:")
    backup_files.sort(key=lambda x: x[2], reverse=True)  # Сортируем по дате
    
    for filename, size, mod_time in backup_files:
        size_mb = size / (1024 * 1024)
        print(f"  📄 {filename} ({size_mb:.2f} MB) - {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "backup":
            create_backup()
        elif command == "list":
            list_backups()
        elif command == "restore" and len(sys.argv) > 2:
            restore_from_backup(sys.argv[2])
        else:
            print("Использование:")
            print("  python backup_database.py backup     - создать резервную копию")
            print("  python backup_database.py list       - показать список копий")
            print("  python backup_database.py restore <filename> - восстановить из копии")
    else:
        # По умолчанию создаем резервную копию
        create_backup()
