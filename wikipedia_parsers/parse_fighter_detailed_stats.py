#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Парсер детальной статистики бойцов с индивидуальных страниц Wikipedia
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

def parse_fighter_detailed_stats(profile_url):
    """Парсит детальную статистику бойца с его страницы Wikipedia"""
    
    if not profile_url or not profile_url.startswith('http'):
        return None
    
    tree = get_page(profile_url)
    if not tree:
        return None
    
    stats = {}
    
    try:
        # 1. Парсим таблицу с разбивкой рекорда
        record_breakdown_table = tree.xpath('//h2[@id="Mixed_martial_arts_record"]/ancestor::div[1]/following-sibling::table[1]')
        if record_breakdown_table:
            table = record_breakdown_table[0]
            rows = table.xpath('.//tr')
            
            for row in rows:
                cells = row.xpath('.//td | .//th')
                if len(cells) >= 3:
                    method = cells[0].text_content().strip()
                    wins = cells[1].text_content().strip()
                    losses = cells[2].text_content().strip()
                    
                    # Извлекаем числа
                    wins_num = re.search(r'(\d+)', wins)
                    losses_num = re.search(r'(\d+)', losses)
                    
                    if wins_num and losses_num:
                        wins_count = int(wins_num.group(1))
                        losses_count = int(losses_num.group(1))
                        
                        if 'knockout' in method.lower() or 'ko' in method.lower():
                            stats['wins_by_ko'] = wins_count
                            stats['losses_by_ko'] = losses_count
                        elif 'submission' in method.lower() or 'sub' in method.lower():
                            stats['wins_by_submission'] = wins_count
                            stats['losses_by_submission'] = losses_count
                        elif 'decision' in method.lower():
                            stats['wins_by_decision'] = wins_count
                            stats['losses_by_decision'] = losses_count
                        elif 'disqualification' in method.lower() or 'dq' in method.lower():
                            stats['wins_by_dq'] = wins_count
                            stats['losses_by_dq'] = losses_count
        
        # 2. Парсим основную таблицу с боями для получения дополнительной статистики
        main_table = tree.xpath('//h2[@id="Mixed_martial_arts_record"]/ancestor::div[1]/following-sibling::table[2]')
        if main_table:
            table = main_table[0]
            rows = table.xpath('.//tr')[1:]  # Пропускаем заголовок
            
            total_fights = 0
            total_wins = 0
            total_losses = 0
            total_draws = 0
            total_nc = 0
            
            wins_by_round = {}
            losses_by_round = {}
            avg_fight_time = 0
            total_fight_time = 0
            fight_times = []
            
            for row in rows:
                cells = row.xpath('.//td')
                if len(cells) >= 6:
                    result = cells[0].text_content().strip()
                    record = cells[1].text_content().strip()
                    method = cells[2].text_content().strip()
                    event = cells[3].text_content().strip()
                    date = cells[4].text_content().strip()
                    round_info = cells[5].text_content().strip()
                    time_info = cells[6].text_content().strip() if len(cells) > 6 else ""
                    
                    if result and record:
                        total_fights += 1
                        
                        # Парсим рекорд
                        record_parts = record.split('–')
                        if len(record_parts) >= 2:
                            wins = int(record_parts[0])
                            losses = int(record_parts[1])
                            
                            if 'Win' in result:
                                total_wins += 1
                                # Анализируем раунд
                                round_match = re.search(r'(\d+)', round_info)
                                if round_match:
                                    round_num = int(round_match.group(1))
                                    wins_by_round[round_num] = wins_by_round.get(round_num, 0) + 1
                            elif 'Loss' in result:
                                total_losses += 1
                                # Анализируем раунд
                                round_match = re.search(r'(\d+)', round_info)
                                if round_match:
                                    round_num = int(round_match.group(1))
                                    losses_by_round[round_num] = losses_by_round.get(round_num, 0) + 1
                            elif 'Draw' in result:
                                total_draws += 1
                            elif 'NC' in result or 'No Contest' in result:
                                total_nc += 1
                        
                        # Парсим время боя
                        if time_info:
                            time_match = re.search(r'(\d+):(\d+)', time_info)
                            if time_match:
                                minutes = int(time_match.group(1))
                                seconds = int(time_match.group(2))
                                total_seconds = minutes * 60 + seconds
                                fight_times.append(total_seconds)
                                total_fight_time += total_seconds
            
            # Вычисляем среднее время боя
            if fight_times:
                avg_fight_time = total_fight_time / len(fight_times)
                stats['avg_fight_time_seconds'] = round(avg_fight_time, 2)
            
            # Статистика по раундам
            if wins_by_round:
                stats['wins_by_round'] = wins_by_round
            if losses_by_round:
                stats['losses_by_round'] = losses_by_round
            
            # Общая статистика
            stats['total_fights'] = total_fights
            stats['total_wins'] = total_wins
            stats['total_losses'] = total_losses
            stats['total_draws'] = total_draws
            stats['total_nc'] = total_nc
        
        # 3. Парсим инфобокс для дополнительной информации
        infobox = tree.xpath('//table[contains(@class, "infobox")]')
        if infobox:
            infobox = infobox[0]
            rows = infobox.xpath('.//tr')
            
            for row in rows:
                cells = row.xpath('.//td | .//th')
                if len(cells) >= 2:
                    label = cells[0].text_content().strip()
                    value = cells[1].text_content().strip()
                    
                    if 'Years active' in label:
                        stats['years_active'] = value
                    elif 'Team' in label:
                        stats['team'] = value
                    elif 'Rank' in label:
                        stats['belt_rank'] = value
                    elif 'Fighting out of' in label:
                        stats['fighting_out_of'] = value
        
        return stats
        
    except Exception as e:
        print(f"   ⚠️ Ошибка при парсинге статистики: {e}")
        return None

def update_database_schema():
    """Обновляет схему базы данных для новых полей"""
    
    try:
        conn = sqlite3.connect("ufc_ranker_v2.db")
        cursor = conn.cursor()
        
        # Добавляем новые колонки в таблицу fight_records
        new_columns = [
            "wins_by_ko INTEGER DEFAULT 0",
            "losses_by_ko INTEGER DEFAULT 0", 
            "wins_by_submission INTEGER DEFAULT 0",
            "losses_by_submission INTEGER DEFAULT 0",
            "wins_by_decision INTEGER DEFAULT 0",
            "losses_by_decision INTEGER DEFAULT 0",
            "wins_by_dq INTEGER DEFAULT 0",
            "losses_by_dq INTEGER DEFAULT 0",
            "avg_fight_time_seconds REAL DEFAULT 0",
            "total_fights INTEGER DEFAULT 0",
            "total_nc INTEGER DEFAULT 0"
        ]
        
        for column in new_columns:
            try:
                cursor.execute(f"ALTER TABLE fight_records ADD COLUMN {column.split()[0]} {column.split()[1]} DEFAULT {column.split()[-1]}")
                print(f"   ✅ Добавлена колонка: {column.split()[0]}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"   ⚠️ Колонка {column.split()[0]} уже существует")
                else:
                    print(f"   ❌ Ошибка при добавлении колонки {column.split()[0]}: {e}")
        
        # Добавляем новые колонки в таблицу fighters
        fighter_columns = [
            "fighting_out_of TEXT",
            "years_active TEXT"
        ]
        
        for column in fighter_columns:
            try:
                cursor.execute(f"ALTER TABLE fighters ADD COLUMN {column.split()[0]} {column.split()[1]}")
                print(f"   ✅ Добавлена колонка в fighters: {column.split()[0]}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"   ⚠️ Колонка {column.split()[0]} уже существует в fighters")
                else:
                    print(f"   ❌ Ошибка при добавлении колонки {column.split()[0]}: {e}")
        
        conn.commit()
        conn.close()
        
        print("✅ Схема базы данных обновлена")
        
    except Exception as e:
        print(f"❌ Ошибка при обновлении схемы БД: {e}")

def update_fighter_detailed_stats():
    """Обновляет детальную статистику бойцов"""
    
    # Настройка кодировки для Windows
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    
    print("🥊 ОБНОВЛЕНИЕ ДЕТАЛЬНОЙ СТАТИСТИКИ БОЙЦОВ")
    print("=" * 60)
    
    # Обновляем схему БД
    print("🔧 Обновление схемы базы данных...")
    update_database_schema()
    
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
        print(f"📊 Найдено {len(fighters)} бойцов для обновления")
        
        updated_count = 0
        
        for fighter_id, name_en, profile_url in fighters:
            print(f"\n🔍 Обрабатываем {name_en}...")
            
            # Парсим детальную статистику
            stats = parse_fighter_detailed_stats(profile_url)
            
            if not stats:
                print(f"   ❌ Не удалось получить данные")
                continue
            
            # Обновляем таблицу fight_records
            fight_record_fields = [
                'wins_by_ko', 'losses_by_ko', 'wins_by_submission', 'losses_by_submission',
                'wins_by_decision', 'losses_by_decision', 'wins_by_dq', 'losses_by_dq',
                'avg_fight_time_seconds', 'total_fights', 'total_nc'
            ]
            
            update_fields = []
            update_values = []
            
            for field in fight_record_fields:
                if field in stats:
                    update_fields.append(f"{field} = ?")
                    update_values.append(stats[field])
            
            if update_fields:
                # Проверяем, есть ли запись в fight_records
                cursor.execute("SELECT id FROM fight_records WHERE fighter_id = ?", (fighter_id,))
                existing_record = cursor.fetchone()
                
                if existing_record:
                    # Обновляем существующую запись
                    update_values.append(fighter_id)
                    sql = f"UPDATE fight_records SET {', '.join(update_fields)} WHERE fighter_id = ?"
                    cursor.execute(sql, update_values)
                else:
                    # Создаем новую запись
                    update_values.insert(0, fighter_id)  # fighter_id в начало
                    placeholders = ', '.join(['?'] * (len(update_values) + 1))  # +1 для id
                    fields_str = 'fighter_id, ' + ', '.join([field.split()[0] for field in update_fields])
                    sql = f"INSERT INTO fight_records ({fields_str}) VALUES ({placeholders})"
                    cursor.execute(sql, update_values)
            
            # Обновляем таблицу fighters
            fighter_fields = ['fighting_out_of', 'years_active']
            
            fighter_update_fields = []
            fighter_update_values = []
            
            for field in fighter_fields:
                if field in stats:
                    fighter_update_fields.append(f"{field} = ?")
                    fighter_update_values.append(stats[field])
            
            if fighter_update_fields:
                fighter_update_values.append(fighter_id)
                sql = f"UPDATE fighters SET {', '.join(fighter_update_fields)} WHERE id = ?"
                cursor.execute(sql, fighter_update_values)
            
            updated_count += 1
            print(f"   ✅ Обновлено полей: {len(update_fields) + len(fighter_update_fields)}")
            
            # Показываем некоторые статистики
            if 'wins_by_ko' in stats:
                print(f"   📊 KO: {stats['wins_by_ko']} побед, {stats['losses_by_ko']} поражений")
            if 'wins_by_submission' in stats:
                print(f"   📊 Submission: {stats['wins_by_submission']} побед, {stats['losses_by_submission']} поражений")
            if 'avg_fight_time_seconds' in stats:
                print(f"   ⏱️ Среднее время боя: {stats['avg_fight_time_seconds']} сек")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Обновлено {updated_count} бойцов")
        
    except Exception as e:
        print(f"❌ Ошибка при обновлении статистики: {e}")

def show_updated_stats():
    """Показывает обновленную статистику"""
    
    try:
        conn = sqlite3.connect("ufc_ranker_v2.db")
        cursor = conn.cursor()
        
        print("\n📊 ОБНОВЛЕННАЯ СТАТИСТИКА БОЙЦОВ")
        print("=" * 60)
        
        # Показываем статистику для нескольких бойцов
        cursor.execute("""
            SELECT 
                f.name_en,
                fr.wins_by_ko,
                fr.losses_by_ko,
                fr.wins_by_submission,
                fr.losses_by_submission,
                fr.avg_fight_time_seconds,
                fr.total_fights
            FROM fighters f
            LEFT JOIN fight_records fr ON f.id = fr.fighter_id
            WHERE fr.wins_by_ko IS NOT NULL
            ORDER BY fr.wins_by_ko DESC
            LIMIT 10
        """)
        
        fighters = cursor.fetchall()
        
        for fighter in fighters:
            name, wins_ko, losses_ko, wins_sub, losses_sub, avg_time, total_fights = fighter
            print(f"\n🥊 {name}")
            print(f"   📊 KO: {wins_ko} побед, {losses_ko} поражений")
            print(f"   📊 Submission: {wins_sub} побед, {losses_sub} поражений")
            print(f"   ⏱️ Среднее время боя: {avg_time} сек")
            print(f"   🥊 Всего боев: {total_fights}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка при показе статистики: {e}")

def main():
    """Главная функция"""
    update_fighter_detailed_stats()
    show_updated_stats()

if __name__ == "__main__":
    main()









