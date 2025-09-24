#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление структуры базы данных согласно требованиям пользователя
"""

import sqlite3
import sys
from datetime import datetime

def create_backup():
    """Создает резервную копию базы данных"""
    backup_name = f"ufc_ranker_v2_backup_before_final_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    try:
        import shutil
        shutil.copy2("ufc_ranker_v2.db", backup_name)
        print(f"✅ Создана резервная копия: {backup_name}")
        return backup_name
    except Exception as e:
        print(f"❌ Ошибка создания резервной копии: {e}")
        return None

def fix_database_structure():
    """Исправляет структуру базы данных"""
    
    print("🔧 ИСПРАВЛЕНИЕ СТРУКТУРЫ БАЗЫ ДАННЫХ")
    print("=" * 60)
    
    # Создаем резервную копию
    backup_name = create_backup()
    if not backup_name:
        return False
    
    try:
        conn = sqlite3.connect("ufc_ranker_v2.db")
        cursor = conn.cursor()
        
        print("\n1️⃣ Удаляем лишнюю таблицу fighter_fights...")
        cursor.execute("DROP TABLE IF EXISTS fighter_fights")
        print("   ✅ Таблица fighter_fights удалена")
        
        print("\n2️⃣ Удаляем лишнюю колонку full_name из fighters...")
        cursor.execute("ALTER TABLE fighters DROP COLUMN full_name")
        print("   ✅ Колонка full_name удалена из fighters")
        
        print("\n3️⃣ Обновляем таблицу fights...")
        
        # Сначала создаем новую таблицу fights с правильной структурой
        cursor.execute("""
            CREATE TABLE fights_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_name TEXT,
                fighter1_id INTEGER NOT NULL,
                fighter2_id INTEGER NOT NULL,
                weight_class TEXT,
                scheduled_rounds INTEGER DEFAULT 3,
                method TEXT,
                method_details TEXT,
                round INTEGER,
                time TEXT,
                fight_date DATE,
                location TEXT,
                notes TEXT,
                is_title_fight BOOLEAN DEFAULT 0,
                is_main_event BOOLEAN DEFAULT 0,
                fighter1_name TEXT,
                fighter2_name TEXT,
                winner_name TEXT,
                fighter1_record TEXT,
                fighter2_record TEXT,
                fight_time_seconds INTEGER,
                card_type TEXT,
                referee TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (fighter1_id) REFERENCES fighters(id),
                FOREIGN KEY (fighter2_id) REFERENCES fighters(id)
            )
        """)
        
        # Копируем данные из старой таблицы (если есть)
        cursor.execute("SELECT COUNT(*) FROM fights")
        old_count = cursor.fetchone()[0]
        
        if old_count > 0:
            print(f"   📊 Копируем {old_count} записей из старой таблицы...")
            cursor.execute("""
                INSERT INTO fights_new (
                    id, event_name, fighter1_id, fighter2_id, weight_class,
                    scheduled_rounds, method, method_details, round, time,
                    fight_date, location, notes, is_title_fight, is_main_event,
                    fighter1_record, fighter2_record, fight_time_seconds,
                    card_type, referee, created_at, updated_at
                )
                SELECT 
                    id, event_name, fighter1_id, fighter2_id, weight_class,
                    scheduled_rounds, method, method_details, round, time,
                    fight_date, location, notes, is_title_fight, is_main_event,
                    fighter1_record, fighter2_record, fight_time_seconds,
                    card_type, referee, created_at, updated_at
                FROM fights
            """)
        
        # Удаляем старую таблицу и переименовываем новую
        cursor.execute("DROP TABLE fights")
        cursor.execute("ALTER TABLE fights_new RENAME TO fights")
        
        # Создаем индексы для новой таблицы
        cursor.execute("CREATE INDEX idx_fights_event_name ON fights(event_name)")
        cursor.execute("CREATE INDEX idx_fights_fighter1 ON fights(fighter1_id)")
        cursor.execute("CREATE INDEX idx_fights_fighter2 ON fights(fighter2_id)")
        cursor.execute("CREATE INDEX idx_fights_date ON fights(fight_date)")
        cursor.execute("CREATE INDEX idx_fights_weight_class ON fights(weight_class)")
        
        print("   ✅ Таблица fights обновлена")
        
        print("\n4️⃣ Обновляем таблицу rankings...")
        
        # Создаем новую таблицу rankings с weight_class вместо weight_class_id
        cursor.execute("""
            CREATE TABLE rankings_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fighter_id INTEGER NOT NULL,
                weight_class TEXT NOT NULL,
                rank_position INTEGER,
                is_champion BOOLEAN DEFAULT 0,
                rank_change INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (fighter_id) REFERENCES fighters(id)
            )
        """)
        
        # Копируем данные с заменой weight_class_id на weight_class
        cursor.execute("""
            INSERT INTO rankings_new (
                id, fighter_id, weight_class, rank_position, is_champion, 
                rank_change, created_at, updated_at
            )
            SELECT 
                r.id, r.fighter_id, wc.name_en, r.rank_position, r.is_champion,
                r.rank_change, r.created_at, r.updated_at
            FROM rankings r
            JOIN weight_classes wc ON r.weight_class_id = wc.id
        """)
        
        # Удаляем старую таблицу и переименовываем новую
        cursor.execute("DROP TABLE rankings")
        cursor.execute("ALTER TABLE rankings_new RENAME TO rankings")
        
        # Создаем индексы для новой таблицы
        cursor.execute("CREATE INDEX idx_rankings_fighter ON rankings(fighter_id)")
        cursor.execute("CREATE INDEX idx_rankings_weight_class ON rankings(weight_class)")
        cursor.execute("CREATE INDEX idx_rankings_position ON rankings(rank_position)")
        
        print("   ✅ Таблица rankings обновлена")
        
        print("\n5️⃣ Обновляем таблицу upcoming_fights...")
        
        # Создаем новую таблицу upcoming_fights с weight_class вместо weight_class_id
        cursor.execute("""
            CREATE TABLE upcoming_fights_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fighter1_id INTEGER NOT NULL,
                fighter2_id INTEGER NOT NULL,
                weight_class TEXT NOT NULL,
                event_name TEXT,
                event_date DATE,
                location TEXT,
                is_main_event BOOLEAN DEFAULT 0,
                is_title_fight BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (fighter1_id) REFERENCES fighters(id),
                FOREIGN KEY (fighter2_id) REFERENCES fighters(id)
            )
        """)
        
        # Копируем данные с заменой weight_class_id на weight_class
        cursor.execute("""
            INSERT INTO upcoming_fights_new (
                id, fighter1_id, fighter2_id, weight_class, event_name,
                event_date, location, is_main_event, is_title_fight,
                created_at, updated_at
            )
            SELECT 
                uf.id, uf.fighter1_id, uf.fighter2_id, wc.name_en, uf.event_name,
                uf.event_date, uf.location, uf.is_main_event, uf.is_title_fight,
                uf.created_at, uf.updated_at
            FROM upcoming_fights uf
            JOIN weight_classes wc ON uf.weight_class_id = wc.id
        """)
        
        # Удаляем старую таблицу и переименовываем новую
        cursor.execute("DROP TABLE upcoming_fights")
        cursor.execute("ALTER TABLE upcoming_fights_new RENAME TO upcoming_fights")
        
        print("   ✅ Таблица upcoming_fights обновлена")
        
        print("\n6️⃣ Обновляем таблицу fight_records...")
        
        # Добавляем связь с weight_class если нужно
        cursor.execute("PRAGMA table_info(fight_records)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'weight_class' not in columns:
            cursor.execute("ALTER TABLE fight_records ADD COLUMN weight_class TEXT")
            print("   ✅ Добавлена колонка weight_class в fight_records")
        
        print("\n7️⃣ Обновляем таблицу fight_stats...")
        
        # Добавляем связь с weight_class если нужно
        cursor.execute("PRAGMA table_info(fight_stats)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'weight_class' not in columns:
            cursor.execute("ALTER TABLE fight_stats ADD COLUMN weight_class TEXT")
            print("   ✅ Добавлена колонка weight_class в fight_stats")
        
        # Сохраняем изменения
        conn.commit()
        conn.close()
        
        print("\n✅ СТРУКТУРА БАЗЫ ДАННЫХ УСПЕШНО ИСПРАВЛЕНА!")
        print(f"💾 Резервная копия: {backup_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при исправлении структуры: {e}")
        return False

def verify_structure():
    """Проверяет исправленную структуру"""
    
    print("\n🔍 ПРОВЕРКА ИСПРАВЛЕННОЙ СТРУКТУРЫ")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect("ufc_ranker_v2.db")
        cursor = conn.cursor()
        
        # Проверяем таблицы
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        
        tables = cursor.fetchall()
        print(f"📊 Найдено таблиц: {len(tables)}")
        
        for table_name, in tables:
            print(f"\n📋 {table_name}:")
            
            # Получаем информацию о колонках
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            for col in columns:
                col_id, name, data_type, not_null, default_val, pk = col
                pk_mark = " 🔑" if pk else ""
                print(f"   • {name} ({data_type}){pk_mark}")
            
            # Получаем количество записей
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   📊 Записей: {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка при проверке структуры: {e}")

if __name__ == "__main__":
    if fix_database_structure():
        verify_structure()
    else:
        print("❌ Исправление структуры не удалось")
        sys.exit(1)
