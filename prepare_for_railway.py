#!/usr/bin/env python3
"""
Скрипт подготовки к деплою на Railway
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Выполняет команду и выводит результат"""
    print(f"Выполняется: {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"OK {description} - успешно")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR {description} - ошибка: {e}")
        print(f"Вывод: {e.stdout}")
        print(f"Ошибка: {e.stderr}")
        return False

def check_files():
    """Проверяет наличие необходимых файлов"""
    required_files = [
        "main.py",
        "requirements.txt", 
        "runtime.txt",
        "Procfile"
    ]
    
    print("Проверка необходимых файлов...")
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"OK {file} - найден")
        else:
            print(f"ERROR {file} - НЕ НАЙДЕН")
            missing_files.append(file)
    
    return len(missing_files) == 0

def build_frontend():
    """Собирает фронтенд"""
    if not os.path.exists("frontend"):
        print("ERROR Папка frontend не найдена")
        return False
    
    # Переходим в папку frontend
    os.chdir("frontend")
    
    # Устанавливаем зависимости
    if not run_command("npm install", "Установка npm зависимостей"):
        return False
    
    # Собираем проект
    if not run_command("npm run build", "Сборка фронтенда"):
        return False
    
    # Возвращаемся в корень
    os.chdir("..")
    
    # Проверяем что dist создан
    if os.path.exists("frontend/dist"):
        print("OK Фронтенд собран успешно")
        return True
    else:
        print("ERROR Папка frontend/dist не создана")
        return False

def prepare_git():
    """Подготавливает Git репозиторий"""
    print("Подготовка Git репозитория...")
    
    # Проверяем что мы в Git репозитории
    if not os.path.exists(".git"):
        print("ERROR Не в Git репозитории. Выполните: git init")
        return False
    
    # Добавляем все файлы
    if not run_command("git add .", "Добавление файлов в Git"):
        return False
    
    # Коммитим изменения
    if not run_command('git commit -m "Prepare for Railway deployment"', "Создание коммита"):
        return False
    
    print("OK Git репозиторий подготовлен")
    return True

def main():
    """Главная функция"""
    print("Подготовка UFC Ranker к деплою на Railway")
    print("=" * 50)
    
    # Проверяем файлы
    if not check_files():
        print("\nERROR Не все необходимые файлы найдены!")
        print("Убедитесь что созданы:")
        print("- main.py")
        print("- requirements.txt")
        print("- runtime.txt") 
        print("- Procfile")
        return False
    
    # Собираем фронтенд
    if not build_frontend():
        print("\nERROR Ошибка сборки фронтенда!")
        return False
    
    # Подготавливаем Git
    if not prepare_git():
        print("\nERROR Ошибка подготовки Git!")
        return False
    
    print("\nSUCCESS Подготовка завершена успешно!")
    print("\nСледующие шаги:")
    print("1. Создайте репозиторий на GitHub")
    print("2. Загрузите код: git push origin main")
    print("3. Подключите репозиторий к Railway")
    print("4. Добавьте PostgreSQL сервис")
    print("5. Настройте переменные окружения")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
