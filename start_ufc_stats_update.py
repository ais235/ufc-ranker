#!/usr/bin/env python3
"""
Скрипт для запуска обновления данных ufc.stats
"""

import subprocess
import sys
import os

def main():
    """Запускает обновление данных ufc.stats"""
    print("🥊 Запуск обновления данных ufc.stats...")
    print("=" * 50)
    
    try:
        # Запускаем скрипт обновления
        result = subprocess.run([
            sys.executable, 
            "refresh_ufc_stats.py"
        ], check=True, capture_output=True, text=True)
        
        print("✅ Обновление завершено успешно!")
        print("\nВывод:")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print("❌ Ошибка при обновлении данных:")
        print(f"Код возврата: {e.returncode}")
        print(f"Вывод: {e.stdout}")
        print(f"Ошибки: {e.stderr}")
        return 1
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
