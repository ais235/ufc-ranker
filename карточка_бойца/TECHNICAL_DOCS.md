# Техническая документация - Карточка бойца UFC

## Архитектура

### Структура файлов
```
карточка_бойца/
├── README.md                    # Основная документация
├── TECHNICAL_DOCS.md           # Техническая документация
├── topuria_fighter_card.html   # Готовая карточка
├── generate_topuria_fighter_card.py  # Генератор карточек
└── Topuria.jpg                 # Фотография бойца
```

## База данных

### Таблица `fighters`
Основная таблица с информацией о бойцах:
- `name_ru`, `name_en` - имена на русском и английском
- `nickname` - никнейм
- `country`, `birth_place` - страна и место рождения
- `height`, `weight`, `reach` - физические характеристики
- `age`, `birth_date` - возраст и дата рождения
- `weight_class` - весовая категория
- `stance`, `team`, `belt_rank` - боевые характеристики
- `wins`, `losses`, `draws` - статистика боев

### Таблица `fights`
Информация о боях:
- `event_name`, `fight_date` - событие и дата
- `fighter1_name`, `fighter2_name` - участники
- `method`, `round`, `time` - детали боя
- `referee` - судья
- `is_win` - результат для первого бойца

### Таблица `rankings`
Рейтинги бойцов:
- `rank_position` - позиция в рейтинге
- `weight_class` - весовая категория

## CSS Архитектура

### Основные компоненты

#### `.fighter-main-card`
Главный контейнер карточки бойца:
```css
display: grid;
grid-template-columns: 300px 1fr;
gap: 30px;
position: relative;
```

#### `.fighter-info`
Информация о бойце в 4 колонки:
```css
display: grid;
grid-template-columns: 1fr 1fr 1fr 1fr;
gap: 15px;
```

#### `.fight-card`
Блок с информацией о бое:
```css
display: grid;
grid-template-columns: auto 1fr auto;
gap: 20px;
align-items: center;
```

### Цветовая система

#### Основные цвета
```css
:root {
  --primary-gold: #d4af37;
  --secondary-gold: #ffd700;
  --background-dark: #1a1a1a;
  --background-light: #2d2d2d;
  --text-primary: #fff;
  --text-secondary: #bdc3c7;
}
```

#### Цвета результатов
```css
.wins { color: #27ae60; border-color: #27ae60; }
.losses { color: #e74c3c; border-color: #e74c3c; }
.draws { color: #f39c12; border-color: #f39c12; }
```

## JavaScript/API

### Генератор карточек

#### Класс `TopuriaFighterCardGenerator`

##### Методы:
- `get_fighter_data(fighter_name)` - получение данных бойца
- `get_fighter_fights(fighter_name, limit=5)` - получение последних боев
- `get_fighter_rankings(fighter_name)` - получение рейтинга
- `get_upcoming_events(limit=5)` - получение предстоящих событий
- `generate_html(...)` - генерация HTML
- `generate_card(fighter_name)` - основная функция генерации

##### Пример использования:
```python
generator = TopuriaFighterCardGenerator("ufc_ranker_v2.db")
generator.generate_card("Topuria")
```

## Адаптивность

### Breakpoints
- **Desktop**: `> 768px` - 4 колонки информации
- **Mobile**: `≤ 768px` - 1 колонка информации

### Медиа-запросы
```css
@media (max-width: 768px) {
  .fighter-main-card {
    grid-template-columns: 1fr;
  }
  .fighter-info {
    grid-template-columns: 1fr;
  }
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
```

## Производительность

### Оптимизации
- Использование CSS Grid для эффективной раскладки
- `backdrop-filter` для визуальных эффектов
- Минимальное количество DOM-элементов
- Оптимизированные изображения

### Загрузка данных
- Ограничение запросов к БД (LIMIT 5 для боев)
- Кэширование результатов
- Обработка ошибок для отсутствующих данных

## Безопасность

### Валидация данных
- Проверка существования бойца в БД
- Обработка NULL значений
- Экранирование HTML-символов

### SQL Injection
- Использование параметризованных запросов
- Валидация входных параметров

## Тестирование

### Тестовые данные
- Использование реальных данных из БД UFC
- Тестирование с различными именами бойцов
- Проверка обработки отсутствующих данных

### Браузерная совместимость
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Развертывание

### Требования
- Python 3.7+
- SQLite3
- Веб-сервер (опционально)

### Установка
```bash
# Клонирование репозитория
git clone <repository-url>
cd ufc-ranker

# Установка зависимостей
pip install -r requirements.txt

# Генерация карточки
python карточка_бойца/generate_topuria_fighter_card.py
```

## Мониторинг

### Логирование
- Использование Python logging
- Уровни: INFO, ERROR
- Формат: timestamp - level - message

### Метрики
- Время генерации карточки
- Количество запросов к БД
- Размер генерируемого HTML

## Будущие улучшения

### Планируемые функции
- Интеграция с UFC API
- Кэширование карточек
- Адаптивные изображения
- PWA функциональность

### Технический долг
- Рефакторинг CSS (использование CSS переменных)
- Добавление TypeScript для JavaScript
- Улучшение обработки ошибок
- Добавление unit-тестов







