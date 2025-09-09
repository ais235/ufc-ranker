# UFC Ranker - Новая структура

Современный сайт для отображения рейтингов UFC с функционалом сравнения бойцов и предстоящих кардов.

## 🏗️ Архитектура проекта

```
ufc-ranker/
├── parsers/              # Парсеры данных
│   ├── base_parser.py    # Базовый класс парсера
│   ├── ufc_rankings.py   # Парсер рейтингов
│   ├── fighter_profiles.py # Парсер профилей бойцов
│   ├── upcoming_cards.py # Парсер предстоящих кардов
│   └── main.py           # Главный скрипт
├── backend/              # FastAPI бэкенд
├── frontend/             # React фронтенд
├── database/             # База данных и модели
│   ├── models.py         # SQLAlchemy модели
│   └── config.py         # Конфигурация БД
├── legacy/               # Старые файлы
└── requirements_new.txt  # Новые зависимости
```

## 🚀 Быстрый старт

### 1. Установка зависимостей
```bash
pip install -r requirements_new.txt
```

### 2. Инициализация базы данных
```bash
python -c "from database.config import init_database; init_database()"
```

### 3. Запуск парсеров
```bash
# Все парсеры
python parsers/main.py all

# Только рейтинги
python parsers/main.py rankings

# Только профили
python parsers/main.py profiles

# Только карды
python parsers/main.py cards
```

## 📊 База данных

### Модели:
- **Fighter** - бойцы UFC
- **WeightClass** - весовые категории
- **Ranking** - рейтинги бойцов
- **FightRecord** - боевые рекорды
- **UpcomingFight** - предстоящие бои
- **Event** - события UFC

### Схема связей:
```
Fighter ←→ Ranking ←→ WeightClass
Fighter ←→ FightRecord
Fighter ←→ UpcomingFight ←→ WeightClass
Event ←→ UpcomingFight
```

## 🔧 Парсеры

### UFCRankingsParser
- Парсит рейтинги с fight.ru
- Извлекает чемпионов и рейтинговых бойцов
- Сохраняет в базу данных

### FighterProfilesParser
- Обновляет профили бойцов
- Извлекает фото, физические данные, рекорды
- Работает с кэшированием

### UpcomingCardsParser
- Парсит предстоящие карды с ufc.com
- Извлекает информацию о боях
- Связывает с существующими бойцами

## 🎯 Планируемый функционал

### Фронтенд:
1. **Главная страница** - табы с весовыми категориями
2. **Карточки бойцов** - с фото и основной информацией
3. **Страница бойца** - детальная информация
4. **Сравнение бойцов** - таблица параметров
5. **Предстоящие карды** - список событий

### Бэкенд API:
- `GET /api/fighters` - список бойцов
- `GET /api/fighters/{id}` - детали бойца
- `GET /api/weight-classes` - весовые категории
- `GET /api/rankings/{class_id}` - рейтинг категории
- `GET /api/compare/{id1}/{id2}` - сравнение бойцов
- `GET /api/upcoming-fights` - предстоящие бои

## 🔄 Миграция

Для перехода на новую структуру:
```bash
python migrate_to_new_structure.py
```

Это перенесет старые файлы в папку `legacy/`.

## 📝 Разработка

### Добавление нового парсера:
1. Создать класс наследующий `BaseParser`
2. Реализовать метод `parse()`
3. Добавить в `parsers/__init__.py`
4. Обновить `parsers/main.py`

### Добавление новой модели БД:
1. Создать класс в `database/models.py`
2. Добавить связи с существующими моделями
3. Создать миграцию
4. Обновить парсеры для работы с новой моделью

## 🐛 Отладка

### Логи парсеров:
- Кэш сохраняется в `.cache/`
- Ошибки выводятся в консоль
- База данных: `ufc_ranker.db`

### Проверка данных:
```python
from database.config import SessionLocal
from database.models import Fighter

db = SessionLocal()
fighters = db.query(Fighter).limit(5).all()
for fighter in fighters:
    print(f"{fighter.name_ru} - {fighter.country}")
db.close()
```
