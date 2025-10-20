#!/bin/bash

echo "🚀 Deploying UFC Ranker to production..."

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверяем что мы в правильной директории
if [ ! -f "start_production.py" ]; then
    error "Скрипт должен запускаться из корневой папки проекта!"
    exit 1
fi

log "Остановка сервиса..."
sudo systemctl stop ufc-ranker 2>/dev/null || warn "Сервис не был запущен"

log "Обновление кода из Git..."
git pull origin main || error "Ошибка при обновлении кода"

log "Активация виртуального окружения..."
source venv/bin/activate || error "Ошибка активации виртуального окружения"

log "Установка зависимостей..."
pip install -r requirements-prod.txt || error "Ошибка установки зависимостей"

log "Сборка фронтенда..."
cd frontend
npm install || error "Ошибка установки npm зависимостей"
npm run build || error "Ошибка сборки фронтенда"
cd ..

log "Проверка базы данных..."
python -c "
from database.config import SessionLocal
try:
    db = SessionLocal()
    db.execute('SELECT 1')
    db.close()
    print('✅ База данных доступна')
except Exception as e:
    print(f'❌ Ошибка базы данных: {e}')
    exit(1)
"

log "Перезапуск сервиса..."
sudo systemctl start ufc-ranker || error "Ошибка запуска сервиса"

log "Проверка статуса сервиса..."
sleep 3
if sudo systemctl is-active --quiet ufc-ranker; then
    log "✅ Сервис запущен успешно"
else
    error "❌ Сервис не запустился"
    sudo systemctl status ufc-ranker
    exit 1
fi

log "Проверка доступности API..."
sleep 5
if curl -f http://localhost:8000/api/stats > /dev/null 2>&1; then
    log "✅ API доступно"
else
    warn "⚠️ API недоступно, проверьте логи"
fi

log "Перезагрузка Nginx..."
sudo systemctl reload nginx || warn "Ошибка перезагрузки Nginx"

echo ""
log "🎉 Деплой завершен успешно!"
log "🌐 Сайт доступен по адресу: https://your-domain.com"
log "📊 API доступно по адресу: https://your-domain.com/api"
echo ""

# Показываем статус сервисов
log "Статус сервисов:"
sudo systemctl status ufc-ranker --no-pager -l
