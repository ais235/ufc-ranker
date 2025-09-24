# Основные парсеры Wikipedia для UFC Ranker

## 📋 Список основных парсеров

### 1. **parse_ufc_rankings_correct.py** ✅
- **Источник**: https://en.wikipedia.org/wiki/UFC_rankings
- **Назначение**: Парсинг официальных рейтингов UFC
- **Таблицы**: `rankings`, `fighters`, `weight_classes`
- **Статус**: Работает

### 2. **parse_past_events.py** ✅
- **Источник**: https://en.wikipedia.org/wiki/List_of_UFC_events
- **Назначение**: Парсинг прошедших событий UFC
- **Таблицы**: `events`
- **Статус**: Работает

### 3. **parse_scheduled_events.py** ✅
- **Источник**: https://en.wikipedia.org/wiki/List_of_UFC_events
- **Назначение**: Парсинг запланированных событий UFC
- **Таблицы**: `events`
- **Статус**: Работает

### 4. **parse_fighter_detailed_stats.py** ✅
- **Источник**: Индивидуальные страницы бойцов на Wikipedia
- **Назначение**: Парсинг детальной статистики бойцов
- **Таблицы**: `fight_records`, `fighters`
- **Статус**: Готов к работе

### 5. **parse_fighter_fights.py** ✅
- **Источник**: Индивидуальные страницы бойцов на Wikipedia
- **Назначение**: Парсинг детальной информации о боях бойцов
- **Таблицы**: `fights` (через обновленную схему)
- **Статус**: Готов к работе

---

## 🚫 Исключенные парсеры

### Неосновные парсеры (не Wikipedia):
- `parse_event_details.py` - парсит другие источники
- `updated_*.py` - обновленные версии (дублируют основные)
- `fighter_fights_parser.py` - старая версия
- `fix_rankings_from_official_ufc.py` - исправления

### Удаленные таблицы:
- `fighter_fights` - не нужна (данные идут в `fights`)
- `event_fights` - не нужна (данные идут в `fights`)

---

## 🔧 Исправления схемы

### 1. **Удалены ненужные таблицы**:
- `fighter_fights` ❌
- `event_fights` ❌

### 2. **Исправлены колонки весовых категорий**:
- Удалена `full_name` ❌
- Оставлены `name_ru` и `name_en` ✅

### 3. **Обновлен парсер рейтингов**:
- Изменен запрос с `full_name` на `name_en`
- Теперь корректно находит весовые категории

---

## 📊 Финальная схема БД

### **Таблицы** (7 штук):
1. `weight_classes` - весовые категории
2. `fighters` - бойцы
3. `rankings` - рейтинги
4. `fight_records` - боевые рекорды
5. `events` - события UFC
6. `fights` - бои UFC
7. `upcoming_fights` - предстоящие бои
8. `fight_stats` - детальная статистика боев

### **Ключевые колонки**:

#### В `weight_classes`:
- `name_ru` (TEXT) - русское название
- `name_en` (TEXT) - английское название

#### В `fighters`:
- `name` (TEXT) - основное имя
- `name_ru` (TEXT) - русское имя
- `name_en` (TEXT) - английское имя

---

## 🚀 Порядок запуска парсеров

1. **События** (уже заполнено):
   ```bash
   python parse_past_events.py
   python parse_scheduled_events.py
   ```

2. **Бойцы** (следующий шаг):
   ```bash
   python parse_fighter_detailed_stats.py
   ```

3. **Рейтинги** (после заполнения бойцов):
   ```bash
   python parse_ufc_rankings_correct.py
   ```

4. **Бои** (после заполнения бойцов):
   ```bash
   python parse_fighter_fights.py
   ```

---

## ✅ Готовность

**Все основные парсеры Wikipedia готовы к работе с обновленной схемой БД!**

- ✅ Схема БД оптимизирована
- ✅ Удалены ненужные таблицы
- ✅ Исправлены колонки весовых категорий
- ✅ Парсеры событий работают
- ✅ Остальные парсеры готовы к запуску
