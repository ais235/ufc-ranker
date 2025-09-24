# Руководство по эксплуатации базы данных UFC Ranker

## Структура базы данных

Основная база данных: `ufc_ranker_v2.db`

### Основные таблицы:

1. **fighters** - информация о бойцах
2. **fights** - информация о боях
3. **events** - информация о событиях UFC
4. **rankings** - рейтинги бойцов по весовым категориям
5. **upcoming_fights** - предстоящие бои

## Резервное копирование

### Автоматическое резервное копирование:
```bash
python database_backups/backup_database.py
```

### Ручное резервное копирование:
```bash
cp ufc_ranker_v2.db database_backups/ufc_ranker_v2_backup_$(date +%Y%m%d_%H%M%S).db
```

## Восстановление базы данных

### Из резервной копии:
```bash
cp database_backups/ufc_ranker_v2_backup_YYYYMMDD_HHMMSS.db ufc_ranker_v2.db
```

### Полное пересоздание:
```bash
python parsers/main.py --full-rebuild
```

## Структура схемы

Схема базы данных сохранена в файле: `database_backups/schema/database_schema.sql`

## Мониторинг

- Размер базы данных: обычно 10-50 MB
- Количество записей в fighters: ~1000+
- Количество записей в fights: ~5000+
- Количество записей в events: ~500+

## Важные правила

1. **НИКОГДА не удаляйте файлы .db без создания резервной копии**
2. **Всегда делайте бэкап перед обновлением данных**
3. **Проверяйте целостность данных после восстановления**
4. **Храните резервные копии в папке database_backups/**

## Команды для проверки состояния БД

```bash
# Проверить размер БД
ls -lh ufc_ranker_v2.db

# Проверить количество записей
sqlite3 ufc_ranker_v2.db "SELECT COUNT(*) FROM fighters;"
sqlite3 ufc_ranker_v2.db "SELECT COUNT(*) FROM fights;"
sqlite3 ufc_ranker_v2.db "SELECT COUNT(*) FROM events;"
```

## Контакты для восстановления

При проблемах с БД обращайтесь к разработчику или используйте автоматическое восстановление.
