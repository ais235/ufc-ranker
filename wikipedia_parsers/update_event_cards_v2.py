import sqlite3
import requests
from lxml import html
from datetime import datetime
import sys
import codecs
import re

sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def fetch_html(url):
    """Загружает HTML-содержимое страницы по URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return html.fromstring(response.content)
    except Exception as e:
        print(f"❌ Ошибка при загрузке страницы {url}: {e}")
        return None

def parse_event_card(event_url):
    """Парсит страницу события Wikipedia для извлечения информации о картах боев."""
    tree = fetch_html(event_url)
    if not tree:
        return []
    
    print(f"🔍 Парсим карту события: {event_url}")
    
    fights_data = []
    
    # Ищем таблицу с результатами
    results_table = tree.xpath('//h2[contains(text(), "Results")]/following-sibling::table[1]')
    
    if not results_table:
        # Альтернативный поиск - ищем таблицу с заголовками "Main card", "Weight class"
        results_table = tree.xpath('//table[.//th[contains(text(), "Main card")] or .//th[contains(text(), "Weight class")]]')
    
    if not results_table:
        print("❌ Таблица результатов не найдена")
        return []
    
    table = results_table[0]
    rows = table.xpath('.//tr')
    
    current_card_type = None
    fight_order = 0
    
    for row in rows:
        cells = row.xpath('.//td | .//th')
        
        # Проверяем, является ли строка заголовком карты (имеет только одну ячейку)
        if len(cells) == 1:
            first_cell_text = cells[0].text_content().strip().lower()
            if 'main card' in first_cell_text:
                current_card_type = 'Main card'
                fight_order = 0
                print(f"📋 Найдена карта: {current_card_type}")
                continue
            elif 'preliminary card' in first_cell_text:
                current_card_type = 'Preliminary card'
                fight_order = 0
                print(f"📋 Найдена карта: {current_card_type}")
                continue
            elif 'early preliminary card' in first_cell_text:
                current_card_type = 'Early preliminary card'
                fight_order = 0
                print(f"📋 Найдена карта: {current_card_type}")
                continue
        
        # Пропускаем строки с заголовками таблицы или недостаточным количеством ячеек
        if len(cells) < 6:
            continue
        
        # Парсим данные боя
        try:
            weight_class = cells[0].text_content().strip()
            fighter1_name = cells[1].text_content().strip()
            result = cells[2].text_content().strip()
            fighter2_name = cells[3].text_content().strip()
            method = cells[4].text_content().strip()
            round_info = cells[5].text_content().strip()
            time_info = cells[6].text_content().strip() if len(cells) > 6 else ""
            notes = cells[7].text_content().strip() if len(cells) > 7 else ""
            
            # Пропускаем строки с заголовками или пустые строки
            if not weight_class or weight_class in ['Weight class', 'Main card', 'Preliminary card', 'Early preliminary card']:
                continue
            
            # Извлекаем оценку судей из метода
            judges_score = None
            if 'decision' in method.lower():
                # Ищем паттерн оценок судей (например: 49–45, 49–45, 49–46)
                score_match = re.search(r'\(([0-9–-]+(?:,\s*[0-9–-]+)*)\)', method)
                if score_match:
                    judges_score = score_match.group(1)
            
            fight_order += 1
            
            fight_data = {
                'weight_class': weight_class,
                'fighter1_name': fighter1_name,
                'fighter2_name': fighter2_name,
                'method': method,
                'round': round_info,
                'time': time_info,
                'notes': notes,
                'card_type': current_card_type,
                'judges_score': judges_score,
                'fight_order': fight_order,
                'is_title_fight': 'title' in notes.lower() or 'championship' in notes.lower(),
                'is_main_event': fight_order == 1 and current_card_type and 'main card' in current_card_type.lower()
            }
            
            fights_data.append(fight_data)
            print(f"   ✅ Бой #{fight_order}: {fighter1_name} vs {fighter2_name}")
            
        except Exception as e:
            print(f"   ⚠️ Ошибка при парсинге строки: {e}")
            continue
    
    print(f"📊 Всего найдено боев: {len(fights_data)}")
    return fights_data

def update_fights_in_database(event_name, fights_data):
    """Обновляет существующие бои в БД с информацией о картах."""
    conn = None
    updated_count = 0
    try:
        conn = sqlite3.connect("ufc_ranker_v2.db")
        cursor = conn.cursor()
        
        for fight_data in fights_data:
            # Ищем бой по event_name, fighter1_name и fighter2_name
            # Учитываем, что имена бойцов могут быть перепутаны
            cursor.execute("""
                UPDATE fights
                SET card_type = ?, judges_score = ?, fight_order = ?
                WHERE event_name = ? AND (
                    (fighter1_name = ? AND fighter2_name = ?) OR
                    (fighter1_name = ? AND fighter2_name = ?)
                )
            """, (
                fight_data['card_type'],
                fight_data['judges_score'],
                fight_data['fight_order'],
                event_name,
                fight_data['fighter1_name'],
                fight_data['fighter2_name'],
                fight_data['fighter2_name'], # Обратный порядок
                fight_data['fighter1_name']
            ))
            
            if cursor.rowcount > 0:
                updated_count += cursor.rowcount
                print(f"   ✅ Обновлен бой: {fight_data['fighter1_name']} vs {fight_data['fighter2_name']}")
            else:
                print(f"   ⚠️ Бой не найден в БД: {fight_data['fighter1_name']} vs {fight_data['fighter2_name']}")
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"❌ Ошибка SQLite при обновлении боев: {e}")
    except Exception as e:
        print(f"❌ Произошла ошибка при обновлении боев: {e}")
    finally:
        if conn:
            conn.close()
    return updated_count

def main():
    print("=== ОБНОВЛЕНИЕ ДАННЫХ О КАРТАХ СОБЫТИЙ ===")
    conn = None
    total_updated_fights = 0
    try:
        conn = sqlite3.connect("ufc_ranker_v2.db")
        cursor = conn.cursor()
        
        # Получаем события с боями в БД (не из таблицы events, а из fights)
        cursor.execute("""
            SELECT DISTINCT event_name, COUNT(*) as fight_count
            FROM fights 
            WHERE event_name IS NOT NULL
            GROUP BY event_name
            HAVING fight_count > 0
            ORDER BY fight_count DESC
            LIMIT 20
        """)
        events_with_fights = cursor.fetchall()
        
        print(f"📊 Найдено {len(events_with_fights)} событий с боями для обновления")
        
        for event_name, fight_count in events_with_fights:
            print(f"\n🔍 Обрабатываем событие: {event_name} ({fight_count} боев)")
            
            # Пытаемся найти соответствующее событие в таблице events с URL
            cursor.execute("""
                SELECT id, name, event_url 
                FROM events 
                WHERE event_url IS NOT NULL AND event_url != ''
                AND (name = ? OR name LIKE ? OR ? LIKE name)
                ORDER BY id DESC
                LIMIT 1
            """, (event_name, f"%{event_name}%", event_name))
            
            event_row = cursor.fetchone()
            if not event_row:
                print(f"   ⚠️ Событие не найдено в таблице events с URL")
                continue
                
            event_id, event_db_name, event_url = event_row
            print(f"   📋 Найдено в events: {event_db_name}")
            print(f"   🔗 URL: {event_url}")
            
            # Парсим карту события
            fights_data = parse_event_card(event_url)
            if fights_data:
                updated_count = update_fights_in_database(event_name, fights_data)
                total_updated_fights += updated_count
            else:
                print(f"   ❌ Не удалось получить данные о карте")
        
    except sqlite3.Error as e:
        print(f"❌ Ошибка SQLite: {e}")
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
    finally:
        if conn:
            conn.close()
    
    print(f"\n🎉 ОБНОВЛЕНИЕ ЗАВЕРШЕНО!")
    print(f"   Всего обновлено боев: {total_updated_fights}")

if __name__ == "__main__":
    main()
