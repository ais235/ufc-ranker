#!/usr/bin/env python3
"""
Скрипт для связывания таблиц fights и events через event_name
Обновляет сокращенные названия событий в fights на полные названия из events
"""

import sqlite3
import re
from datetime import datetime

def link_fights_to_events():
    """Связывает бои с событиями, обновляя event_name в таблице fights"""
    
    print("🔗 СВЯЗЫВАНИЕ БОЕВ С СОБЫТИЯМИ")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect("ufc_ranker_v2.db")
        cursor = conn.cursor()
        
        # Получаем все уникальные сокращенные названия номерных UFC событий из fights
        cursor.execute("""
            SELECT DISTINCT event_name 
            FROM fights 
            WHERE event_name LIKE 'UFC %' 
            AND event_name NOT LIKE '%:%'
            AND event_name NOT LIKE 'UFC Fight Night%'
            AND event_name NOT LIKE 'UFC on %'
            ORDER BY event_name
        """)
        
        short_events = cursor.fetchall()
        print(f"📋 Найдено {len(short_events)} сокращенных названий событий")
        
        updated_count = 0
        not_found_count = 0
        
        for (short_name,) in short_events:
            print(f"\n🔍 Ищем полное название для: {short_name}")
            
            # Ищем соответствующее полное название в events
            # Сначала ищем точное совпадение с номером события
            event_number = re.search(r'UFC\s+(\d+)', short_name)
            if event_number:
                ufc_num = event_number.group(1)
                
                # Ищем событие с таким номером
                cursor.execute("""
                    SELECT name FROM events 
                    WHERE name LIKE ? 
                    ORDER BY name
                """, (f"UFC {ufc_num}%",))
                
                full_events = cursor.fetchall()
                
                if full_events:
                    # Берем первое найденное событие
                    full_name = full_events[0][0]
                    print(f"   ✅ Найдено: {full_name}")
                    
                    # Обновляем все бои с этим сокращенным названием
                    cursor.execute("""
                        UPDATE fights 
                        SET event_name = ? 
                        WHERE event_name = ?
                    """, (full_name, short_name))
                    
                    affected_rows = cursor.rowcount
                    updated_count += affected_rows
                    print(f"   📝 Обновлено боев: {affected_rows}")
                    
                else:
                    print(f"   ❌ Полное название не найдено")
                    not_found_count += 1
            else:
                print(f"   ⚠️ Не удалось извлечь номер события")
                not_found_count += 1
        
        # Сохраняем изменения
        conn.commit()
        
        print(f"\n✅ СВЯЗЫВАНИЕ ЗАВЕРШЕНО!")
        print(f"📊 Статистика:")
        print(f"   • Обновлено боев: {updated_count}")
        print(f"   • Событий без полного названия: {not_found_count}")
        
        # Показываем примеры обновленных связей
        print(f"\n📋 Примеры обновленных связей:")
        cursor.execute("""
            SELECT DISTINCT event_name, COUNT(*) as fight_count
            FROM fights 
            WHERE event_name LIKE 'UFC%:%'
            GROUP BY event_name
            ORDER BY fight_count DESC
            LIMIT 5
        """)
        
        examples = cursor.fetchall()
        for event_name, count in examples:
            print(f"   • {event_name}: {count} боев")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    link_fights_to_events()
