#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для исправления рейтингов UFC на основе официальной страницы UFC Rankings
"""

import sqlite3
import requests
from lxml import html
import re
from datetime import datetime
import os
import shutil

def create_backup():
    """Создает резервную копию базы данных"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"ufc_ranker_v2_backup_{timestamp}.db"
    shutil.copy2("ufc_ranker_v2.db", backup_file)
    print(f"✅ Создана резервная копия: {backup_file}")
    return backup_file

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

def parse_ufc_rankings():
    """Парсит официальные рейтинги UFC с Wikipedia"""
    
    url = "https://en.wikipedia.org/wiki/UFC_rankings"
    tree = get_page(url)
    
    if not tree:
        return None
    
    rankings_data = {}
    
    # Маппинг весовых категорий
    weight_class_mapping = {
        "Heavyweight": "Тяжелый вес",
        "Light Heavyweight": "Полутяжелый вес", 
        "Middleweight": "Средний вес",
        "Welterweight": "Полусредний вес",
        "Lightweight": "Легкий вес",
        "Featherweight": "Полулегкий вес",
        "Bantamweight": "Легчайший вес",
        "Flyweight": "Наилегчайший вес",
        "Women's Bantamweight": "Женский легчайший вес",
        "Women's Flyweight": "Женский наилегчайший вес",
        "Women's Strawweight": "Женский минимальный вес"
    }
    
    # XPath для поиска таблиц рейтингов
    weight_class_xpaths = {
        "Heavyweight": "//h2[contains(text(), 'Heavyweight')]/following-sibling::table[1]",
        "Light Heavyweight": "//h2[contains(text(), 'Light Heavyweight')]/following-sibling::table[1]",
        "Middleweight": "//h2[contains(text(), 'Middleweight')]/following-sibling::table[1]",
        "Welterweight": "//h2[contains(text(), 'Welterweight')]/following-sibling::table[1]",
        "Lightweight": "//h2[contains(text(), 'Lightweight')]/following-sibling::table[1]",
        "Featherweight": "//h2[contains(text(), 'Featherweight')]/following-sibling::table[1]",
        "Bantamweight": "//h2[contains(text(), 'Bantamweight')]/following-sibling::table[1]",
        "Flyweight": "//h2[contains(text(), 'Flyweight')]/following-sibling::table[1]",
        "Women's Bantamweight": "//h2[contains(text(), \"Women's Bantamweight\")]/following-sibling::table[1]",
        "Women's Flyweight": "//h2[contains(text(), \"Women's Flyweight\")]/following-sibling::table[1]",
        "Women's Strawweight": "//h2[contains(text(), \"Women's Strawweight\")]/following-sibling::table[1]"
    }
    
    for weight_class, xpath in weight_class_xpaths.items():
        print(f"🔍 Парсинг {weight_class}...")
        
        table = tree.xpath(xpath)
        if not table:
            print(f"   ❌ Таблица не найдена для {weight_class}")
            continue
            
        table = table[0]
        rows = table.xpath('.//tr')
        
        # Пропускаем заголовки (первые 1-2 строки)
        if len(rows) <= 1:
            print(f"   ❌ Таблица пуста для {weight_class}")
            continue
            
        # Определяем, сколько строк заголовка пропустить
        header_rows = 1
        if len(rows) > 1:
            first_row = rows[0]
            first_cell = first_row.xpath('.//td | .//th')
            if first_cell and 'rank' in first_cell[0].text_content().lower():
                header_rows = 1
            else:
                header_rows = 0
        
        rows = rows[header_rows:]
        
        weight_rankings = []
        
        for i, row in enumerate(rows):
            try:
                # Извлекаем данные из строки
                cells = row.xpath('.//td')
                if len(cells) < 3:
                    continue
                
                # Позиция в рейтинге
                rank_cell = cells[0]
                rank_text = rank_cell.text_content().strip()
                
                # Пропускаем пустые строки
                if not rank_text or rank_text == '':
                    continue
                
                # Определяем позицию
                if 'C' in rank_text or 'Champion' in rank_text:
                    rank_position = 0  # Чемпион
                    is_champion = True
                else:
                    # Извлекаем номер позиции
                    rank_match = re.search(r'(\d+)', rank_text)
                    if rank_match:
                        rank_position = int(rank_match.group(1))
                        is_champion = False
                    else:
                        continue
                
                # Имя бойца и ссылка
                fighter_cell = cells[1]
                fighter_link = fighter_cell.xpath('.//a')
                
                if fighter_link:
                    fighter_name = fighter_link[0].text_content().strip()
                    fighter_url = fighter_link[0].get('href', '')
                    if fighter_url.startswith('/wiki/'):
                        fighter_url = 'https://en.wikipedia.org' + fighter_url
                else:
                    fighter_name = fighter_cell.text_content().strip()
                    fighter_url = ''
                
                # Рекорд
                record_cell = cells[2]
                record_text = record_cell.text_content().strip()
                
                # Парсим рекорд
                wins, losses, draws, nc = parse_record(record_text)
                
                weight_rankings.append({
                    'rank_position': rank_position,
                    'is_champion': is_champion,
                    'fighter_name': fighter_name,
                    'fighter_url': fighter_url,
                    'record': record_text,
                    'wins': wins,
                    'losses': losses,
                    'draws': draws,
                    'nc': nc
                })
                
            except Exception as e:
                print(f"   ⚠️ Ошибка при парсинге строки {i+1}: {e}")
                continue
        
        if weight_rankings:
            rankings_data[weight_class] = weight_rankings
            print(f"   ✅ Найдено {len(weight_rankings)} бойцов")
        else:
            print(f"   ❌ Нет данных для {weight_class}")
    
    return rankings_data

def parse_record(record_text):
    """Парсит рекорд бойца из строки"""
    try:
        # Примеры: "17–0", "27–1", "20–1–1 (1 NC)"
        record_text = record_text.strip()
        
        # Убираем лишние символы
        record_text = re.sub(r'[^\d–\-\(\)\s]', '', record_text)
        
        # Парсим основную часть рекорда
        main_parts = re.split(r'[–\-]', record_text)
        
        wins = int(main_parts[0]) if main_parts[0].strip().isdigit() else 0
        losses = int(main_parts[1]) if len(main_parts) > 1 and main_parts[1].strip().isdigit() else 0
        
        # Парсим NC (No Contest)
        nc_match = re.search(r'\((\d+)\s*NC\)', record_text)
        nc = int(nc_match.group(1)) if nc_match else 0
        
        # Парсим ничьи (если есть третья часть)
        draws = 0
        if len(main_parts) > 2:
            third_part = main_parts[2].strip()
            if third_part.isdigit():
                draws = int(third_part)
        
        return wins, losses, draws, nc
        
    except Exception as e:
        print(f"   ⚠️ Ошибка при парсинге рекорда '{record_text}': {e}")
        return 0, 0, 0, 0

def clear_rankings_table(cursor):
    """Очищает таблицу rankings"""
    print("🗑️ Очищаем таблицу rankings...")
    cursor.execute("DELETE FROM rankings")
    print("   ✅ Таблица rankings очищена")

def update_rankings_in_database(rankings_data):
    """Обновляет рейтинги в базе данных"""
    
    # Создаем резервную копию
    backup_file = create_backup()
    
    try:
        conn = sqlite3.connect("ufc_ranker_v2.db")
        cursor = conn.cursor()
        
        # Очищаем таблицу rankings
        clear_rankings_table(cursor)
        
        # Получаем маппинг весовых категорий
        cursor.execute("SELECT id, name_en FROM weight_classes")
        weight_classes = {name_en: id for id, name_en in cursor.fetchall()}
        
        total_updated = 0
        
        for weight_class, rankings in rankings_data.items():
            print(f"\n📊 Обновляем {weight_class}...")
            
            # Получаем ID весовой категории
            weight_class_id = weight_classes.get(weight_class)
            if not weight_class_id:
                print(f"   ❌ Весовая категория {weight_class} не найдена в БД")
                continue
            
            for ranking in rankings:
                try:
                    # Ищем бойца по имени
                    fighter_name = ranking['fighter_name']
                    cursor.execute("""
                        SELECT id FROM fighters 
                        WHERE name_en = ? OR full_name = ?
                        ORDER BY 
                            CASE WHEN name_en = ? THEN 1 ELSE 2 END,
                            id
                        LIMIT 1
                    """, (fighter_name, fighter_name, fighter_name))
                    
                    fighter_result = cursor.fetchone()
                    
                    if not fighter_result:
                        print(f"   ⚠️ Боец {fighter_name} не найден в БД")
                        continue
                    
                    fighter_id = fighter_result[0]
                    
                    # Вставляем рейтинг
                    cursor.execute("""
                        INSERT INTO rankings (
                            fighter_id, weight_class_id, rank_position, 
                            is_champion, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        fighter_id,
                        weight_class_id,
                        ranking['rank_position'],
                        ranking['is_champion'],
                        datetime.now(),
                        datetime.now()
                    ))
                    
                    total_updated += 1
                    
                    champion_mark = "👑" if ranking['is_champion'] else ""
                    print(f"   {champion_mark} #{ranking['rank_position']:2d} {fighter_name}")
                    
                except Exception as e:
                    print(f"   ❌ Ошибка при обновлении {ranking['fighter_name']}: {e}")
                    continue
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Обновлено {total_updated} рейтингов")
        print(f"💾 Резервная копия: {backup_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при обновлении БД: {e}")
        return False

def show_updated_rankings():
    """Показывает обновленные рейтинги"""
    
    try:
        conn = sqlite3.connect("ufc_ranker_v2.db")
        cursor = conn.cursor()
        
        print("\n🏆 ОБНОВЛЕННЫЕ РЕЙТИНГИ UFC")
        print("=" * 60)
        
        # Получаем все весовые категории с рейтингами
        cursor.execute("""
            SELECT wc.name_ru, wc.name_en, COUNT(r.id) as count
            FROM weight_classes wc
            LEFT JOIN rankings r ON wc.id = r.weight_class_id
            GROUP BY wc.id, wc.name_ru, wc.name_en
            ORDER BY wc.id
        """)
        
        weight_classes = cursor.fetchall()
        
        for name_ru, name_en, count in weight_classes:
            print(f"\n⚖️ {name_ru} ({name_en})")
            print("-" * 40)
            
            if count == 0:
                print("   ❌ Нет рейтингов")
                continue
            
            # Получаем топ-10 для этой категории
            cursor.execute("""
                SELECT 
                    f.name_en,
                    f.nickname,
                    r.rank_position,
                    r.is_champion,
                    fr.wins,
                    fr.losses,
                    fr.draws,
                    fr.no_contests
                FROM rankings r
                JOIN fighters f ON r.fighter_id = f.id
                LEFT JOIN fight_records fr ON f.id = fr.fighter_id
                WHERE r.weight_class_id = (
                    SELECT id FROM weight_classes WHERE name_en = ?
                )
                ORDER BY r.rank_position ASC
                LIMIT 10
            """, (name_en,))
            
            fighters = cursor.fetchall()
            
            for fighter in fighters:
                name_en, nickname, rank_pos, is_champion, wins, losses, draws, nc = fighter
                
                champion_mark = "👑" if is_champion else ""
                nickname_str = f' "{nickname}"' if nickname else ""
                record_str = f"{wins}-{losses}" if wins is not None and losses is not None else "N/A"
                if draws and draws > 0:
                    record_str += f"-{draws}"
                if nc and nc > 0:
                    record_str += f" ({nc} NC)"
                
                print(f"   {champion_mark} #{rank_pos:2d} {name_en}{nickname_str} ({record_str})")
        
        # Статистика
        cursor.execute("SELECT COUNT(*) FROM rankings")
        total_rankings = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM rankings WHERE is_champion = 1")
        total_champions = cursor.fetchone()[0]
        
        print(f"\n📊 СТАТИСТИКА:")
        print(f"   🥊 Всего рейтингов: {total_rankings}")
        print(f"   👑 Чемпионов: {total_champions}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка при показе рейтингов: {e}")

def main():
    """Главная функция"""
    print("🥊 ИСПРАВЛЕНИЕ РЕЙТИНГОВ UFC")
    print("=" * 50)
    print("📚 Источник: https://en.wikipedia.org/wiki/UFC_rankings")
    print()
    
    # Парсим официальные рейтинги
    print("🔍 Парсинг официальных рейтингов UFC...")
    rankings_data = parse_ufc_rankings()
    
    if not rankings_data:
        print("❌ Не удалось получить данные рейтингов")
        return
    
    print(f"✅ Получены данные для {len(rankings_data)} весовых категорий")
    
    # Обновляем базу данных
    print("\n💾 Обновление базы данных...")
    if update_rankings_in_database(rankings_data):
        print("✅ Рейтинги успешно обновлены!")
        
        # Показываем результат
        show_updated_rankings()
    else:
        print("❌ Ошибка при обновлении рейтингов")

if __name__ == "__main__":
    main()
