#!/usr/bin/env python3
"""
Скрипт для миграции в новую структуру проекта
"""

import os
import shutil
from pathlib import Path

def migrate_files():
    """Переносит старые файлы в папку legacy"""
    print("🔄 Миграция в новую структуру проекта...")
    
    # Создаем папку legacy если её нет
    legacy_dir = Path("legacy")
    legacy_dir.mkdir(exist_ok=True)
    
    # Файлы для переноса в legacy
    files_to_move = [
        "extract_all_categories.py",
        "build_category_pages.py", 
        "update_design.py",
        "run.py"
    ]
    
    # Переносим файлы
    for file_name in files_to_move:
        if os.path.exists(file_name):
            shutil.move(file_name, legacy_dir / file_name)
            print(f"✅ Перенесен: {file_name}")
    
    # Переносим папки с результатами
    folders_to_move = ["rankings", "category_pages", ".cache"]
    
    for folder_name in folders_to_move:
        if os.path.exists(folder_name):
            shutil.move(folder_name, legacy_dir / folder_name)
            print(f"✅ Перенесена папка: {folder_name}")
    
    print("\n🎉 Миграция завершена!")
    print("📁 Старые файлы находятся в папке legacy/")
    print("🚀 Новая структура готова к использованию!")

if __name__ == "__main__":
    migrate_files()
