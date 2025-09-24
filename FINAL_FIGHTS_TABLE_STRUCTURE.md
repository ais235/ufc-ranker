# ФИНАЛЬНАЯ СТРУКТУРА ТАБЛИЦЫ FIGHTS

**Дата исправления**: 2025-09-24  
**Таблица**: `fights`  
**Колонок**: 26  
**Записей**: 0 (готова для заполнения)

---

## 📋 ОПИСАНИЕ КОЛОНОК

| № | Колонка | Тип | NULL | По умолчанию | Описание |
|---|---------|-----|------|--------------|----------|
| 1 | id | INTEGER | NO | - | Уникальный идентификатор боя (PRIMARY KEY) |
| 2 | event_name | TEXT | YES | - | Название события |
| 3 | fighter1_name | TEXT | YES | - | **Имя первого бойца** |
| 4 | fighter2_name | TEXT | YES | - | **Имя второго бойца** |
| 5 | weight_class | TEXT | YES | - | Весовая категория (связана с weight_classes.name_en) |
| 6 | scheduled_rounds | INTEGER | YES | 3 | Запланированное количество раундов |
| 7 | method | TEXT | YES | - | Метод победы (TKO, Decision, Submission) |
| 8 | method_details | TEXT | YES | - | Детали метода победы |
| 9 | round | INTEGER | YES | - | Раунд завершения боя |
| 10 | time | TEXT | YES | - | Время в раунде |
| 11 | fight_date | DATE | YES | - | Дата боя |
| 12 | location | TEXT | YES | - | Место проведения |
| 13 | notes | TEXT | YES | - | Заметки о бое |
| 14 | is_title_fight | BOOLEAN | YES | 0 | Титульный бой |
| 15 | is_main_event | BOOLEAN | YES | 0 | Главное событие |
| 16 | is_win | TEXT | YES | - | **Имя бойца-победителя** |
| 17 | is_loss | TEXT | YES | - | **Имя бойца-проигравшего** |
| 18 | is_draw | TEXT | YES | - | **"Ничья" если есть ничья** |
| 19 | is_nc | TEXT | YES | - | **"No Contest" если есть NC** |
| 20 | fighter1_record | TEXT | YES | - | Рекорд fighter1 |
| 21 | fighter2_record | TEXT | YES | - | Рекорд fighter2 |
| 22 | fight_time_seconds | INTEGER | YES | - | Время боя в секундах |
| 23 | card_type | TEXT | YES | - | Тип карты |
| 24 | referee | TEXT | YES | - | Рефери |
| 25 | created_at | DATETIME | YES | CURRENT_TIMESTAMP | Дата создания записи |
| 26 | updated_at | DATETIME | YES | CURRENT_TIMESTAMP | Дата обновления записи |

---

## ✅ ИСПРАВЛЕНИЯ СТРУКТУРЫ

### **Удаленные колонки:**
- ❌ `fighter1_id` - заменена на `fighter1_name`
- ❌ `fighter2_id` - заменена на `fighter2_name`
- ❌ `winner_id` - заменена на `is_win` и `is_loss`
- ❌ `winner_name` - заменена на `is_win` и `is_loss`

### **Добавленные/измененные колонки:**
- ✅ `fighter1_name` - имя первого бойца (вместо `fighter1_id`)
- ✅ `fighter2_name` - имя второго бойца (вместо `fighter2_id`)
- ✅ `is_win` - имя бойца-победителя (TEXT)
- ✅ `is_loss` - имя бойца-проигравшего (TEXT)
- ✅ `is_draw` - "Ничья" если есть ничья (TEXT)
- ✅ `is_nc` - "No Contest" если есть NC (TEXT)

---

## 🔍 ЛОГИКА ЗАПОЛНЕНИЯ КОЛОНОК РЕЗУЛЬТАТА

### **Для победы одного из бойцов:**
```sql
-- Если fighter1 выиграл
is_win = 'Имя fighter1'
is_loss = 'Имя fighter2'
is_draw = NULL
is_nc = NULL

-- Если fighter2 выиграл
is_win = 'Имя fighter2'
is_loss = 'Имя fighter1'
is_draw = NULL
is_nc = NULL
```

### **Для ничьей:**
```sql
is_win = NULL
is_loss = NULL
is_draw = 'Ничья'
is_nc = NULL
```

### **Для No Contest:**
```sql
is_win = NULL
is_loss = NULL
is_draw = NULL
is_nc = 'No Contest'
```

---

## 📊 ПРИМЕРЫ ЗАПИСЕЙ

### **Пример 1: Победа fighter1**
```sql
INSERT INTO fights (
    event_name, fighter1_name, fighter2_name, weight_class,
    method, method_details, round, time, fight_date,
    is_win, is_loss, is_draw, is_nc
) VALUES (
    'UFC Fight Night: Lopes vs. Silva',
    'Diego Lopes', 'Jean Silva', 'Featherweight',
    'TKO', 'spinning back elbow and punches', 2, '4:48', '2025-09-13',
    'Diego Lopes', 'Jean Silva', NULL, NULL
);
```

### **Пример 2: Ничья**
```sql
INSERT INTO fights (
    event_name, fighter1_name, fighter2_name, weight_class,
    method, method_details, round, time, fight_date,
    is_win, is_loss, is_draw, is_nc
) VALUES (
    'UFC 300',
    'Fighter A', 'Fighter B', 'Lightweight',
    'Decision', 'split', 3, '5:00', '2025-04-13',
    NULL, NULL, 'Ничья', NULL
);
```

### **Пример 3: No Contest**
```sql
INSERT INTO fights (
    event_name, fighter1_name, fighter2_name, weight_class,
    method, method_details, round, time, fight_date,
    is_win, is_loss, is_draw, is_nc
) VALUES (
    'UFC 301',
    'Fighter C', 'Fighter D', 'Welterweight',
    'NC', 'accidental eye poke', 1, '2:30', '2025-05-04',
    NULL, NULL, NULL, 'No Contest'
);
```

---

## 🔗 ИНДЕКСЫ

Созданы следующие индексы для оптимизации запросов:

- `idx_fights_event_name` - по названию события
- `idx_fights_fighter1_name` - по имени первого бойца
- `idx_fights_fighter2_name` - по имени второго бойца
- `idx_fights_date` - по дате боя
- `idx_fights_weight_class` - по весовой категории
- `idx_fights_is_win` - по победителю
- `idx_fights_is_loss` - по проигравшему

---

## 🎯 ПРЕИМУЩЕСТВА НОВОЙ СТРУКТУРЫ

### **1. Упрощение запросов:**
- Не нужно делать JOIN для получения имен бойцов
- Все данные о результате в одной строке
- Простой поиск по именам бойцов

### **2. Гибкость результатов:**
- Поддержка всех типов результатов (победа, поражение, ничья, NC)
- Четкое разделение победителя и проигравшего
- Текстовые значения для лучшей читаемости

### **3. Производительность:**
- Меньше JOIN операций
- Быстрый поиск по именам
- Оптимизированные индексы

---

## ✅ ЗАКЛЮЧЕНИЕ

Таблица `fights` теперь полностью соответствует требованиям:

1. ✅ **Удалены ID колонки** (`fighter1_id`, `fighter2_id`, `winner_id`)
2. ✅ **Добавлены имена бойцов** (`fighter1_name`, `fighter2_name`)
3. ✅ **Изменена логика результатов** (`is_win`, `is_loss`, `is_draw`, `is_nc`)
4. ✅ **Упрощена структура** (нет внешних ключей на бойцов)
5. ✅ **Оптимизированы индексы** для быстрого поиска

**Таблица готова для заполнения парсерами!** 🚀
