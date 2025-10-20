# 🌐 Подключение домена voltfighters.ru к PythonAnywhere

## 📋 Пошаговая инструкция

### Шаг 1: Обновление плана PythonAnywhere

Для подключения собственного домена нужен **платный план**:

1. **Hacker план ($5/месяц)** - минимальный для собственного домена
2. **Web Developer план ($12/месяц)** - рекомендуется для продакшена

### Шаг 2: Настройка DNS записей

В панели управления вашего регистратора домена (где покупали voltfighters.ru) добавьте:

#### A-запись (основная):
```
Тип: A
Имя: @ (или оставить пустым)
Значение: 185.199.108.153
TTL: 3600 (или минимальное значение)
```

#### CNAME запись (для www):
```
Тип: CNAME
Имя: www
Значение: voltfighters.ru
TTL: 3600
```

### Шаг 3: Настройка в PythonAnywhere

1. **Войдите в панель PythonAnywhere**
2. **Перейдите в раздел Web**
3. **Нажмите "Add a new web app"**
4. **Выберите "Manual configuration"**
5. **Выберите Python 3.10**

### Шаг 4: Настройка домена

1. **В разделе "Domains" добавьте:**
   - `voltfighters.ru`
   - `www.voltfighters.ru`

2. **В разделе "Code" укажите путь:**
   ```
   /home/yourusername/ufc-ranker
   ```

### Шаг 5: WSGI конфигурация

В разделе **WSGI configuration file** замените содержимое на:

```python
import sys
import os

# Добавляем путь к проекту
path = '/home/yourusername/ufc-ranker'  # Замените yourusername на ваш username
if path not in sys.path:
    sys.path.append(path)

# Импортируем FastAPI приложение
from backend.app import app

# WSGI приложение
application = app
```

### Шаг 6: Настройка статических файлов

В разделе **Static files** добавьте:

1. **Основные статические файлы:**
   - **URL**: `/static/`
   - **Directory**: `/home/yourusername/ufc-ranker/frontend/dist/`

2. **Медиа файлы:**
   - **URL**: `/media/`
   - **Directory**: `/home/yourusername/ufc-ranker/media/`

### Шаг 7: Переменные окружения

В разделе **Environment variables** добавьте:

```
DATABASE_URL=sqlite:///./ufc_ranker_v2.db
DEBUG=False
SITE_DOMAIN=voltfighters.ru
SITE_URL=https://voltfighters.ru
```

### Шаг 8: SSL сертификат

PythonAnywhere автоматически предоставляет SSL сертификат:

1. **В разделе "SSL"**
2. **Нажмите "Enable HTTPS"**
3. **Дождитесь активации сертификата**

## 🔧 Проверка работы

### После настройки проверьте:

1. **Основной домен:** `https://voltfighters.ru`
2. **С www:** `https://www.voltfighters.ru`
3. **API:** `https://voltfighters.ru/api/fighters`
4. **Документация:** `https://voltfighters.ru/docs`

## ⏱️ Время активации

- **DNS изменения:** 1-24 часа (обычно 1-2 часа)
- **SSL сертификат:** 5-30 минут
- **Общее время:** до 24 часов

## 🚨 Возможные проблемы

### Проблема: Домен не открывается
**Решение:**
1. Проверьте DNS записи
2. Убедитесь что прошло достаточно времени (до 24 часов)
3. Проверьте настройки в PythonAnywhere

### Проблема: SSL ошибка
**Решение:**
1. Дождитесь активации SSL сертификата
2. Проверьте что домен правильно настроен

### Проблема: CORS ошибки
**Решение:**
1. Обновите `backend/app.py` с правильными доменами
2. Перезапустите приложение

## 📊 Мониторинг

1. **Логи:** Проверяйте логи в разделе Web → Log files
2. **Статус:** Следите за статусом домена в разделе Web
3. **SSL:** Проверяйте статус SSL сертификата

## 💰 Стоимость

- **Hacker план:** $5/месяц
- **Web Developer план:** $12/месяц
- **Домен:** уже у вас есть
- **SSL:** бесплатно с PythonAnywhere

## 🎯 Итоговый результат

После настройки ваш сайт будет доступен по адресам:
- `https://voltfighters.ru` (основной)
- `https://www.voltfighters.ru` (с www)
- `http://voltfighters.ru` (HTTP версия)
- `http://www.voltfighters.ru` (HTTP с www)

---

**Удачи с настройкой домена! 🚀**
