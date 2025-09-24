# ИСПРАВЛЕННАЯ СТРУКТУРА БАЗЫ ДАННЫХ UFC RANKER

**Дата исправления**: 2025-09-24  
**База данных**: `ufc_ranker_v2.db`  
**Всего таблиц**: 8  
**Всего записей**: 176 бойцов, 176 рейтингов, 18 событий

---

## 📋 ТАБЛИЦА: events

**Назначение**: Хранение информации о событиях UFC  
**Колонок**: 19  
**Записей**: 18  
**Первичный ключ**: `id`

| № | Колонка | Тип | NULL | По умолчанию | Описание |
|---|---------|-----|------|--------------|----------|
| 1 | id | INTEGER | NO | - | Уникальный идентификатор события (PRIMARY KEY) |
| 2 | name | TEXT | NO | - | Название события |
| 3 | event_number | TEXT | YES | - | Номер события (например, "747") |
| 4 | event_type | TEXT | YES | - | Тип события (UFC Fight Night, UFC PPV) |
| 5 | date | DATE | YES | - | Дата проведения события |
| 6 | venue | TEXT | YES | - | Место проведения |
| 7 | venue_url | TEXT | YES | - | URL места проведения |
| 8 | location | TEXT | YES | - | Город и страна |
| 9 | location_url | TEXT | YES | - | URL локации |
| 10 | event_url | TEXT | YES | - | URL страницы события |
| 11 | reference_url | TEXT | YES | - | URL источника |
| 12 | status | TEXT | YES | - | Статус события (completed, upcoming) |
| 13 | attendance | INTEGER | YES | - | Количество зрителей |
| 14 | gate_revenue | TEXT | YES | - | Выручка от билетов |
| 15 | description | TEXT | YES | - | Описание события |
| 16 | image_url | TEXT | YES | - | URL изображения события |
| 17 | is_upcoming | BOOLEAN | YES | 1 | Является ли предстоящим событием |
| 18 | created_at | DATETIME | YES | CURRENT_TIMESTAMP | Дата создания записи |
| 19 | updated_at | DATETIME | YES | CURRENT_TIMESTAMP | Дата обновления записи |

---

## 📋 ТАБЛИЦА: fighters

**Назначение**: Хранение информации о бойцах UFC  
**Колонок**: 34  
**Записей**: 176  
**Первичный ключ**: `id`

| № | Колонка | Тип | NULL | По умолчанию | Описание |
|---|---------|-----|------|--------------|----------|
| 1 | id | INTEGER | NO | - | Уникальный идентификатор бойца (PRIMARY KEY) |
| 2 | name | TEXT | NO | - | Полное имя бойца |
| 3 | name_ru | TEXT | YES | - | Имя на русском языке |
| 4 | name_en | TEXT | YES | - | Имя на английском языке |
| 5 | nickname | TEXT | YES | - | Прозвище бойца |
| 6 | country | TEXT | YES | - | Страна бойца |
| 7 | country_flag_url | TEXT | YES | - | URL флага страны |
| 8 | image_url | TEXT | YES | - | URL фотографии бойца |
| 9 | profile_url | TEXT | YES | - | URL профиля бойца |
| 10 | height | INTEGER | YES | - | Рост в см |
| 11 | weight | INTEGER | YES | - | Вес в кг |
| 12 | reach | INTEGER | YES | - | Размах рук в см |
| 13 | age | INTEGER | YES | - | Возраст |
| 14 | birth_date | DATE | YES | - | Дата рождения |
| 15 | weight_class | TEXT | YES | - | Весовая категория |
| 16 | wins | INTEGER | YES | 0 | Количество побед |
| 17 | losses | INTEGER | YES | 0 | Количество поражений |
| 18 | draws | INTEGER | YES | 0 | Количество ничьих |
| 19 | no_contests | INTEGER | YES | 0 | Количество NC |
| 20 | ufc_wins | INTEGER | YES | 0 | Победы в UFC |
| 21 | ufc_losses | INTEGER | YES | 0 | Поражения в UFC |
| 22 | ufc_draws | INTEGER | YES | 0 | Ничьи в UFC |
| 23 | ufc_no_contests | INTEGER | YES | 0 | NC в UFC |
| 24 | career | TEXT | YES | - | Карьера бойца |
| 25 | birth_place | TEXT | YES | - | Место рождения |
| 26 | stance | TEXT | YES | - | Стойка бойца |
| 27 | team | TEXT | YES | - | Команда/зал |
| 28 | trainer | TEXT | YES | - | Тренер |
| 29 | belt_rank | TEXT | YES | - | Ранг пояса |
| 30 | years_active | TEXT | YES | - | Годы активности |
| 31 | current_division | TEXT | YES | - | Текущий дивизион |
| 32 | fighting_out_of | TEXT | YES | - | Откуда борется |
| 33 | created_at | DATETIME | YES | CURRENT_TIMESTAMP | Дата создания записи |
| 34 | updated_at | DATETIME | YES | CURRENT_TIMESTAMP | Дата обновления записи |

**✅ ИСПРАВЛЕНИЯ:**
- ❌ Удалена колонка `full_name` (лишняя)

---

## 📋 ТАБЛИЦА: fights

**Назначение**: Хранение информации о боях UFC  
**Колонок**: 25  
**Записей**: 0  
**Первичный ключ**: `id`

| № | Колонка | Тип | NULL | По умолчанию | Описание |
|---|---------|-----|------|--------------|----------|
| 1 | id | INTEGER | NO | - | Уникальный идентификатор боя (PRIMARY KEY) |
| 2 | event_name | TEXT | YES | - | Название события (вместо event_id) |
| 3 | fighter1_id | INTEGER | NO | - | ID первого бойца (FOREIGN KEY → fighters.id) |
| 4 | fighter2_id | INTEGER | NO | - | ID второго бойца (FOREIGN KEY → fighters.id) |
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
| 16 | fighter1_name | TEXT | YES | - | Имя первого бойца |
| 17 | fighter2_name | TEXT | YES | - | Имя второго бойца |
| 18 | winner_name | TEXT | YES | - | Имя победителя |
| 19 | fighter1_record | TEXT | YES | - | Рекорд fighter1 |
| 20 | fighter2_record | TEXT | YES | - | Рекорд fighter2 |
| 21 | fight_time_seconds | INTEGER | YES | - | Время боя в секундах |
| 22 | card_type | TEXT | YES | - | Тип карты |
| 23 | referee | TEXT | YES | - | Рефери |
| 24 | created_at | DATETIME | YES | CURRENT_TIMESTAMP | Дата создания записи |
| 25 | updated_at | DATETIME | YES | CURRENT_TIMESTAMP | Дата обновления записи |

**✅ ИСПРАВЛЕНИЯ:**
- ❌ Удален `event_id` (заменен на `event_name`)
- ❌ Удален `weight_class_id` (заменен на `weight_class`)
- ❌ Удален `result` (лишняя колонка)
- ❌ Удален `winner_id` (заменен на `winner_name`)
- ❌ Удален `opponent_name` (заменен на `fighter2_name`)
- ✅ Добавлены `fighter1_name`, `fighter2_name`, `winner_name`
- ✅ `event_name` перемещен на позицию 2

**Внешние ключи**:
- `fighter1_id` → `fighters(id)`
- `fighter2_id` → `fighters(id)`

**Индексы**:
- `idx_fights_event_name` - по названию события
- `idx_fights_fighter1` - по первому бойцу
- `idx_fights_fighter2` - по второму бойцу
- `idx_fights_date` - по дате боя
- `idx_fights_weight_class` - по весовой категории

---

## 📋 ТАБЛИЦА: rankings

**Назначение**: Хранение рейтингов бойцов UFC  
**Колонок**: 8  
**Записей**: 176  
**Первичный ключ**: `id`

| № | Колонка | Тип | NULL | По умолчанию | Описание |
|---|---------|-----|------|--------------|----------|
| 1 | id | INTEGER | NO | - | Уникальный идентификатор рейтинга (PRIMARY KEY) |
| 2 | fighter_id | INTEGER | NO | - | ID бойца (FOREIGN KEY → fighters.id) |
| 3 | weight_class | TEXT | NO | - | Весовая категория (связана с weight_classes.name_en) |
| 4 | rank_position | INTEGER | YES | - | Позиция в рейтинге |
| 5 | is_champion | BOOLEAN | YES | 0 | Является ли чемпионом |
| 6 | rank_change | INTEGER | YES | 0 | Изменение позиции |
| 7 | created_at | DATETIME | YES | CURRENT_TIMESTAMP | Дата создания записи |
| 8 | updated_at | DATETIME | YES | CURRENT_TIMESTAMP | Дата обновления записи |

**✅ ИСПРАВЛЕНИЯ:**
- ❌ Удален `weight_class_id` (заменен на `weight_class`)

**Внешние ключи**:
- `fighter_id` → `fighters(id)`

**Индексы**:
- `idx_rankings_fighter` - по бойцу
- `idx_rankings_weight_class` - по весовой категории
- `idx_rankings_position` - по позиции

---

## 📋 ТАБЛИЦА: weight_classes

**Назначение**: Хранение весовых категорий UFC  
**Колонок**: 10  
**Записей**: 11  
**Первичный ключ**: `id`

| № | Колонка | Тип | NULL | По умолчанию | Описание |
|---|---------|-----|------|--------------|----------|
| 1 | id | INTEGER | NO | - | Уникальный идентификатор категории (PRIMARY KEY) |
| 2 | name_ru | TEXT | NO | - | Название на русском языке |
| 3 | name_en | TEXT | NO | - | Название на английском языке |
| 4 | weight_min | INTEGER | YES | - | Минимальный вес в кг |
| 5 | weight_max | INTEGER | YES | - | Максимальный вес в кг |
| 6 | weight_limit | REAL | YES | - | Лимит веса в фунтах |
| 7 | gender | TEXT | YES | male | Пол (male/female) |
| 8 | is_p4p | BOOLEAN | YES | 0 | Pound-for-pound рейтинг |
| 9 | created_at | DATETIME | YES | CURRENT_TIMESTAMP | Дата создания записи |
| 10 | updated_at | DATETIME | YES | CURRENT_TIMESTAMP | Дата обновления записи |

---

## 📋 ТАБЛИЦА: fight_records

**Назначение**: Хранение детальных рекордов бойцов  
**Колонок**: 20  
**Записей**: 0  
**Первичный ключ**: `id`

| № | Колонка | Тип | NULL | По умолчанию | Описание |
|---|---------|-----|------|--------------|----------|
| 1 | id | INTEGER | NO | - | Уникальный идентификатор записи (PRIMARY KEY) |
| 2 | fighter_id | INTEGER | NO | - | ID бойца (FOREIGN KEY → fighters.id) |
| 3 | wins | INTEGER | YES | 0 | Общие победы |
| 4 | losses | INTEGER | YES | 0 | Общие поражения |
| 5 | draws | INTEGER | YES | 0 | Общие ничьи |
| 6 | no_contests | INTEGER | YES | 0 | Общие NC |
| 7 | wins_by_ko | INTEGER | YES | 0 | Победы нокаутом |
| 8 | losses_by_ko | INTEGER | YES | 0 | Поражения нокаутом |
| 9 | wins_by_submission | INTEGER | YES | 0 | Победы сабмишном |
| 10 | losses_by_submission | INTEGER | YES | 0 | Поражения сабмишном |
| 11 | wins_by_decision | INTEGER | YES | 0 | Победы решением судей |
| 12 | losses_by_decision | INTEGER | YES | 0 | Поражения решением судей |
| 13 | wins_by_dq | INTEGER | YES | 0 | Победы дисквалификацией |
| 14 | losses_by_dq | INTEGER | YES | 0 | Поражения дисквалификацией |
| 15 | avg_fight_time_seconds | REAL | YES | 0 | Среднее время боя в секундах |
| 16 | total_fights | INTEGER | YES | 0 | Общее количество боев |
| 17 | total_nc | INTEGER | YES | 0 | Общее количество NC |
| 18 | created_at | DATETIME | YES | CURRENT_TIMESTAMP | Дата создания записи |
| 19 | updated_at | DATETIME | YES | CURRENT_TIMESTAMP | Дата обновления записи |
| 20 | weight_class | TEXT | YES | - | **НОВАЯ** - Весовая категория |

**✅ ИСПРАВЛЕНИЯ:**
- ✅ Добавлена колонка `weight_class`

---

## 📋 ТАБЛИЦА: fight_stats

**Назначение**: Хранение детальной статистики боев  
**Колонок**: 34  
**Записей**: 0  
**Первичный ключ**: `id`

| № | Колонка | Тип | NULL | По умолчанию | Описание |
|---|---------|-----|------|--------------|----------|
| 1 | id | INTEGER | NO | - | Уникальный идентификатор записи (PRIMARY KEY) |
| 2 | fight_id | INTEGER | NO | - | ID боя (FOREIGN KEY → fights.id) |
| 3 | fighter_id | INTEGER | NO | - | ID бойца (FOREIGN KEY → fighters.id) |
| 4 | round_number | INTEGER | NO | - | Номер раунда |
| 5 | knockdowns | INTEGER | YES | 0 | Нокдауны |
| 6 | significant_strikes_landed | INTEGER | YES | 0 | Значимые удары попавшие |
| 7 | significant_strikes_attempted | INTEGER | YES | 0 | Значимые удары попытки |
| 8 | significant_strikes_rate | REAL | YES | 0.0 | Процент попаданий значимых ударов |
| 9 | total_strikes_landed | INTEGER | YES | 0 | Всего ударов попавших |
| 10 | total_strikes_attempted | INTEGER | YES | 0 | Всего ударов попыток |
| 11 | takedown_successful | INTEGER | YES | 0 | Успешные тейкдауны |
| 12 | takedown_attempted | INTEGER | YES | 0 | Попытки тейкдаунов |
| 13 | takedown_rate | REAL | YES | 0.0 | Процент успешных тейкдаунов |
| 14 | submission_attempt | INTEGER | YES | 0 | Попытки сабмишнов |
| 15 | reversals | INTEGER | YES | 0 | Реверсы |
| 16 | head_landed | INTEGER | YES | 0 | Удары в голову попавшие |
| 17 | head_attempted | INTEGER | YES | 0 | Удары в голову попытки |
| 18 | body_landed | INTEGER | YES | 0 | Удары по корпусу попавшие |
| 19 | body_attempted | INTEGER | YES | 0 | Удары по корпусу попытки |
| 20 | leg_landed | INTEGER | YES | 0 | Удары по ногам попавшие |
| 21 | leg_attempted | INTEGER | YES | 0 | Удары по ногам попытки |
| 22 | distance_landed | INTEGER | YES | 0 | Удары на дистанции попавшие |
| 23 | distance_attempted | INTEGER | YES | 0 | Удары на дистанции попытки |
| 24 | clinch_landed | INTEGER | YES | 0 | Удары в клинче попавшие |
| 25 | clinch_attempted | INTEGER | YES | 0 | Удары в клинче попытки |
| 26 | ground_landed | INTEGER | YES | 0 | Удары в партере попавшие |
| 27 | ground_attempted | INTEGER | YES | 0 | Удары в партере попытки |
| 28 | result | TEXT | YES | - | Результат раунда |
| 29 | last_round | BOOLEAN | YES | 0 | Последний раунд |
| 30 | time | TEXT | YES | - | Время раунда |
| 31 | winner | TEXT | YES | - | Победитель раунда |
| 32 | created_at | DATETIME | YES | CURRENT_TIMESTAMP | Дата создания записи |
| 33 | updated_at | DATETIME | YES | CURRENT_TIMESTAMP | Дата обновления записи |
| 34 | weight_class | TEXT | YES | - | **НОВАЯ** - Весовая категория |

**✅ ИСПРАВЛЕНИЯ:**
- ✅ Добавлена колонка `weight_class`

---

## 📋 ТАБЛИЦА: upcoming_fights

**Назначение**: Хранение предстоящих боев  
**Колонок**: 11  
**Записей**: 0  
**Первичный ключ**: `id`

| № | Колонка | Тип | NULL | По умолчанию | Описание |
|---|---------|-----|------|--------------|----------|
| 1 | id | INTEGER | NO | - | Уникальный идентификатор записи (PRIMARY KEY) |
| 2 | fighter1_id | INTEGER | NO | - | ID первого бойца (FOREIGN KEY → fighters.id) |
| 3 | fighter2_id | INTEGER | NO | - | ID второго бойца (FOREIGN KEY → fighters.id) |
| 4 | weight_class | TEXT | NO | - | Весовая категория (связана с weight_classes.name_en) |
| 5 | event_name | TEXT | YES | - | Название события |
| 6 | event_date | DATE | YES | - | Дата события |
| 7 | location | TEXT | YES | - | Место проведения |
| 8 | is_main_event | BOOLEAN | YES | 0 | Главное событие |
| 9 | is_title_fight | BOOLEAN | YES | 0 | Титульный бой |
| 10 | created_at | DATETIME | YES | CURRENT_TIMESTAMP | Дата создания записи |
| 11 | updated_at | DATETIME | YES | CURRENT_TIMESTAMP | Дата обновления записи |

**✅ ИСПРАВЛЕНИЯ:**
- ❌ Удален `weight_class_id` (заменен на `weight_class`)

**Внешние ключи**:
- `fighter1_id` → `fighters(id)`
- `fighter2_id` → `fighters(id)`

---

## 🚨 УДАЛЕННЫЕ ТАБЛИЦЫ

### ❌ **fighter_fights** - УДАЛЕНА
**Причина**: Лишняя таблица по требованию пользователя

---

## ✅ ИТОГОВЫЕ ИСПРАВЛЕНИЯ

### **Таблица fights:**
- ❌ Удален `event_id` → заменен на `event_name`
- ❌ Удален `weight_class_id` → заменен на `weight_class`
- ❌ Удален `result` (лишняя колонка)
- ❌ Удален `winner_id` → заменен на `winner_name`
- ❌ Удален `opponent_name` → заменен на `fighter2_name`
- ✅ Добавлены `fighter1_name`, `fighter2_name`, `winner_name`
- ✅ `event_name` перемещен на позицию 2

### **Таблица rankings:**
- ❌ Удален `weight_class_id` → заменен на `weight_class`

### **Таблица upcoming_fights:**
- ❌ Удален `weight_class_id` → заменен на `weight_class`

### **Таблица fighters:**
- ❌ Удалена колонка `full_name` (лишняя)

### **Таблицы fight_records и fight_stats:**
- ✅ Добавлена колонка `weight_class`

### **Удаленные таблицы:**
- ❌ `fighter_fights` (лишняя таблица)

---

## 📊 СТАТИСТИКА ИСПРАВЛЕНИЙ

- **Всего таблиц**: 8 (было 9)
- **Удалено таблиц**: 1 (`fighter_fights`)
- **Изменено таблиц**: 5 (`fights`, `rankings`, `upcoming_fights`, `fight_records`, `fight_stats`)
- **Удалено колонок**: 6
- **Добавлено колонок**: 4
- **Переименовано колонок**: 3

---

## 🎯 РЕЗУЛЬТАТ

База данных теперь полностью соответствует требованиям пользователя:

1. ✅ **Удалены лишние колонки** (`full_name`, `result`, `winner_id`, `opponent_name`)
2. ✅ **Заменены ID на текстовые поля** (`weight_class_id` → `weight_class`)
3. ✅ **Добавлены имена бойцов** (`fighter1_name`, `fighter2_name`, `winner_name`)
4. ✅ **Упрощена структура** (удален `event_id`, добавлен `event_name`)
5. ✅ **Удалена лишняя таблица** (`fighter_fights`)

**Структура готова для работы парсеров!** 🚀
