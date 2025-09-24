#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ текущей структуры базы данных
"""

import sqlite3
import sys

def analyze_database_structure():
    """Анализирует структуру базы данных"""
    
    print("🔍 АНАЛИЗ СТРУКТУРЫ БАЗЫ ДАННЫХ")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect("ufc_ranker_v2.db")
        cursor = conn.cursor()
        
        # Получаем список всех таблиц
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        
        tables = cursor.fetchall()
        print(f"📊 Найдено таблиц: {len(tables)}")
        print()
        
        for table_name, in tables:
            print(f"📋 ТАБЛИЦА: {table_name}")
            print("-" * 40)
            
            # Получаем информацию о колонках
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print(f"   Колонок: {len(columns)}")
            for col in columns:
                col_id, name, data_type, not_null, default_val, pk = col
                pk_mark = " 🔑" if pk else ""
                not_null_mark = " NOT NULL" if not_null else ""
                default_mark = f" DEFAULT {default_val}" if default_val else ""
                print(f"   • {name} ({data_type}){not_null_mark}{default_mark}{pk_mark}")
            
            # Получаем количество записей
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   📊 Записей: {count}")
            
            # Показываем примеры данных для первых 3 записей
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                sample_data = cursor.fetchall()
                print(f"   📝 Примеры данных:")
                for i, row in enumerate(sample_data, 1):
                    print(f"      {i}. {row}")
            
            print()
        
        # Проверяем индексы
        print("🔍 ИНДЕКСЫ")
        print("-" * 40)
        cursor.execute("""
            SELECT name, tbl_name, sql FROM sqlite_master 
            WHERE type='index' AND name NOT LIKE 'sqlite_%'
            ORDER BY tbl_name, name
        """)
        
        indexes = cursor.fetchall()
        if indexes:
            for name, table, sql in indexes:
                print(f"   📌 {table}.{name}")
                if sql:
                    print(f"      {sql}")
        else:
            print("   ❌ Индексы не найдены")
        
        print()
        
        # Проверяем внешние ключи
        print("🔗 ВНЕШНИЕ КЛЮЧИ")
        print("-" * 40)
        cursor.execute("PRAGMA foreign_key_list(fighters)")
        fk_fighters = cursor.fetchall()
        if fk_fighters:
            print("   fighters:")
            for fk in fk_fighters:
                print(f"      {fk}")
        
        cursor.execute("PRAGMA foreign_key_list(fights)")
        fk_fights = cursor.fetchall()
        if fk_fights:
            print("   fights:")
            for fk in fk_fights:
                print(f"      {fk}")
        
        cursor.execute("PRAGMA foreign_key_list(rankings)")
        fk_rankings = cursor.fetchall()
        if fk_rankings:
            print("   rankings:")
            for fk in fk_rankings:
                print(f"      {fk}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка при анализе БД: {e}")

if __name__ == "__main__":
    analyze_database_structure()
