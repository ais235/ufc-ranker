#!/usr/bin/env python3
"""
Просмотрщик базы данных UFC Ranker
Показывает все 37 параметров статистики бойцов
"""

import sqlite3
import pandas as pd
from tabulate import tabulate

def view_database():
    conn = sqlite3.connect('ufc_ranker_v2.db')
    
    print("🥊 UFC RANKER - Просмотр базы данных")
    print("=" * 50)
    
    # 1. Общая статистика
    print("\n📊 ОБЩАЯ СТАТИСТИКА:")
    tables = ['fighters', 'events', 'fights', 'fight_stats', 'weight_classes', 'rankings']
    for table in tables:
        try:
            cursor = conn.cursor()
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            print(f"  {table:15}: {count:4d} записей")
        except:
            print(f"  {table:15}: таблица не найдена")
    
    # 2. 37 параметров статистики
    print("\n📈 37 ПАРАМЕТРОВ СТАТИСТИКИ БОЙЦА:")
    cursor = conn.cursor()
    cursor.execute('PRAGMA table_info(fight_stats)')
    columns = cursor.fetchall()
    
    for i, col in enumerate(columns, 1):
        print(f"  {i:2d}. {col[1]:<25} ({col[2]})")
    
    # 3. Примеры данных статистики
    print("\n📋 ПРИМЕРЫ ДАННЫХ СТАТИСТИКИ:")
    cursor.execute("""
        SELECT 
            fs.id,
            f.name_ru as fighter_name,
            fs.round_number,
            fs.knockdowns,
            fs.significant_strikes_landed,
            fs.significant_strikes_attempted,
            fs.significant_strikes_rate,
            fs.takedown_successful,
            fs.takedown_attempted,
            fs.takedown_rate,
            fs.result,
            fs.winner
        FROM fight_stats fs
        JOIN fighters f ON fs.fighter_id = f.id
        LIMIT 5
    """)
    
    rows = cursor.fetchall()
    if rows:
        headers = ['ID', 'Боец', 'Раунд', 'Нокауты', 'Удары (попал)', 'Удары (всего)', 'Точность %', 'Тейкдауны (успех)', 'Тейкдауны (всего)', 'Тейкдауны %', 'Результат', 'Победитель']
        print(tabulate(rows, headers=headers, tablefmt='grid'))
    
    # 4. Статистика по бойцам
    print("\n👊 СТАТИСТИКА ПО БОЙЦАМ:")
    cursor.execute("""
        SELECT 
            f.name_ru,
            f.country,
            COUNT(fs.id) as total_rounds,
            SUM(fs.knockdowns) as total_knockdowns,
            SUM(fs.significant_strikes_landed) as total_strikes,
            AVG(fs.significant_strikes_rate) as avg_accuracy,
            SUM(fs.takedown_successful) as total_takedowns
        FROM fighters f
        LEFT JOIN fight_stats fs ON f.id = fs.fighter_id
        GROUP BY f.id, f.name_ru, f.country
        ORDER BY total_rounds DESC
    """)
    
    fighter_stats = cursor.fetchall()
    if fighter_stats:
        headers = ['Боец', 'Страна', 'Раундов', 'Нокаутов', 'Ударов', 'Точность %', 'Тейкдаунов']
        print(tabulate(fighter_stats, headers=headers, tablefmt='grid'))
    
    # 5. Весовые категории
    print("\n⚖️ ВЕСОВЫЕ КАТЕГОРИИ:")
    cursor.execute("SELECT id, name_ru, name_en FROM weight_classes")
    weight_classes = cursor.fetchall()
    if weight_classes:
        headers = ['ID', 'Русское название', 'Английское название']
        print(tabulate(weight_classes, headers=headers, tablefmt='grid'))
    
    conn.close()
    print("\n✅ Просмотр завершен!")

if __name__ == "__main__":
    view_database()
