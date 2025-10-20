import requests
from lxml import html
import sqlite3
from datetime import datetime
import sys
import codecs
import re

sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def get_page_content(url):
    """Загружает содержимое страницы"""
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

def parse_event_card_data(event_url):
    """Парсит данные о карте события с Wikipedia"""
    try:
        tree = get_page_content(event_url)
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
            cells = row.xpath('.//td')
            if len(cells) < 6:
                continue
            
            # Проверяем, является ли строка заголовком карты
            first_cell_text = cells[0].text_content().strip().lower()
            if 'main card' in first_cell_text or 'preliminary card' in first_cell_text or 'early preliminary card' in first_cell_text:
                current_card_type = cells[0].text_content().strip()
                fight_order = 0
                print(f"📋 Найдена карта: {current_card_type}")
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
                    import re
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
        
    except Exception as e:
        print(f"❌ Ошибка при парсинге карты события: {e}")
        return []

def update_event_fights_in_database():
    """Обновляет данные о боях событий в базе данных"""
    try:
        conn = sqlite3.connect("ufc_ranker_v2.db")
        cursor = conn.cursor()
        
        print("=== ОБНОВЛЕНИЕ ДАННЫХ О КАРТАХ СОБЫТИЙ ===")
        
        # Получаем события с URL (больше событий, включая прошедшие)
        cursor.execute("""
            SELECT id, name, event_url 
            FROM events 
            WHERE event_url IS NOT NULL AND event_url != ''
            ORDER BY id DESC
            LIMIT 50
        """)
        
        events = cursor.fetchall()
        print(f"📊 Найдено {len(events)} событий для обновления")
        
        total_updated = 0
        
        for event_id, event_name, event_url in events:
            print(f"\n🔍 Обрабатываем событие: {event_name}")
            
            # Парсим данные карты
            fights_data = parse_event_card_data(event_url)
            
            if not fights_data:
                print(f"   ❌ Не удалось получить данные о карте")
                continue
            
            # Обновляем бои в базе данных
            updated_count = 0
            for fight_data in fights_data:
                try:
                    # Ищем существующий бой
                    cursor.execute("""
                        SELECT id FROM fights 
                        WHERE event_name = ? AND fighter1_name = ? AND fighter2_name = ?
                        LIMIT 1
                    """, (event_name, fight_data['fighter1_name'], fight_data['fighter2_name']))
                    
                    fight_id = cursor.fetchone()
                    
                    if fight_id:
                        # Обновляем существующий бой
                        cursor.execute("""
                            UPDATE fights SET
                                card_type = ?,
                                judges_score = ?,
                                fight_order = ?,
                                is_title_fight = ?,
                                is_main_event = ?,
                                updated_at = ?
                            WHERE id = ?
                        """, (
                            fight_data['card_type'],
                            fight_data['judges_score'],
                            fight_data['fight_order'],
                            fight_data['is_title_fight'],
                            fight_data['is_main_event'],
                            datetime.now(),
                            fight_id[0]
                        ))
                        updated_count += 1
                        print(f"   ✅ Обновлен бой: {fight_data['fighter1_name']} vs {fight_data['fighter2_name']}")
                    else:
                        print(f"   ⚠️ Бой не найден в БД: {fight_data['fighter1_name']} vs {fight_data['fighter2_name']}")
                        
                except Exception as e:
                    print(f"   ❌ Ошибка при обновлении боя: {e}")
                    continue
            
            print(f"   📊 Обновлено боев: {updated_count}")
            total_updated += updated_count
        
        conn.commit()
        conn.close()
        
        print(f"\n🎉 ОБНОВЛЕНИЕ ЗАВЕРШЕНО!")
        print(f"   Всего обновлено боев: {total_updated}")
        
    except Exception as e:
        print(f"❌ Ошибка при обновлении базы данных: {e}")

if __name__ == "__main__":
    update_event_fights_in_database()
