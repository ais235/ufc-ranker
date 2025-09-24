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
                            'is_main_event': is_main_event
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
                            fight_date, scheduled_rounds, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

def main():
    """Главная функция"""
    parse_all_fighter_fights()
    show_fighter_fights()

if __name__ == "__main__":
    main()
