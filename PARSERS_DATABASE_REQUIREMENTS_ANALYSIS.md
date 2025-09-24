# Анализ требований парсеров к схеме базы данных

## 📋 Обзор парсеров

| Парсер | Файл | Основные таблицы | Статус |
|--------|------|------------------|--------|
| Рейтинги UFC | `parse_ufc_rankings_correct.py` | `rankings`, `fighters`, `weight_classes` | ✅ Работает |
| Прошедшие события | `parse_past_events.py` | `events` | ❌ Ошибки схемы |
| Запланированные события | `parse_scheduled_events.py` | `events` | ❌ Ошибки схемы |
| Детальная статистика бойцов | `parse_fighter_detailed_stats.py` | `fight_records`, `fighters` | ❌ Ошибки схемы |
| Бои бойцов | `parse_fighter_fights.py` | `fighter_fights` | ❌ Ошибки схемы |
| Детали событий | `parse_event_details.py` | `events`, `event_fights` | ❌ Ошибки схемы |
| Обновленные парсеры | `updated_*.py` | `fights`, `events` | ❌ Ошибки схемы |

---

## 🔍 Детальный анализ по парсерам

### 1. **parse_ufc_rankings_correct.py** ✅
**Таблицы**: `rankings`, `fighters`, `weight_classes`

**Колонки в rankings**:
- `fighter_id` (INTEGER, FK → fighters.id)
- `weight_class_id` (INTEGER, FK → weight_classes.id) 
- `rank_position` (INTEGER)
- `is_champion` (BOOLEAN)
- `created_at`, `updated_at` (DATETIME)

**Колонки в fighters**:
- `name_en` (TEXT) - **ОТСУТСТВУЕТ в текущей схеме!**
- `nickname` (TEXT)
- `wins`, `losses`, `draws`, `nc` (INTEGER)

**Колонки в weight_classes**:
- `name_en` (TEXT) - **ОТСУТСТВУЕТ в текущей схеме!**
- `name_ru` (TEXT)

---

### 2. **parse_past_events.py** ❌
**Таблица**: `events`

**Ожидаемые колонки**:
- `name` (TEXT) ✅
- `event_number` (TEXT) ✅
- `event_type` (TEXT) - **ОТСУТСТВУЕТ!**
- `date` (DATE) ✅
- `venue` (TEXT) ✅
- `venue_url` (TEXT) - **ОТСУТСТВУЕТ!**
- `location` (TEXT) ✅
- `location_url` (TEXT) - **ОТСУТСТВУЕТ!**
- `event_url` (TEXT) ✅
- `reference_url` (TEXT) - **ОТСУТСТВУЕТ!**
- `status` (TEXT) - **ОТСУТСТВУЕТ!**
- `attendance` (INTEGER) ✅

---

### 3. **parse_scheduled_events.py** ❌
**Таблица**: `events`

**Ожидаемые колонки** (аналогично parse_past_events.py):
- Все те же колонки, что и в parse_past_events.py

---

### 4. **parse_fighter_detailed_stats.py** ❌
**Таблицы**: `fight_records`, `fighters`

**Ожидаемые колонки в fight_records**:
- `wins_by_ko` (INTEGER) - **ОТСУТСТВУЕТ!**
- `losses_by_ko` (INTEGER) - **ОТСУТСТВУЕТ!**
- `wins_by_submission` (INTEGER) - **ОТСУТСТВУЕТ!**
- `losses_by_submission` (INTEGER) - **ОТСУТСТВУЕТ!**
- `wins_by_decision` (INTEGER) - **ОТСУТСТВУЕТ!**
- `losses_by_decision` (INTEGER) - **ОТСУТСТВУЕТ!**
- `wins_by_dq` (INTEGER) - **ОТСУТСТВУЕТ!**
- `losses_by_dq` (INTEGER) - **ОТСУТСТВУЕТ!**
- `avg_fight_time_seconds` (REAL) - **ОТСУТСТВУЕТ!**
- `total_fights` (INTEGER) - **ОТСУТСТВУЕТ!**
- `total_nc` (INTEGER) - **ОТСУТСТВУЕТ!**

**Ожидаемые колонки в fighters**:
- `fighting_out_of` (TEXT) - **ОТСУТСТВУЕТ!**
- `years_active` (TEXT) - **ОТСУТСТВУЕТ!**

---

### 5. **parse_fighter_fights.py** ❌
**Таблица**: `fighter_fights`

**Ожидаемые колонки**:
- `fighter_id` (INTEGER, FK → fighters.id) ✅
- `result` (TEXT) - **ОТСУТСТВУЕТ!**
- `record` (TEXT) - **ОТСУТСТВУЕТ!**
- `method` (TEXT) - **ОТСУТСТВУЕТ!**
- `event` (TEXT) - **ОТСУТСТВУЕТ!**
- `fight_date` (DATE) - **ОТСУТСТВУЕТ!**
- `scheduled_rounds` (INTEGER) - **ОТСУТСТВУЕТ!**
- `fight_time_seconds` (INTEGER) - **ОТСУТСТВУЕТ!**
- `location` (TEXT) - **ОТСУТСТВУЕТ!**
- `notes` (TEXT) - **ОТСУТСТВУЕТ!**

---

### 6. **parse_event_details.py** ❌
**Таблицы**: `events`, `event_fights`

**Ожидаемые колонки в events**:
- `gate_revenue` (TEXT) - **ОТСУТСТВУЕТ!**

**Ожидаемые колонки в event_fights**:
- `event_id` (INTEGER, FK → events.id) - **ТАБЛИЦА ОТСУТСТВУЕТ!**
- `fighter1_id` (INTEGER, FK → fighters.id)
- `fighter2_id` (INTEGER, FK → fighters.id)
- `winner_id` (INTEGER, FK → fighters.id)
- `weight_class` (TEXT)
- `method` (TEXT)
- `method_details` (TEXT)
- `round` (INTEGER)
- `time` (TEXT)

---

### 7. **updated_event_details_parser.py** ❌
**Таблица**: `fights`

**Ожидаемые колонки**:
- `event_id` (INTEGER, FK → events.id) ✅
- `fighter1_id` (INTEGER, FK → fighters.id) ✅
- `fighter2_id` (INTEGER, FK → fighters.id) ✅
- `winner_id` (INTEGER, FK → fighters.id) ✅
- `result` (TEXT) - **ОТСУТСТВУЕТ!**
- `method` (TEXT) - **ОТСУТСТВУЕТ!**
- `method_details` (TEXT) - **ОТСУТСТВУЕТ!**
- `round` (INTEGER) - **ОТСУТСТВУЕТ!**
- `time` (TEXT) - **ОТСУТСТВУЕТ!**
- `card_type` (TEXT) - **ОТСУТСТВУЕТ!**
- `notes` (TEXT) - **ОТСУТСТВУЕТ!**

---

### 8. **updated_fighter_fights_parser.py** ❌
**Таблица**: `fights`

**Ожидаемые колонки**:
- `event_id` (INTEGER, FK → events.id) ✅
- `fighter1_id` (INTEGER, FK → fighters.id) ✅
- `fighter2_id` (INTEGER, FK → fighters.id) ✅
- `winner_id` (INTEGER, FK → fighters.id) ✅
- `method` (TEXT) - **ОТСУТСТВУЕТ!**
- `method_details` (TEXT) - **ОТСУТСТВУЕТ!**
- `round` (INTEGER) - **ОТСУТСТВУЕТ!**
- `time` (TEXT) - **ОТСУТСТВУЕТ!**
- `fight_date` (DATE) - **ОТСУТСТВУЕТ!**
- `opponent_name` (TEXT) - **ОТСУТСТВУЕТ!**
- `fighter1_record` (TEXT) - **ОТСУТСТВУЕТ!**
- `fighter2_record` (TEXT) - **ОТСУТСТВУЕТ!**
- `event_name` (TEXT) - **ОТСУТСТВУЕТ!**

---

## 🚨 Критические проблемы

### 1. **Отсутствующие колонки в существующих таблицах**

#### В таблице `fighters`:
- `name_en` (TEXT) - используется парсером рейтингов
- `fighting_out_of` (TEXT) - используется парсером детальной статистики
- `years_active` (TEXT) - используется парсером детальной статистики

#### В таблице `weight_classes`:
- `name_en` (TEXT) - используется парсером рейтингов

#### В таблице `events`:
- `event_type` (TEXT)
- `venue_url` (TEXT)
- `location_url` (TEXT)
- `reference_url` (TEXT)
- `status` (TEXT)
- `gate_revenue` (TEXT)

#### В таблице `fights`:
- `result` (TEXT)
- `method` (TEXT)
- `method_details` (TEXT)
- `round` (INTEGER)
- `time` (TEXT)
- `fight_date` (DATE)
- `opponent_name` (TEXT)
- `fighter1_record` (TEXT)
- `fighter2_record` (TEXT)
- `event_name` (TEXT)
- `card_type` (TEXT)
- `notes` (TEXT)

#### В таблице `fight_records`:
- `wins_by_ko` (INTEGER)
- `losses_by_ko` (INTEGER)
- `wins_by_submission` (INTEGER)
- `losses_by_submission` (INTEGER)
- `wins_by_decision` (INTEGER)
- `losses_by_decision` (INTEGER)
- `wins_by_dq` (INTEGER)
- `losses_by_dq` (INTEGER)
- `avg_fight_time_seconds` (REAL)
- `total_fights` (INTEGER)
- `total_nc` (INTEGER)

### 2. **Отсутствующие таблицы**
- `fighter_fights` - используется парсером боев бойцов
- `event_fights` - используется парсером деталей событий

---

## ✅ Рекомендации

1. **Обновить схему БД** - добавить все отсутствующие колонки
2. **Создать отсутствующие таблицы** - `fighter_fights`, `event_fights`
3. **Унифицировать парсеры** - использовать единую схему
4. **Протестировать все парсеры** - убедиться в совместимости

---

## 📊 Статистика проблем

- **Парсеров с ошибками**: 7 из 8
- **Отсутствующих колонок**: ~30
- **Отсутствующих таблиц**: 2
- **Критических проблем**: 8

**Вывод**: Текущая схема БД несовместима с большинством парсеров и требует серьезного обновления.
