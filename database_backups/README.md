# Система резервного копирования базы данных UFC Ranker

## 📁 Структура папки

```
database_backups/
├── README.md                           # Этот файл
├── backup_database.py                  # Скрипт для создания бэкапов
├── restore_database.py                 # Скрипт для восстановления БД
├── docs/
│   └── DATABASE_OPERATION_GUIDE.md    # Руководство по эксплуатации
└── schema/
    ├── database_schema.sql            # Базовая схема (устаревшая)
    └── current_database_schema.sql    # Актуальная схема (соответствует models.py)
```

## 🚀 Быстрый старт

### Создание резервной копии:
```bash
python database_backups/backup_database.py
```

### Просмотр доступных копий:
```bash
python database_backups/backup_database.py list
```

### Восстановление из копии:
```bash
python database_backups/backup_database.py restore ufc_ranker_v2_backup_YYYYMMDD_HHMMSS.db
```

### Полное пересоздание БД:
```bash
python database_backups/restore_database.py
```

## 📋 Основные команды

| Команда | Описание |
|---------|----------|
| `backup` | Создать резервную копию |
| `list` | Показать список копий |
| `restore <filename>` | Восстановить из копии |

## 🔧 Автоматизация

### Ежедневный бэкап (cron):
```bash
# Добавить в crontab
0 2 * * * cd /path/to/ufc-ranker && python database_backups/backup_database.py
```

### Бэкап перед обновлением:
```bash
# Создать бэкап
python database_backups/backup_database.py

# Запустить парсеры
python parsers/main.py

# Создать финальный бэкап
python database_backups/backup_database.py
```

## ⚠️ Важные правила

1. **НИКОГДА не удаляйте файлы .db без создания резервной копии**
2. **Всегда делайте бэкап перед обновлением данных**
3. **Проверяйте целостность данных после восстановления**
4. **Храните резервные копии в папке database_backups/**
5. **Автоматически удаляются старые копии (остаются только последние 5)**

## 📊 Мониторинг

### Проверка размера БД:
```bash
ls -lh ufc_ranker_v2.db
```

### Проверка количества записей:
```bash
sqlite3 ufc_ranker_v2.db "SELECT COUNT(*) FROM fighters;"
sqlite3 ufc_ranker_v2.db "SELECT COUNT(*) FROM fights;"
sqlite3 ufc_ranker_v2.db "SELECT COUNT(*) FROM events;"
```

### Проверка целостности:
```bash
sqlite3 ufc_ranker_v2.db "PRAGMA integrity_check;"
```

## 🆘 Восстановление после сбоя

### Если БД повреждена:
1. Найдите последнюю рабочую копию: `python database_backups/backup_database.py list`
2. Восстановите: `python database_backups/backup_database.py restore <filename>`
3. Проверьте целостность: `sqlite3 ufc_ranker_v2.db "PRAGMA integrity_check;"`

### Если БД полностью потеряна:
1. Пересоздайте: `python database_backups/restore_database.py`
2. Запустите парсеры для заполнения данными
3. Создайте резервную копию: `python database_backups/backup_database.py`

## 📈 Статистика

- **Размер БД**: обычно 10-50 MB
- **Количество записей в fighters**: ~1000+
- **Количество записей в fights**: ~5000+
- **Количество записей в events**: ~500+
- **Количество резервных копий**: до 5 (автоматическая очистка)

## 🔗 Связанные файлы

- `ufc_ranker_v2.db` - основная база данных
- `database/models.py` - SQLAlchemy модели
- `database_backups/schema/current_database_schema.sql` - актуальная схема
- `FIGHTS_TABLE_COLUMNS_DESCRIPTION.md` - описание таблицы fights
