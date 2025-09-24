# ОПИСАНИЕ КОЛОНОК ТАБЛИЦЫ FIGHTS

## 📋 Основная информация о таблице
- **Название**: `fights`
- **Назначение**: Хранение информации о боях UFC
- **Всего колонок**: 29
- **Первичный ключ**: `id`

---

## 🔍 Подробное описание колонок

### 1. **id** (INTEGER, PRIMARY KEY)
- **Назначение**: Уникальный идентификатор боя
- **Тип**: Автоинкремент
- **Пример**: 1, 2, 3...

### 2. **event_id** (INTEGER)
- **Назначение**: Ссылка на событие UFC, в котором проходил бой
- **Связь**: FOREIGN KEY → `events(id)`
- **Пример**: 1 (UFC 314), 2 (UFC Fight Night: Lopes vs. Silva)

### 3. **fighter1_id** (INTEGER)
- **Назначение**: ID первого бойца (основного бойца, чья страница парсилась)
- **Связь**: FOREIGN KEY → `fighters(id)`
- **Пример**: 1 (Diego Lopes), 2 (Jean Silva)

### 4. **fighter2_id** (INTEGER)
- **Назначение**: ID второго бойца (соперника)
- **Связь**: FOREIGN KEY → `fighters(id)`
- **Может быть NULL**: Да (если соперник не найден в базе)
- **Пример**: 2 (Jean Silva), 3 (Alexander Volkanovski)

### 5. **winner_id** (INTEGER)
- **Назначение**: ID победителя боя
- **Связь**: FOREIGN KEY → `fighters(id)`
- **Может быть NULL**: Да (если ничья или NC)
- **Пример**: 1 (Diego Lopes), 2 (Jean Silva)

### 6. **weight_class_id** (INTEGER)
- **Назначение**: ID весовой категории боя
- **Связь**: FOREIGN KEY → `weight_classes(id)`
- **Пример**: 1 (Featherweight), 2 (Lightweight)

### 7. **scheduled_rounds** (INTEGER)
- **Назначение**: Запланированное количество раундов
- **Пример**: 3 (обычный бой), 5 (титульный бой)

### 8. **method** (VARCHAR(200))
- **Назначение**: Метод победы
- **Пример**: "TKO", "Decision", "Submission", "KO"

### 9. **method_details** (TEXT)
- **Назначение**: Детали метода победы (решения судей, детали)
- **Пример**: "unanimous", "split", "spinning back elbow and punches"

### 10. **round** (INTEGER)
- **Назначение**: Раунд, в котором завершился бой
- **Пример**: 1, 2, 3, 4, 5

### 11. **time** (VARCHAR(20))
- **Назначение**: Время в раунде, когда завершился бой
- **Пример**: "4:48", "5:00", "1:29"

### 12. **fight_date** (DATE)
- **Назначение**: Дата проведения боя
- **Формат**: YYYY-MM-DD
- **Пример**: "2025-09-13", "2025-04-12"

### 13. **location** (VARCHAR(200))
- **Назначение**: Место проведения боя
- **Пример**: "San Antonio, Texas, United States", "Miami, Florida, United States"

### 14. **notes** (TEXT)
- **Назначение**: Дополнительные заметки о бое
- **Пример**: "Performance of the Night", "Fight of the Night", "For the vacant UFC Featherweight Championship"

### 15. **is_title_fight** (BOOLEAN)
- **Назначение**: Является ли бой титульным
- **Значения**: 0 (нет), 1 (да)
- **Пример**: 1 (титульный бой за чемпионский пояс)

### 16. **is_main_event** (BOOLEAN)
- **Назначение**: Является ли бой главным событием
- **Значения**: 0 (нет), 1 (да)
- **Пример**: 1 (главный бой карты)

### 17. **is_win** (BOOLEAN)
- **Назначение**: Победа для fighter1
- **Значения**: 0 (нет), 1 (да)
- **Пример**: 1 (fighter1 выиграл)

### 18. **is_loss** (BOOLEAN)
- **Назначение**: Поражение для fighter1
- **Значения**: 0 (нет), 1 (да)
- **Пример**: 1 (fighter1 проиграл)

### 19. **is_draw** (BOOLEAN)
- **Назначение**: Ничья
- **Значения**: 0 (нет), 1 (да)
- **Пример**: 1 (ничья)

### 20. **is_nc** (BOOLEAN)
- **Назначение**: No Contest (не состоялся)
- **Значения**: 0 (нет), 1 (да)
- **Пример**: 1 (бой не состоялся)

### 21. **opponent_name** (VARCHAR(200))
- **Назначение**: Имя соперника (для случаев, когда fighter2_id = NULL)
- **Пример**: "Jean Silva", "Alexander Volkanovski"

### 22. **fight_time_seconds** (INTEGER)
- **Назначение**: Общее время боя в секундах
- **Пример**: 300 (5 минут), 1200 (20 минут)

### 23. **card_type** (VARCHAR(50))
- **Назначение**: Тип карты боя
- **Пример**: "main_card", "preliminary_card", "early_preliminary_card"

### 24. **referee** (VARCHAR(100))
- **Назначение**: Имя рефери
- **Пример**: "Herb Dean", "Marc Goddard"

### 25. **created_at** (DATETIME)
- **Назначение**: Дата и время создания записи
- **Формат**: YYYY-MM-DD HH:MM:SS
- **Пример**: "2025-09-24 01:30:23"

### 26. **updated_at** (DATETIME)
- **Назначение**: Дата и время последнего обновления записи
- **Формат**: YYYY-MM-DD HH:MM:SS
- **Пример**: "2025-09-24 01:30:23"

### 27. **fighter1_record** (VARCHAR(20))
- **Назначение**: Рекорд fighter1 на момент боя
- **Формат**: "W-L-D" (победы-поражения-ничьи)
- **Пример**: "27-7-0", "16-2-0"

### 28. **fighter2_record** (VARCHAR(20))
- **Назначение**: Рекорд fighter2 на момент боя
- **Формат**: "W-L-D" (победы-поражения-ничьи)
- **Пример**: "16-2-0", "27-7-0"

### 29. **event_name** (VARCHAR(200))
- **Назначение**: Название события (для быстрого поиска)
- **Пример**: "UFC Fight Night: Lopes vs. Silva", "UFC 314"

---

## 🔗 Связи с другими таблицами

### Внешние ключи:
- `event_id` → `events(id)`
- `fighter1_id` → `fighters(id)`
- `fighter2_id` → `fighters(id)`
- `winner_id` → `fighters(id)`
- `weight_class_id` → `weight_classes(id)`

### Индексы (рекомендуемые):
- `event_id` - для быстрого поиска боев по событию
- `fighter1_id` - для быстрого поиска боев бойца
- `fighter2_id` - для быстрого поиска боев бойца
- `fight_date` - для сортировки по дате
- `event_name` - для поиска по названию события

---

## 📊 Пример записи

```sql
INSERT INTO fights (
    event_id, fighter1_id, fighter2_id, winner_id,
    method, method_details, round, time, fight_date,
    location, notes, fighter1_record, fighter2_record,
    event_name, is_win, is_loss, is_draw, is_nc
) VALUES (
    2, 1, 2, 1,  -- event_id=2, Diego Lopes vs Jean Silva, Diego выиграл
    'TKO', 'spinning back elbow and punches', 2, '4:48', '2025-09-13',
    'San Antonio, Texas, United States', 'Performance of the Night. Fight of the Night.',
    '27', '16', 'UFC Fight Night: Lopes vs. Silva',
    1, 0, 0, 0  -- is_win=1 (Diego выиграл)
);
```

---

## 🎯 Назначение таблицы

Таблица `fights` является центральной для хранения информации о всех боях UFC. Она связывает:
- **События** (events) - где проходил бой
- **Бойцов** (fighters) - кто участвовал в бою
- **Весовые категории** (weight_classes) - в какой категории проходил бой
- **Детали боя** - метод, раунд, время, место, заметки
- **Результаты** - кто выиграл, рекорды бойцов


