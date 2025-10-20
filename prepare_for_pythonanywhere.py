#!/usr/bin/env python3
"""
Скрипт подготовки UFC Ranker для деплоя на PythonAnywhere
"""
import os
import shutil
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
        "pythonanywhere_wsgi.py",
        "pythonanywhere_config.py", 
        "main.py",
        "requirements.txt",
        "backend/app.py",
        "database/models.py"
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
        os.chdir("..")
        return False
    
    # Собираем фронтенд
    if not run_command("npm run build", "Сборка фронтенда"):
        os.chdir("..")
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

def create_pythonanywhere_files():
    """Создает файлы специфичные для PythonAnywhere"""
    print("Создание файлов для PythonAnywhere...")
    
    # Создаем .pythonanywhere файл
    pythonanywhere_content = """# PythonAnywhere конфигурация
# Этот файл содержит настройки для PythonAnywhere

# Путь к проекту (замените yourusername на ваш username)
PROJECT_PATH = '/home/yourusername/ufc-ranker'

# URL вашего сайта
SITE_URL = 'https://yourusername.pythonanywhere.com'

# Настройки базы данных
DATABASE_URL = 'sqlite:///./ufc_ranker_v2.db'

# Настройки статических файлов
STATIC_URL = '/static/'
STATIC_ROOT = '/home/yourusername/ufc-ranker/frontend/dist/'

# Настройки медиа файлов
MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/yourusername/ufc-ranker/media/'
"""
    
    with open(".pythonanywhere", "w", encoding="utf-8") as f:
        f.write(pythonanywhere_content)
    
    print("OK Файл .pythonanywhere создан")
    return True

def create_deployment_script():
    """Создает скрипт для деплоя"""
    deploy_script = """#!/bin/bash
# Скрипт деплоя на PythonAnywhere

echo "🚀 Деплой UFC Ranker на PythonAnywhere"
echo "======================================"

# Проверяем что мы в правильной папке
if [ ! -f "pythonanywhere_wsgi.py" ]; then
    echo "❌ Ошибка: файл pythonanywhere_wsgi.py не найден"
    echo "Убедитесь что вы находитесь в корне проекта"
    exit 1
fi

# Устанавливаем зависимости
echo "📦 Установка зависимостей..."
pip3.10 install --user -r requirements.txt

# Инициализируем базу данных
echo "🗄️ Инициализация базы данных..."
python3.10 -c "from database.config import init_database; init_database()"

# Собираем фронтенд
echo "🎨 Сборка фронтенда..."
cd frontend
npm install
npm run build
cd ..

echo "✅ Деплой завершен!"
echo "🌐 Ваш сайт будет доступен по адресу: https://yourusername.pythonanywhere.com"
echo "📚 Не забудьте настроить WSGI конфигурацию в панели PythonAnywhere"
"""
    
    with open("deploy_pythonanywhere.sh", "w", encoding="utf-8") as f:
        f.write(deploy_script)
    
    # Делаем файл исполняемым
    os.chmod("deploy_pythonanywhere.sh", 0o755)
    
    print("OK Скрипт deploy_pythonanywhere.sh создан")
    return True

def main():
    """Главная функция"""
    print("Подготовка UFC Ranker к деплою на PythonAnywhere")
    print("=" * 60)
    
    # Проверяем файлы
    if not check_files():
        print("\nERROR Не все необходимые файлы найдены!")
        print("Убедитесь что созданы:")
        print("- pythonanywhere_wsgi.py")
        print("- pythonanywhere_config.py")
        print("- main.py")
        print("- requirements.txt")
        return False
    
    # Собираем фронтенд
    if not build_frontend():
        print("\nERROR Ошибка сборки фронтенда!")
        return False
    
    # Создаем файлы для PythonAnywhere
    if not create_pythonanywhere_files():
        print("\nERROR Ошибка создания файлов PythonAnywhere!")
        return False
    
    # Создаем скрипт деплоя
    if not create_deployment_script():
        print("\nERROR Ошибка создания скрипта деплоя!")
        return False
    
    print("\nSUCCESS Подготовка завершена успешно!")
    print("\nСледующие шаги:")
    print("1. Загрузите файлы на PythonAnywhere")
    print("2. Выполните: bash deploy_pythonanywhere.sh")
    print("3. Настройте WSGI конфигурацию")
    print("4. Настройте статические файлы")
    print("5. Перезапустите приложение")
    print("\nПодробная инструкция в файле: PYTHONANYWHERE_DEPLOYMENT_GUIDE.md")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
