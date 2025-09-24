#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Дополнительное исправление таблицы fights согласно требованиям пользователя
"""

import sqlite3
import sys
from datetime import datetime

def create_backup():
    """Создает резервную копию базы данных"""
    backup_name = f"ufc_ranker_v2_backup_before_fights_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    try:
        import shutil
        shutil.copy2("ufc_ranker_v2.db", backup_name)
        print(f"✅ Создана резервная копия: {backup_name}")
        return backup_name
    except Exception as e:
        print(f"❌ Ошибка создания резервной копии: {e}")
        return None

def fix_fights_table():
    """Исправляет таблицу fights согласно новым требованиям"""
    
    print("🔧 ДОПОЛНИТЕЛЬНОЕ ИСПРАВЛЕНИЕ ТАБЛИЦЫ FIGHTS")
    print("=" * 60)
    
    # Создаем резервную копию
    backup_name = create_backup()
    if not backup_name:
        return False
    
    try:
        conn = sqlite3.connect("ufc_ranker_v2.db")
        cursor = conn.cursor()
        
        print("\n1️⃣ Создаем новую таблицу fights с исправленной структурой...")
        
        # Создаем новую таблицу fights с правильной структурой
        cursor.execute("""
            CREATE TABLE fights_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_name TEXT,
                fighter1_name TEXT,
                fighter2_name TEXT,
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
                is_win TEXT,
                is_loss TEXT,
                is_draw TEXT,
                is_nc TEXT,
                fighter1_record TEXT,
                fighter2_record TEXT,
                fight_time_seconds INTEGER,
                card_type TEXT,
                referee TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        print("   ✅ Новая таблица fights создана")
        
        print("\n2️⃣ Копируем данные из старой таблицы...")
        
        # Копируем данные из старой таблицы (если есть)
        cursor.execute("SELECT COUNT(*) FROM fights")
        old_count = cursor.fetchone()[0]
        
        if old_count > 0:
            print(f"   📊 Копируем {old_count} записей из старой таблицы...")
            
            # Получаем данные из старой таблицы
            cursor.execute("""
                SELECT 
                    id, event_name, fighter1_id, fighter2_id, weight_class,
                    scheduled_rounds, method, method_details, round, time,
                    fight_date, location, notes, is_title_fight, is_main_event,
                    fighter1_record, fighter2_record, fight_time_seconds,
                    card_type, referee, created_at, updated_at
                FROM fights
            """)
            
            old_data = cursor.fetchall()
            
            # Копируем данные в новую таблицу
            for row in old_data:
                (id_val, event_name, fighter1_id, fighter2_id, weight_class,
                 scheduled_rounds, method, method_details, round, time,
                 fight_date, location, notes, is_title_fight, is_main_event,
                 fighter1_record, fighter2_record, fight_time_seconds,
                 card_type, referee, created_at, updated_at) = row
                
                # Получаем имена бойцов по ID
                fighter1_name = None
                fighter2_name = None
                
                if fighter1_id:
                    cursor.execute("SELECT name_en FROM fighters WHERE id = ?", (fighter1_id,))
                    result = cursor.fetchone()
                    if result:
                        fighter1_name = result[0]
                
                if fighter2_id:
                    cursor.execute("SELECT name_en FROM fighters WHERE id = ?", (fighter2_id,))
                    result = cursor.fetchone()
                    if result:
                        fighter2_name = result[0]
                
                # Определяем значения для is_win, is_loss, is_draw, is_nc
                is_win = None
                is_loss = None
                is_draw = None
                is_nc = None
                
                # Логика определения результата (нужно будет адаптировать под реальные данные)
                if method:
                    if method.lower() in ['ko', 'tko', 'submission', 'decision']:
                        # Предполагаем, что fighter1 выиграл, если есть метод победы
                        is_win = fighter1_name
                    elif method.lower() == 'draw':
                        is_draw = "Ничья"
                    elif method.lower() in ['nc', 'no contest']:
                        is_nc = "No Contest"
                    else:
                        # Если не можем определить, оставляем пустым
                        pass
                
                cursor.execute("""
                    INSERT INTO fights_new (
                        id, event_name, fighter1_name, fighter2_name, weight_class,
                        scheduled_rounds, method, method_details, round, time,
                        fight_date, location, notes, is_title_fight, is_main_event,
                        is_win, is_loss, is_draw, is_nc,
                        fighter1_record, fighter2_record, fight_time_seconds,
                        card_type, referee, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    id_val, event_name, fighter1_name, fighter2_name, weight_class,
                    scheduled_rounds, method, method_details, round, time,
                    fight_date, location, notes, is_title_fight, is_main_event,
                    is_win, is_loss, is_draw, is_nc,
                    fighter1_record, fighter2_record, fight_time_seconds,
                    card_type, referee, created_at, updated_at
                ))
            
            print(f"   ✅ Скопировано {old_count} записей")
        else:
            print("   ℹ️ Старая таблица пуста, копирование не требуется")
        
        print("\n3️⃣ Заменяем старую таблицу новой...")
        
        # Удаляем старую таблицу и переименовываем новую
        cursor.execute("DROP TABLE fights")
        cursor.execute("ALTER TABLE fights_new RENAME TO fights")
        
        print("   ✅ Таблица fights заменена")
        
        print("\n4️⃣ Создаем индексы для новой таблицы...")
        
        # Создаем индексы для новой таблицы
        cursor.execute("CREATE INDEX idx_fights_event_name ON fights(event_name)")
        cursor.execute("CREATE INDEX idx_fights_fighter1_name ON fights(fighter1_name)")
        cursor.execute("CREATE INDEX idx_fights_fighter2_name ON fights(fighter2_name)")
        cursor.execute("CREATE INDEX idx_fights_date ON fights(fight_date)")
        cursor.execute("CREATE INDEX idx_fights_weight_class ON fights(weight_class)")
        cursor.execute("CREATE INDEX idx_fights_is_win ON fights(is_win)")
        cursor.execute("CREATE INDEX idx_fights_is_loss ON fights(is_loss)")
        
        print("   ✅ Индексы созданы")
        
        # Сохраняем изменения
        conn.commit()
        conn.close()
        
        print("\n✅ ТАБЛИЦА FIGHTS УСПЕШНО ИСПРАВЛЕНА!")
        print(f"💾 Резервная копия: {backup_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при исправлении таблицы fights: {e}")
        return False

def verify_fights_structure():
    """Проверяет исправленную структуру таблицы fights"""
    
    print("\n🔍 ПРОВЕРКА ИСПРАВЛЕННОЙ СТРУКТУРЫ ТАБЛИЦЫ FIGHTS")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect("ufc_ranker_v2.db")
        cursor = conn.cursor()
        
        # Получаем информацию о колонках
        cursor.execute("PRAGMA table_info(fights)")
        columns = cursor.fetchall()
        
        print(f"📋 Таблица fights - колонок: {len(columns)}")
        print("\nКолонки:")
        for col in columns:
            col_id, name, data_type, not_null, default_val, pk = col
            pk_mark = " 🔑" if pk else ""
            not_null_mark = " NOT NULL" if not_null else ""
            default_mark = f" DEFAULT {default_val}" if default_val else ""
            print(f"   • {name} ({data_type}){not_null_mark}{default_mark}{pk_mark}")
        
        # Получаем количество записей
        cursor.execute("SELECT COUNT(*) FROM fights")
        count = cursor.fetchone()[0]
        print(f"\n📊 Записей: {count}")
        
        # Показываем примеры данных если есть
        if count > 0:
            cursor.execute("SELECT * FROM fights LIMIT 3")
            sample_data = cursor.fetchall()
            print(f"\n📝 Примеры данных:")
            for i, row in enumerate(sample_data, 1):
                print(f"   {i}. {row}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка при проверке структуры: {e}")

if __name__ == "__main__":
    if fix_fights_table():
        verify_fights_structure()
    else:
        print("❌ Исправление таблицы fights не удалось")
        sys.exit(1)
