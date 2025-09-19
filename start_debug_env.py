#!/usr/bin/env python3
"""
Скрипт для быстрого запуска отладочной среды с полной БД
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_requirements():
    """Проверяет наличие необходимых файлов"""
    required_files = [
        "debug_ufc_ranker.db",
        "database/models.py",
        "database/config.py",
        "backend/app.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Отсутствуют необходимые файлы:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    return True

def switch_to_debug_db():
    """Переключается на отладочную БД"""
    print("🔄 Переключение на отладочную базу данных...")
    
    try:
        import shutil
        from datetime import datetime
        
        # Создаем резервную копию
        if os.path.exists("ufc_ranker_v2.db"):
            backup_name = f"ufc_ranker_v2_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2("ufc_ranker_v2.db", backup_name)
            print(f"✅ Резервная копия: {backup_name}")
        
        # Переключаемся на отладочную БД
        shutil.copy2("debug_ufc_ranker.db", "ufc_ranker_v2.db")
        print("✅ Переключено на отладочную БД")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка переключения БД: {e}")
        return False

def start_backend():
    """Запускает бэкенд"""
    print("🚀 Запуск бэкенда...")
    
    try:
        # Проверяем, что мы в правильной директории
        if not os.path.exists("backend/app.py"):
            print("❌ Файл backend/app.py не найден!")
            return None
        
        # Запускаем бэкенд в фоновом режиме
        process = subprocess.Popen(
            [sys.executable, "start_backend.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Ждем немного, чтобы бэкенд запустился
        time.sleep(2)
        
        if process.poll() is None:
            print("✅ Бэкенд запущен (PID: {})".format(process.pid))
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Ошибка запуска бэкенда:")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка запуска бэкенда: {e}")
        return None

def start_frontend():
    """Запускает фронтенд"""
    print("🎨 Запуск фронтенда...")
    
    try:
        frontend_dir = Path("frontend")
        if not frontend_dir.exists():
            print("❌ Папка frontend не найдена!")
            return None
        
        # Переходим в папку фронтенда
        os.chdir(frontend_dir)
        
        # Проверяем наличие package.json
        if not os.path.exists("package.json"):
            print("❌ package.json не найден в папке frontend!")
            return None
        
        # Запускаем фронтенд
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Ждем немного
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ Фронтенд запущен (PID: {})".format(process.pid))
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Ошибка запуска фронтенда:")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка запуска фронтенда: {e}")
        return None

def show_info():
    """Показывает информацию о запущенной среде"""
    print("\n" + "="*60)
    print("🎉 ОТЛАДОЧНАЯ СРЕДА ЗАПУЩЕНА!")
    print("="*60)
    print("📊 База данных: debug_ufc_ranker.db")
    print("   - 17 бойцов")
    print("   - 7 весовых категорий")
    print("   - 5 событий UFC")
    print("   - 4 исторических боя")
    print("   - 4 предстоящих боя")
    print("   - Детальная статистика боев")
    print()
    print("🌐 Доступные URL:")
    print("   - Фронтенд: http://localhost:5173")
    print("   - Бэкенд API: http://localhost:8000")
    print("   - API документация: http://localhost:8000/docs")
    print()
    print("💡 Для остановки нажмите Ctrl+C")
    print("="*60)

def main():
    """Главная функция"""
    print("🚀 Запуск отладочной среды UFC Ranker")
    print("="*50)
    
    # Проверяем требования
    if not check_requirements():
        print("\n💥 Не удалось запустить отладочную среду")
        return False
    
    # Переключаемся на отладочную БД
    if not switch_to_debug_db():
        print("\n💥 Не удалось переключиться на отладочную БД")
        return False
    
    # Запускаем бэкенд
    backend_process = start_backend()
    if not backend_process:
        print("\n💥 Не удалось запустить бэкенд")
        return False
    
    # Запускаем фронтенд
    frontend_process = start_frontend()
    if not frontend_process:
        print("\n💥 Не удалось запустить фронтенд")
        if backend_process:
            backend_process.terminate()
        return False
    
    # Показываем информацию
    show_info()
    
    try:
        # Ждем завершения процессов
        while True:
            time.sleep(1)
            
            # Проверяем, что процессы еще работают
            if backend_process.poll() is not None:
                print("\n❌ Бэкенд остановлен неожиданно")
                break
            
            if frontend_process.poll() is not None:
                print("\n❌ Фронтенд остановлен неожиданно")
                break
                
    except KeyboardInterrupt:
        print("\n\n🛑 Остановка отладочной среды...")
        
        # Останавливаем процессы
        if backend_process and backend_process.poll() is None:
            backend_process.terminate()
            print("✅ Бэкенд остановлен")
        
        if frontend_process and frontend_process.poll() is None:
            frontend_process.terminate()
            print("✅ Фронтенд остановлен")
        
        print("🎉 Отладочная среда остановлена")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        sys.exit(1)





