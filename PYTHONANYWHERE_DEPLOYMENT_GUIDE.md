# 🚀 Инструкция по деплою UFC Ranker на PythonAnywhere

## 📋 Подготовка

### 1. Зарегистрируйтесь на PythonAnywhere
- Перейдите на [https://www.pythonanywhere.com/](https://www.pythonanywhere.com/)
- Создайте аккаунт (бесплатный план подойдет для начала)
- Запомните ваш username (будет в URL: `yourusername.pythonanywhere.com`)

### 2. Подготовьте файлы локально
Убедитесь что у вас есть все необходимые файлы:
```
ufc-ranker/
├── pythonanywhere_wsgi.py      # WSGI конфигурация
├── pythonanywhere_config.py    # Конфигурация для PA
├── main.py                     # Точка входа
├── requirements.txt            # Зависимости
├── backend/                    # FastAPI приложение
├── frontend/                   # React приложение
├── database/                   # Модели БД
├── parsers/                    # Парсеры
└── ufc_ranker_v2.db           # База данных
```

## 🔧 Деплой на PythonAnywhere

### Шаг 1: Загрузите файлы

#### Вариант A: Через Git (рекомендуется)
1. Откройте **Console** в PythonAnywhere
2. Выполните команды:
```bash
# Клонируйте ваш репозиторий
git clone https://github.com/ais235/ufc-ranker.git
cd ufc-ranker

# Установите зависимости
pip3.10 install --user -r requirements.txt
```

#### Вариант B: Через загрузку файлов
1. Откройте **Files** в PythonAnywhere
2. Создайте папку `ufc-ranker`
3. Загрузите все файлы проекта через веб-интерфейс

### Шаг 2: Настройте базу данных

1. В **Console** выполните:
```bash
cd ufc-ranker
python3.10 -c "from database.config import init_database; init_database()"
```

### Шаг 3: Соберите фронтенд

1. В **Console** выполните:
```bash
cd ufc-ranker/frontend
npm install
npm run build
```

### Шаг 4: Настройте WSGI

1. Откройте **Web** в PythonAnywhere
2. Нажмите **Add a new web app**
3. Выберите **Manual configuration**
4. Выберите **Python 3.10**
5. В разделе **Code** укажите путь: `/home/yourusername/ufc-ranker`
6. В разделе **WSGI configuration file** замените содержимое на:

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

### Шаг 5: Настройте статические файлы

1. В разделе **Static files** добавьте:
   - **URL**: `/static/`
   - **Directory**: `/home/yourusername/ufc-ranker/frontend/dist/`

2. Добавьте еще одну запись:
   - **URL**: `/media/`
   - **Directory**: `/home/yourusername/ufc-ranker/media/`

### Шаг 6: Настройте переменные окружения

1. В разделе **Environment variables** добавьте:
   - `DATABASE_URL`: `sqlite:///./ufc_ranker_v2.db`
   - `DEBUG`: `False`

### Шаг 7: Перезапустите приложение

1. Нажмите **Reload** в разделе Web
2. Проверьте логи на наличие ошибок

## 🌐 Проверка работы

1. Откройте ваш сайт: `https://yourusername.pythonanywhere.com`
2. Проверьте API: `https://yourusername.pythonanywhere.com/api/fighters`
3. Проверьте документацию: `https://yourusername.pythonanywhere.com/docs`

## 🔧 Возможные проблемы и решения

### Проблема: Ошибка импорта модулей
**Решение**: Убедитесь что все пути в `pythonanywhere_wsgi.py` правильные

### Проблема: База данных не найдена
**Решение**: Проверьте что файл `ufc_ranker_v2.db` загружен в корень проекта

### Проблема: Статические файлы не загружаются
**Решение**: Проверьте настройки Static files в Web разделе

### Проблема: CORS ошибки
**Решение**: Обновите `backend/app.py` с правильным доменом PythonAnywhere

## 📊 Мониторинг

1. **Логи**: Проверяйте логи в разделе Web → Log files
2. **Консоль**: Используйте Console для отладки
3. **Файлы**: Проверяйте файлы через Files раздел

## 💰 Обновление плана

- **Бесплатный план**: 1 веб-приложение, ограниченное время CPU
- **Hacker план ($5/месяц)**: Больше CPU времени, собственный домен
- **Web Developer план ($12/месяц)**: Еще больше ресурсов

## 🎯 Следующие шаги

1. Протестируйте все функции сайта
2. Настройте собственный домен (если нужно)
3. Настройте автоматические задачи для обновления данных
4. Добавьте мониторинг и логирование

## 📞 Поддержка

Если возникнут проблемы:
1. Проверьте логи в PythonAnywhere
2. Обратитесь в поддержку PythonAnywhere
3. Проверьте документацию FastAPI и PythonAnywhere

---

**Удачи с деплоем! 🚀**
