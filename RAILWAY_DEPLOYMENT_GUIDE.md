# 🚀 Деплой UFC Ranker на Railway

## 📋 Подготовка проекта для Railway

Railway требует определенную структуру файлов. Давайте создадим все необходимые файлы:

### 1. Создание main.py (точка входа)

Railway ищет файл `main.py` в корне проекта. Создадим его:

```python
#!/usr/bin/env python3
"""
Точка входа для Railway
"""

import uvicorn
import os
import sys

# Добавляем корневую папку в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Получаем порт из переменной окружения Railway
    port = int(os.environ.get("PORT", 8000))
    
    print(f"🚀 Запуск UFC Ranker на Railway...")
    print(f"🌐 API будет доступно на порту: {port}")
    print("-" * 50)
    
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
```

### 2. Обновление requirements.txt

Railway использует `requirements.txt` из корня проекта:

```txt
# API (FastAPI)
fastapi>=0.95.0
uvicorn[standard]>=0.20.0
pydantic>=1.10.0

# База данных
sqlalchemy>=1.4.0
psycopg2-binary>=2.9.0  # PostgreSQL драйвер
alembic>=1.8.0

# Парсинг данных
requests>=2.28.0
beautifulsoup4>=4.11.0
lxml>=4.9.0
pandas>=1.5.0

# Утилиты
python-dotenv>=0.19.0
```

### 3. Создание runtime.txt

```txt
python-3.11.0
```

### 4. Создание Procfile

```txt
web: python main.py
```

### 5. Настройка переменных окружения

Railway автоматически предоставляет PostgreSQL. Нужно настроить переменные:

```env
DATABASE_URL=postgresql://postgres:password@host:port/database
ENVIRONMENT=production
```

---

## 🚀 Пошаговая инструкция деплоя

### Шаг 1: Подготовка файлов

1. **Создайте файлы в корне проекта:**
   - `main.py`
   - `requirements.txt` (обновленный)
   - `runtime.txt`
   - `Procfile`

2. **Соберите фронтенд:**
   ```bash
   cd frontend
   npm run build
   cd ..
   ```

### Шаг 2: Настройка GitHub

1. **Создайте репозиторий на GitHub:**
   - Перейдите на github.com
   - Нажмите "New repository"
   - Название: `ufc-ranker`
   - Сделайте публичным или приватным

2. **Загрузите код:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit for Railway deployment"
   git branch -M main
   git remote add origin https://github.com/your-username/ufc-ranker.git
   git push -u origin main
   ```

### Шаг 3: Деплой на Railway

1. **Зарегистрируйтесь на Railway:**
   - Перейдите на [railway.com](https://railway.com/)
   - Нажмите "Deploy a new project"
   - Войдите через GitHub

2. **Подключите репозиторий:**
   - Выберите "Deploy from GitHub Repo"
   - Найдите ваш репозиторий `ufc-ranker`
   - Нажмите "Deploy"

3. **Добавьте PostgreSQL:**
   - В панели Railway нажмите "+ New"
   - Выберите "Database" → "PostgreSQL"
   - Railway автоматически создаст БД

4. **Настройте переменные окружения:**
   - В настройках проекта найдите "Variables"
   - Добавьте переменные:
     ```
     DATABASE_URL=<автоматически из PostgreSQL>
     ENVIRONMENT=production
     ```

### Шаг 4: Миграция данных

1. **Подключитесь к Railway CLI:**
   ```bash
   npm install -g @railway/cli
   railway login
   railway link
   ```

2. **Мигрируйте данные:**
   ```bash
   railway run python migrate_to_postgres.py
   ```

### Шаг 5: Настройка домена

1. **В панели Railway:**
   - Перейдите в настройки проекта
   - Найдите "Domains"
   - Добавьте ваш домен
   - Настройте DNS записи

---

## 🔧 Дополнительные настройки

### Настройка CORS для фронтенда

Обновите `backend/app.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-domain.com",
        "https://www.your-domain.com",
        "https://your-app-name.railway.app"  # Railway домен
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Настройка статических файлов

Добавьте в `backend/app.py`:

```python
from fastapi.staticfiles import StaticFiles

# Обслуживание статических файлов фронтенда
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")
```

---

## 📊 Мониторинг и логи

Railway предоставляет встроенный мониторинг:

1. **Логи:** В панели Railway → "Deployments" → выберите деплой → "Logs"
2. **Метрики:** CPU, память, сеть в реальном времени
3. **Алерты:** Настройте уведомления о проблемах

---

## 💰 Стоимость Railway

- **Hobby Plan:** $5/месяц (достаточно для начала)
- **Pro Plan:** $20/месяц (для продакшена)
- **PostgreSQL:** включен в план

---

## 🆘 Решение проблем

### Проблема: Приложение не запускается
```bash
# Проверьте логи в Railway панели
# Убедитесь что main.py существует в корне
# Проверьте requirements.txt
```

### Проблема: База данных не подключается
```bash
# Проверьте переменную DATABASE_URL
# Убедитесь что PostgreSQL сервис запущен
```

### Проблема: Фронтенд не загружается
```bash
# Проверьте что frontend/dist создан
# Убедитесь что статические файлы настроены
```

---

## 🎉 Результат

После успешного деплоя:
- ✅ Сайт доступен по Railway домену
- ✅ API работает стабильно
- ✅ PostgreSQL база данных настроена
- ✅ Автоматическое масштабирование
- ✅ SSL сертификат включен

**Railway действительно делает деплой очень простым! 🚀**
