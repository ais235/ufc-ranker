# 🥊 UFC Ranker - Полнофункциональный сайт

Современный веб-сайт для отображения рейтингов UFC с функционалом сравнения бойцов и предстоящих кардов.

## ✨ Функционал

### 🏆 **Рейтинги UFC**
- Табы для переключения между весовыми категориями
- Карточки бойцов с фото и основной информацией
- Отдельное отображение чемпионов
- Поиск и фильтрация бойцов

### ⚖️ **Сравнение бойцов**
- Выбор двух бойцов для сравнения
- Таблица с физическими параметрами
- Выделение преимуществ каждого бойца
- Боевые рекорды и статистика

### 📅 **Предстоящие карды**
- Список предстоящих боев
- Фильтр по главным боям
- Информация о весовых категориях
- Статус титульных боев

### 👤 **Профили бойцов**
- Детальная информация о бойце
- Физические данные (рост, вес, размах рук)
- Боевой рекорд с процентом побед
- Фотографии и личная информация

## 🏗️ Архитектура

```
ufc-ranker/
├── parsers/              # Парсеры данных
│   ├── base_parser.py    # Базовый класс
│   ├── ufc_rankings.py   # Рейтинги UFC
│   ├── fighter_profiles.py # Профили бойцов
│   ├── upcoming_cards.py # Предстоящие карды
│   └── main.py           # Главный скрипт
├── backend/              # FastAPI бэкенд
│   └── app.py            # API приложение
├── frontend/             # React фронтенд
│   ├── src/
│   │   ├── components/   # React компоненты
│   │   ├── pages/        # Страницы
│   │   ├── services/     # API сервисы
│   │   └── types/        # TypeScript типы
│   └── package.json      # Зависимости
├── database/             # База данных
│   ├── models.py         # SQLAlchemy модели
│   └── config.py         # Конфигурация БД
└── legacy/               # Старые файлы
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

**Python (бэкенд):**
```bash
pip install -r requirements_new.txt
```

**Node.js (фронтенд):**
```bash
cd frontend
npm install
```

### 2. Инициализация базы данных

```bash
python -c "from database.config import init_database; init_database()"
```

### 3. Запуск парсеров (сбор данных)

```bash
# Все парсеры
python parsers/main.py all

# Или по отдельности
python parsers/main.py rankings    # Рейтинги
python parsers/main.py profiles    # Профили
python parsers/main.py cards       # Карды
```

### 4. Запуск приложения

**Терминал 1 - Бэкенд:**
```bash
python start_backend.py
```
API будет доступно по адресу: http://localhost:8000

**Терминал 2 - Фронтенд:**
```bash
# Windows
start_frontend.bat

# Linux/Mac
chmod +x start_frontend.sh
./start_frontend.sh
```
Фронтенд будет доступен по адресу: http://localhost:3000

## 📊 База данных

### Модели:
- **Fighter** - бойцы UFC
- **WeightClass** - весовые категории  
- **Ranking** - рейтинги бойцов
- **FightRecord** - боевые рекорды
- **UpcomingFight** - предстоящие бои
- **Event** - события UFC

### API эндпоинты:
- `GET /api/fighters` - список бойцов
- `GET /api/fighters/{id}` - детали бойца
- `GET /api/weight-classes` - весовые категории
- `GET /api/rankings/{class_id}` - рейтинг категории
- `GET /api/compare/{id1}/{id2}` - сравнение бойцов
- `GET /api/upcoming-fights` - предстоящие бои
- `GET /api/stats` - общая статистика

## 🎨 Дизайн

### Цветовая схема:
- **UFC Gold** (#d4af37) - чемпионы и акценты
- **UFC Dark** (#202733) - заголовки и навигация
- **UFC Blue** (#2f49d1) - кнопки и ссылки

### Компоненты:
- **Адаптивная верстка** - работает на всех устройствах
- **Современный UI** - градиенты, тени, анимации
- **Иконки Lucide** - красивые иконки
- **Tailwind CSS** - быстрая стилизация

## 🔧 Разработка

### Добавление нового парсера:
1. Создать класс наследующий `BaseParser`
2. Реализовать метод `parse()`
3. Добавить в `parsers/__init__.py`
4. Обновить `parsers/main.py`

### Добавление нового API эндпоинта:
1. Добавить функцию в `backend/app.py`
2. Создать Pydantic модель для ответа
3. Обновить фронтенд в `frontend/src/services/api.ts`

### Добавление новой страницы:
1. Создать компонент в `frontend/src/pages/`
2. Добавить маршрут в `frontend/src/App.tsx`
3. Обновить навигацию в `frontend/src/components/Header.tsx`

## 🐛 Отладка

### Логи:
- **Бэкенд**: логи в консоли FastAPI
- **Фронтенд**: логи в браузере (F12)
- **Парсеры**: логи в консоли Python

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

### Тестирование API:
- Документация: http://localhost:8000/docs
- Swagger UI: http://localhost:8000/redoc

## 📝 TODO

### Планируемые улучшения:
- [ ] Поиск бойцов по имени
- [ ] Фильтры по стране и весу
- [ ] История изменений рейтингов
- [ ] Уведомления о новых боях
- [ ] Мобильное приложение
- [ ] Админ панель
- [ ] Система пользователей
- [ ] Комментарии и обсуждения

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

MIT License - используйте свободно для личных и коммерческих проектов.

---

**UFC Ranker** - ваш надежный источник информации о UFC! 🥊






