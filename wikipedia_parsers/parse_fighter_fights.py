#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Парсер детальной информации о боях бойцов с индивидуальных страниц Wikipedia
"""

import sqlite3
import requests
from lxml import html
import re
from datetime import datetime
import sys
import codecs

def get_page(url):
    """Получает HTML страницу"""
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

def check_fight_duplicate(cursor, fight_data):
    """Проверяет, существует ли уже такой бой в БД"""
    try:
        # Проверяем дубликат по комбинации: событие + дата + оба бойца (в любом порядке)
        cursor.execute("""
            SELECT id FROM fights 
            WHERE event_name = ? AND fight_date = ? 
            AND (
                (fighter1_name = ? AND fighter2_name = ?) OR 
                (fighter1_name = ? AND fighter2_name = ?)
            )
            LIMIT 1
        """, (
            fight_data['event'],
            fight_data['date'],
            fight_data['fighter1_name'],
            fight_data['fighter2_name'],
            fight_data['fighter2_name'],  # Обратный порядок
            fight_data['fighter1_name']
        ))
        
        result = cursor.fetchone()
        return result is not None
        
    except Exception as e:
        print(f"   ⚠️ Ошибка при проверке дубликата: {e}")
        return False

def parse_fighter_fights(profile_url, fighter_id, fighter_name):
    """Парсит детальную информацию о боях бойца с его страницы Wikipedia"""
    
    if not profile_url or not profile_url.startswith('http'):
        return []
    
    tree = get_page(profile_url)
    if not tree:
        return []
    
    fights = []
    
    try:
        # Парсим основную таблицу с боями
        main_table = tree.xpath('//h2[@id="Mixed_martial_arts_record"]/ancestor::div[1]/following-sibling::table[2]')
        if main_table:
            table = main_table[0]
            rows = table.xpath('.//tr')[1:]  # Пропускаем заголовок
            
            for row in rows:
                cells = row.xpath('.//td')
                if len(cells) >= 10:
                    result = cells[0].text_content().strip()
                    record = cells[1].text_content().strip()
                    opponent = cells[2].text_content().strip()
                    method = cells[3].text_content().strip()
                    event = cells[4].text_content().strip()
                    date = cells[5].text_content().strip()
                    round_info = cells[6].text_content().strip()
                    time_info = cells[7].text_content().strip()
                    location = cells[8].text_content().strip()
                    notes = cells[9].text_content().strip()
                    
                    if result and record and event:
                        # Парсим дату
                        fight_date = None
                        if date:
                            try:
                                # Пробуем разные форматы дат
                                date_formats = [
                                    '%d %B %Y',  # 13 April 2024
                                    '%B %d, %Y',  # April 13, 2024
                                    '%d %b %Y',  # 13 Apr 2024
                                    '%b %d, %Y',  # Apr 13, 2024
                                    '%Y-%m-%d',  # 2024-04-13
                                ]
                                
                                for fmt in date_formats:
                                    try:
                                        fight_date = datetime.strptime(date, fmt).date()
                                        break
                                    except ValueError:
                                        continue
                            except:
                                pass
                        
                        # Парсим раунд
                        scheduled_rounds = None
                        if round_info:
                            round_match = re.search(r'(\d+)', round_info)
                            if round_match:
                                scheduled_rounds = int(round_match.group(1))
                        
                        # Парсим время
                        fight_time = None
                        if time_info:
                            time_match = re.search(r'(\d+):(\d+)', time_info)
                            if time_match:
                                minutes = int(time_match.group(1))
                                seconds = int(time_match.group(2))
                                fight_time = minutes * 60 + seconds
                        
                        # Определяем результат
                        is_win = 'Win' in result
                        is_loss = 'Loss' in result
                        is_draw = 'Draw' in result
                        is_nc = 'NC' in result or 'No Contest' in result
                        
                        # Определяем имя победителя
                        winner_name = None
                        if is_win:
                            winner_name = fighter_name
                        elif is_loss:
                            winner_name = opponent
                        elif is_draw:
                            winner_name = None  # Ничья - нет победителя
                        elif is_nc:
                            winner_name = None  # Несостоявшийся бой
                        
                        # Определяем тип боя
                        is_title_fight = 'title' in event.lower() or 'championship' in event.lower() or 'belt' in event.lower()
                        is_main_event = 'main' in event.lower() or 'headliner' in event.lower()
                        
                        # Используем переданное имя бойца
                        
                        fight_data = {
                            'fighter1_name': fighter_name,
                            'fighter2_name': opponent,
                            'weight_class': 'Unknown',  # Будет заполнено позже
                            'result': result,
                            'method': method,
                            'event': event,
                            'date': fight_date,
                            'round': scheduled_rounds,
                            'time': fight_time,
                            'location': location,
                            'notes': notes,
                            'is_win': 'Win' if is_win else None,
                            'is_loss': 'Loss' if is_loss else None,
                            'is_draw': 'Draw' if is_draw else None,
                            'is_nc': 'No Contest' if is_nc else None,
                            'is_title_fight': is_title_fight,
                            'is_main_event': is_main_event,
                            'winner_name': winner_name
                        }
                        
                        fights.append(fight_data)
        
        return fights
        
    except Exception as e:
        print(f"   ⚠️ Ошибка при парсинге боев: {e}")
        return []

def create_fights_table():
    """Создает таблицу для хранения детальной информации о боях"""
    
    try:
        conn = sqlite3.connect("ufc_ranker_v2.db")
        cursor = conn.cursor()
        
        # Создаем таблицу fighter_fights для детальной информации о боях
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fighter_fights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fighter_id INTEGER NOT NULL,
                result VARCHAR(50),
                record VARCHAR(20),
                method VARCHAR(100),
                event VARCHAR(200),
                fight_date DATE,
                scheduled_rounds INTEGER,
                fight_time_seconds INTEGER,
                location VARCHAR(200),
                notes TEXT,
                is_win BOOLEAN,
                is_loss BOOLEAN,
                is_draw BOOLEAN,
                is_nc BOOLEAN,
                is_title_fight BOOLEAN,
                is_main_event BOOLEAN,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(fighter_id) REFERENCES fighters (id)
            )
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Таблица fighter_fights создана")
        
    except Exception as e:
        print(f"❌ Ошибка при создании таблицы: {e}")

def parse_all_fighter_fights():
    """Парсит детальную информацию о боях для всех бойцов"""
    
    # Настройка кодировки для Windows
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    
    print("🥊 ПАРСИНГ ДЕТАЛЬНОЙ ИНФОРМАЦИИ О БОЯХ")
    print("=" * 60)
    
    # Создаем таблицу
    create_fights_table()
    
    try:
        conn = sqlite3.connect("ufc_ranker_v2.db")
        cursor = conn.cursor()
        
        # Получаем всех бойцов с URL профилей
        cursor.execute("""
            SELECT id, name_en, profile_url 
            FROM fighters 
            WHERE profile_url IS NOT NULL AND profile_url != ''
            ORDER BY id
        """)
        
        fighters = cursor.fetchall()
        print(f"📊 Найдено {len(fighters)} бойцов для парсинга")
        
        total_fights = 0
        
        for fighter_id, name_en, profile_url in fighters:
            print(f"\n🔍 Обрабатываем {name_en}...")
            
            # Парсим детальную информацию о боях
            fights = parse_fighter_fights(profile_url, fighter_id, name_en)
            
            if not fights:
                print(f"   ❌ Не удалось получить данные о боях")
                continue
            
            # Сохраняем бои в базу данных
            saved_count = 0
            for fight in fights:
                try:
                    # Проверяем дубликат боя
                    if check_fight_duplicate(cursor, fight):
                        continue  # Пропускаем дубликат
                    
                    cursor.execute("""
                        INSERT INTO fights (
                            event_name, fighter1_name, fighter2_name, weight_class,
                            method, round, time, location, notes,
                            is_win, is_loss, is_draw, is_nc, is_title_fight, is_main_event,
                            fight_date, scheduled_rounds, winner_name, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        fight['event'],
                        fight['fighter1_name'],
                        fight['fighter2_name'],
                        fight['weight_class'],
                        fight['method'],
                        fight['round'],
                        fight['time'],
                        fight['location'],
                        fight['notes'],
                        fight['is_win'],
                        fight['is_loss'],
                        fight['is_draw'],
                        fight['is_nc'],
                        fight['is_title_fight'],
                        fight['is_main_event'],
                        fight['date'],
                        fight['round'],
                        fight.get('winner_name'),  # Добавляем winner_name
                        datetime.now(),
                        datetime.now()
                    ))
                    total_fights += 1
                    saved_count += 1
                except Exception as e:
                    print(f"   ⚠️ Ошибка при сохранении боя: {e}")
                    continue
            
            print(f"   ✅ Сохранено {saved_count} новых боев (пропущено {len(fights) - saved_count} дубликатов)")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Всего сохранено {total_fights} боев")
        
    except Exception as e:
        print(f"❌ Ошибка при парсинге боев: {e}")

def show_fighter_fights():
    """Показывает примеры сохраненных боев"""
    
    try:
        conn = sqlite3.connect("ufc_ranker_v2.db")
        cursor = conn.cursor()
        
        print("\n📊 ПРИМЕРЫ СОХРАНЕННЫХ БОЕВ")
        print("=" * 60)
        
        # Показываем несколько примеров
        cursor.execute("""
            SELECT 
                f1.name_en,
                f.is_win,
                f.is_loss,
                f.is_draw,
                f.is_nc,
                f.method,
                f.event_name,
                f.fight_date,
                f.scheduled_rounds,
                f.location,
                f.is_title_fight,
                f.is_main_event
            FROM fights f
            JOIN fighters f1 ON f.fighter1_name = f1.name_en
            ORDER BY f.fight_date DESC
            LIMIT 10
        """)
        
        fights = cursor.fetchall()
        
        for fight in fights:
            name, is_win, is_loss, is_draw, is_nc, method, event, date, rounds, location, is_title, is_main = fight
            
            # Определяем результат
            result = "Unknown"
            if is_win:
                result = "Win"
            elif is_loss:
                result = "Loss"
            elif is_draw:
                result = "Draw"
            elif is_nc:
                result = "No Contest"
            
            print(f"\n🥊 {name}")
            print(f"   Результат: {result}")
            print(f"   Метод: {method}")
            print(f"   Событие: {event}")
            print(f"   Дата: {date}")
            print(f"   Раунды: {rounds}")
            print(f"   Место: {location}")
            if is_title:
                print(f"   🏆 Титульный бой")
            if is_main:
                print(f"   ⭐ Главный бой")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка при показе боев: {e}")

def parse_event_card(event_url):
    """Парсит страницу события Wikipedia для извлечения информации о картах боев"""
    tree = get_page(event_url)
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
            
            # Пропускаем строки с заголовками или пустыми строками
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

def update_fights_cards_in_database(event_name, fights_data, cursor):
    """Обновляет существующие бои в БД с информацией о картах"""
    updated_count = 0
    try:
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
        
    except Exception as e:
        print(f"❌ Произошла ошибка при обновлении боев: {e}")
    
    return updated_count

def update_event_cards_in_database():
    """Обновляет данные о картах событий в базе данных"""
    conn = None
    total_updated_fights = 0
    try:
        conn = sqlite3.connect("ufc_ranker_v2.db")
        cursor = conn.cursor()
        
        print("=== ОБНОВЛЕНИЕ ДАННЫХ О КАРТАХ СОБЫТИЙ ===")
        
        # Получаем события с боями в БД, которые имеют Wikipedia URL
        cursor.execute("""
            SELECT DISTINCT f.event_name, COUNT(*) as fight_count
            FROM fights f
            INNER JOIN events e ON (f.event_name = e.name OR f.event_name LIKE '%' || e.name || '%')
            WHERE f.event_name IS NOT NULL 
            AND e.event_url IS NOT NULL AND e.event_url != ''
            GROUP BY f.event_name
            HAVING fight_count > 0
            ORDER BY fight_count DESC
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
                updated_count = update_fights_cards_in_database(event_name, fights_data, cursor)
                total_updated_fights += updated_count
            else:
                print(f"   ❌ Не удалось получить данные о карте")
        
        conn.commit()
        
    except sqlite3.Error as e:
        print(f"❌ Ошибка SQLite: {e}")
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
    finally:
        if conn:
            conn.close()
    
    print(f"\n🎉 ОБНОВЛЕНИЕ КАРТ ЗАВЕРШЕНО!")
    print(f"   Всего обновлено боев: {total_updated_fights}")
    return total_updated_fights

def main():
    """Главная функция"""
    print("=== ПАРСЕР БОЕВ БОЙЦОВ И КАРТ СОБЫТИЙ ===")
    print("1. Парсинг боев бойцов...")
    parse_all_fighter_fights()
    show_fighter_fights()
    
    print("\n2. Обновление карт событий...")
    update_event_cards_in_database()

if __name__ == "__main__":
    main()
