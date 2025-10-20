#!/bin/bash
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
