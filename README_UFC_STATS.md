
# UFC Stats Integration

Интеграция данных ufc.stats в проект UFC Ranker для расширенной статистики боев.

## 🚀 Новые возможности

### Расширенная база данных
- **37 переменных статистики** как в оригинальном проекте ufc.stats
- **Детальная статистика по раундам** для каждого боя
- **Агрегированная статистика бойцов** по всем боям
- **События UFC** с полной информацией

### Новые API эндпоинты

#### События
- `GET /api/events` - Список событий UFC
- `GET /api/events/{id}` - Детали события

#### Бои
- `GET /api/fights` - Список боев
- `GET /api/fights/{id}` - Детали боя
- `GET /api/fights/{id}/stats` - Статистика боя по раундам

#### Статистика бойцов
- `GET /api/fighters/{id}/stats` - Полная статистика бойца
- `GET /api/fighters/{id}/fights` - Бои бойца

#### Обновление данных
- `POST /api/refresh-ufc-stats` - Обновление данных (аналог refresh_data())

## 📊 Структура данных

### Основные таблицы
- `events` - События UFC
- `fights` - Бои
- `fight_stats` - Детальная статистика по раундам
- `fighters` - Бойцы (расширена)
- `weight_classes` - Весовые категории

### Переменные статистики (37 штук)
- **Удары**: significant_strikes_landed, significant_strikes_attempted, significant_strikes_rate
- **Тейкдауны**: takedown_successful, takedown_attempted, takedown_rate
- **Части тела**: head_landed, body_landed, leg_landed
- **Дистанция**: distance_landed, clinch_landed, ground_landed
- **Специальные**: knockdowns, submission_attempt, reversals
- **Время**: round, result, last_round, time, scheduled_rounds
- **Результат**: winner, weight_class, event, fight_date, location, attendance

## 🛠 Установка и запуск

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Инициализация базы данных
```bash
python -c "from database.config import init_database; init_database()"
```

### 3. Загрузка данных ufc.stats
```bash
# Автоматическое обновление
python refresh_ufc_stats.py

# Или через скрипт
python start_ufc_stats_update.py
```

### 4. Запуск сервера
```bash
# Backend
python backend/app.py

# Frontend
cd frontend
npm install
npm run dev
```

## 🔄 Обновление данных

### Автоматическое обновление
```python
from parsers.ufc_stats_importer import UFCStatsImporter

importer = UFCStatsImporter()
importer.refresh_data()  # Аналог refresh_data() из ufc.stats
```

### Через API
```bash
curl -X POST http://localhost:8000/api/refresh-ufc-stats
```

### Через веб-интерфейс
Нажмите кнопку "Обновить данные ufc.stats" на главной странице.

## 📈 Использование

### Получение статистики бойца
```python
import requests

# Получить статистику бойца
response = requests.get('http://localhost:8000/api/fighters/1/stats')
stats = response.json()

print(f"Боев: {stats['total_fights']}")
print(f"Точность ударов: {stats['average_significant_strikes_rate']}%")
print(f"Тейкдауны: {stats['total_takedowns_successful']}")
```

### Получение статистики боя
```python
# Получить статистику конкретного боя
response = requests.get('http://localhost:8000/api/fights/1/stats')
fight_stats = response.json()

for round_stat in fight_stats:
    print(f"Раунд {round_stat['round_number']}: {round_stat['significant_strikes_landed']} ударов")
```

## 🎯 Преимущества над оригинальным ufc.stats

1. **Веб-интерфейс** - удобное отображение данных
2. **REST API** - легкая интеграция с другими системами
3. **Актуальные данные** - автоматическое обновление
4. **Расширенная функциональность** - сравнение бойцов, рейтинги
5. **Современная архитектура** - FastAPI + React + TypeScript

## 🔧 Настройка

### Источники данных
По умолчанию используются тестовые данные. Для подключения реальных данных ufc.stats:

1. Найдите актуальный источник данных
2. Обновите URL в `parsers/ufc_stats_importer.py`
3. Настройте парсинг под формат данных

### Кэширование
Данные кэшируются в папке `.cache/ufc_stats/` для ускорения повторных загрузок.

## 📝 Примеры запросов

### Статистика топ-бойцов по ударам
```sql
SELECT 
    f.name_ru,
    SUM(fs.significant_strikes_landed) as total_strikes,
    AVG(fs.significant_strikes_rate) as avg_accuracy
FROM fighters f
JOIN fight_stats fs ON f.id = fs.fighter_id
GROUP BY f.id, f.name_ru
ORDER BY total_strikes DESC
LIMIT 10;
```

### Самые точные бойцы
```sql
SELECT 
    f.name_ru,
    AVG(fs.significant_strikes_rate) as avg_accuracy,
    COUNT(*) as rounds
FROM fighters f
JOIN fight_stats fs ON f.id = fs.fighter_id
WHERE fs.significant_strikes_attempted > 10
GROUP BY f.id, f.name_ru
HAVING rounds >= 5
ORDER BY avg_accuracy DESC
LIMIT 10;
```

## 🚨 Примечания

- Тестовые данные генерируются автоматически для демонстрации
- Для продакшена настройте реальные источники данных
- Регулярно обновляйте данные для актуальности
- Мониторьте производительность при больших объемах данных
