# 🚀 Инструкция по переносу UFC Ranker на хостинг reg.ru

## 📋 Обзор проекта

**Текущая архитектура:**
- **Backend:** FastAPI (Python) на порту 8000
- **Frontend:** React + Vite на порту 3000  
- **База данных:** SQLite (ufc_ranker_v2.db)
- **Парсеры:** Python скрипты для сбора данных

---

## 🎯 План деплоя

### Вариант 1: Простой деплой (рекомендуется для начала)
- Frontend: статические файлы на хостинге
- Backend: отдельный VPS или облачный сервер
- База данных: PostgreSQL на облаке

### Вариант 2: Полный деплой на VPS
- Все компоненты на одном сервере
- Docker контейнеры
- Nginx как reverse proxy

---

## 📁 Подготовка файлов для деплоя

### 1. Создание production версии фронтенда

```bash
# В папке frontend
cd frontend
npm run build
```

**Результат:** папка `frontend/dist/` с готовыми статическими файлами

### 2. Подготовка backend для продакшена

**Создать файл `requirements-prod.txt`:**
```
fastapi>=0.95.0
uvicorn[standard]>=0.20.0
pydantic>=1.10.0
sqlalchemy>=1.4.0
python-dotenv>=0.19.0
requests>=2.28.0
beautifulsoup4>=4.11.0
lxml>=4.9.0
pandas>=1.5.0
psycopg2-binary>=2.9.0  # Для PostgreSQL
```

**Создать файл `start_production.py`:**
```python
#!/usr/bin/env python3
import uvicorn
import os

if __name__ == "__main__":
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        workers=1,  # Для начала один воркер
        log_level="info"
    )
```

### 3. Настройка базы данных для продакшена

**Создать файл `database/production_config.py`:**
```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# PostgreSQL для продакшена
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@host:port/database")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 🌐 Деплой на reg.ru

### Этап 1: Настройка хостинга

1. **Войдите в панель управления reg.ru**
2. **Создайте новый сайт** с вашим доменом
3. **Выберите тип хостинга:**
   - **Shared hosting** - для статического фронтенда
   - **VPS** - для полного деплоя

### Этап 2: Загрузка фронтенда (Shared Hosting)

**Если используете shared hosting:**

1. **Соберите фронтенд:**
   ```bash
   cd frontend
   npm run build
   ```

2. **Загрузите содержимое папки `frontend/dist/` в корень сайта через FTP/SFTP**

3. **Настройте API URL в фронтенде:**
   
   **Создать файл `frontend/src/config/production.ts`:**
   ```typescript
   export const API_BASE_URL = 'https://your-backend-domain.com/api';
   ```

   **Обновить `frontend/src/services/api.ts`:**
   ```typescript
   import { API_BASE_URL } from '../config/production';
   
   const API_URL = API_BASE_URL || 'http://localhost:8000/api';
   ```

### Этап 3: Настройка backend (VPS или облачный сервер)

**Рекомендуемые варианты:**
- **reg.ru VPS** - удобно, все в одном месте
- **DigitalOcean/AWS** - больше возможностей
- **Heroku/Railway** - простой деплой

#### Вариант A: reg.ru VPS

1. **Закажите VPS** с Ubuntu 20.04/22.04
2. **Подключитесь по SSH:**
   ```bash
   ssh root@your-vps-ip
   ```

3. **Установите зависимости:**
   ```bash
   # Обновление системы
   apt update && apt upgrade -y
   
   # Python 3.11
   apt install python3.11 python3.11-pip python3.11-venv -y
   
   # PostgreSQL
   apt install postgresql postgresql-contrib -y
   
   # Nginx
   apt install nginx -y
   
   # Git
   apt install git -y
   ```

4. **Создайте пользователя для приложения:**
   ```bash
   adduser ufcranker
   usermod -aG sudo ufcranker
   su - ufcranker
   ```

5. **Клонируйте проект:**
   ```bash
   git clone https://github.com/your-username/ufc-ranker.git
   cd ufc-ranker
   ```

6. **Настройте виртуальное окружение:**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements-prod.txt
   ```

#### Вариант B: Heroku (проще всего)

1. **Создайте аккаунт на Heroku**
2. **Установите Heroku CLI**
3. **Создайте файл `Procfile`:**
   ```
   web: python start_production.py
   ```

4. **Создайте файл `runtime.txt`:**
   ```
   python-3.11.0
   ```

5. **Деплой:**
   ```bash
   heroku create your-app-name
   heroku addons:create heroku-postgresql:hobby-dev
   git push heroku main
   ```

### Этап 4: Настройка базы данных

#### Для VPS (PostgreSQL):

1. **Создайте базу данных:**
   ```bash
   sudo -u postgres psql
   CREATE DATABASE ufc_ranker;
   CREATE USER ufcranker WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE ufc_ranker TO ufcranker;
   \q
   ```

2. **Мигрируйте данные из SQLite:**
   
   **Создать скрипт `migrate_to_postgres.py`:**
   ```python
   import sqlite3
   import psycopg2
   from sqlalchemy import create_engine
   import pandas as pd
   
   # Подключение к SQLite
   sqlite_conn = sqlite3.connect('ufc_ranker_v2.db')
   
   # Подключение к PostgreSQL
   pg_engine = create_engine('postgresql://ufcranker:password@localhost/ufc_ranker')
   
   # Миграция таблиц
   tables = ['fighters', 'weight_classes', 'rankings', 'events', 'fights']
   
   for table in tables:
       df = pd.read_sql_query(f"SELECT * FROM {table}", sqlite_conn)
       df.to_sql(table, pg_engine, if_exists='replace', index=False)
       print(f"Migrated {table}: {len(df)} rows")
   
   sqlite_conn.close()
   ```

#### Для Heroku:
```bash
heroku run python migrate_to_postgres.py
```

### Этап 5: Настройка переменных окружения

**Создать файл `.env` на сервере:**
```env
# База данных
DATABASE_URL=postgresql://ufcranker:password@localhost/ufc_ranker

# Окружение
ENVIRONMENT=production

# API настройки
API_HOST=0.0.0.0
API_PORT=8000

# CORS
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

### Этап 6: Настройка Nginx (для VPS)

**Создать файл `/etc/nginx/sites-available/ufc-ranker`:**
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Frontend (статические файлы)
    location / {
        root /home/ufcranker/ufc-ranker/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Активировать конфигурацию:**
```bash
sudo ln -s /etc/nginx/sites-available/ufc-ranker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Этап 7: Настройка SSL (HTTPS)

**Для reg.ru:**
1. В панели управления включите SSL сертификат
2. Настройте редирект с HTTP на HTTPS

**Для VPS (Let's Encrypt):**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

---

## 🔧 Настройка системы

### Создание systemd сервиса (для VPS)

**Файл `/etc/systemd/system/ufc-ranker.service`:**
```ini
[Unit]
Description=UFC Ranker Backend
After=network.target

[Service]
Type=simple
User=ufcranker
WorkingDirectory=/home/ufcranker/ufc-ranker
Environment=PATH=/home/ufcranker/ufc-ranker/venv/bin
ExecStart=/home/ufcranker/ufc-ranker/venv/bin/python start_production.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Запуск сервиса:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable ufc-ranker
sudo systemctl start ufc-ranker
sudo systemctl status ufc-ranker
```

---

## 📊 Мониторинг и логи

### Просмотр логов:
```bash
# Логи приложения
sudo journalctl -u ufc-ranker -f

# Логи Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Проверка статуса:
```bash
# Статус сервисов
sudo systemctl status ufc-ranker
sudo systemctl status nginx
sudo systemctl status postgresql

# Проверка портов
sudo netstat -tlnp | grep :8000
sudo netstat -tlnp | grep :80
```

---

## 🚀 Автоматизация деплоя

### Создать скрипт деплоя `deploy.sh`:
```bash
#!/bin/bash
echo "🚀 Deploying UFC Ranker..."

# Остановка сервиса
sudo systemctl stop ufc-ranker

# Обновление кода
git pull origin main

# Активация виртуального окружения
source venv/bin/activate

# Установка зависимостей
pip install -r requirements-prod.txt

# Сборка фронтенда
cd frontend
npm run build
cd ..

# Миграции БД (если нужно)
python migrate_database.py

# Перезапуск сервиса
sudo systemctl start ufc-ranker

echo "✅ Deployment completed!"
```

---

## 📝 Чек-лист деплоя

### Перед деплоем:
- [ ] Собрать фронтенд (`npm run build`)
- [ ] Подготовить production зависимости
- [ ] Настроить переменные окружения
- [ ] Подготовить скрипт миграции БД

### После деплоя:
- [ ] Проверить доступность сайта
- [ ] Проверить API эндпоинты
- [ ] Проверить загрузку данных
- [ ] Настроить SSL сертификат
- [ ] Настроить мониторинг

### Тестирование:
- [ ] Главная страница загружается
- [ ] Карточки бойцов отображаются
- [ ] Рейтинги работают
- [ ] События загружаются
- [ ] Поиск функционирует

---

## 💰 Примерные расходы

**reg.ru Shared Hosting:** ~300-500 руб/месяц
- Только для статического фронтенда
- Backend нужен отдельно

**reg.ru VPS:** ~1000-2000 руб/месяц
- Полный контроль
- Все компоненты на одном сервере

**Heroku:** ~$7-25/месяц
- Простой деплой
- Автоматическое масштабирование

---

## 🆘 Решение проблем

### Частые проблемы:

1. **CORS ошибки:**
   - Проверить настройки CORS в backend
   - Убедиться что домены указаны правильно

2. **База данных не подключается:**
   - Проверить строку подключения
   - Убедиться что PostgreSQL запущен

3. **Статические файлы не загружаются:**
   - Проверить настройки Nginx
   - Убедиться что файлы загружены в правильную папку

4. **SSL сертификат не работает:**
   - Проверить DNS записи
   - Убедиться что домен указывает на сервер

---

## 📞 Поддержка

Если возникнут проблемы:
1. Проверьте логи сервисов
2. Убедитесь что все порты открыты
3. Проверьте настройки файрвола
4. Обратитесь в поддержку reg.ru

**Удачи с деплоем! 🚀**
