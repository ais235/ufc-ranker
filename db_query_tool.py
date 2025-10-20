#!/usr/bin/env python3
"""
🔧 Инструмент для работы с базой данных UFC Ranker
Позволяет выполнять SQL запросы напрямую через командную строку
"""

import sqlite3
import pandas as pd
import sys
import argparse
from pathlib import Path

class UFCDataBase:
    def __init__(self, db_path="ufc_ranker_v2.db"):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Подключение к базе данных"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Для доступа к колонкам по имени
            print(f"✅ Подключено к базе данных: {self.db_path}")
            return True
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            return False
    
    def execute_query(self, query, params=None):
        """Выполнение SQL запроса"""
        if not self.conn:
            if not self.connect():
                return None
        
        try:
            cursor = self.conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Получаем результаты
            results = cursor.fetchall()
            
            # Преобразуем в список словарей для удобства
            columns = [description[0] for description in cursor.description] if cursor.description else []
            data = [dict(zip(columns, row)) for row in results]
            
            return data
        except Exception as e:
            print(f"❌ Ошибка выполнения запроса: {e}")
            return None
    
    def execute_query_pandas(self, query, params=None):
        """Выполнение SQL запроса с возвратом DataFrame"""
        if not self.conn:
            if not self.connect():
                return None
        
        try:
            if params:
                df = pd.read_sql_query(query, self.conn, params=params)
            else:
                df = pd.read_sql_query(query, self.conn)
            return df
        except Exception as e:
            print(f"❌ Ошибка выполнения запроса: {e}")
            return None
    
    def get_tables(self):
        """Получение списка таблиц"""
        query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        results = self.execute_query(query)
        return [row['name'] for row in results] if results else []
    
    def get_table_info(self, table_name):
        """Получение информации о таблице"""
        query = f"PRAGMA table_info({table_name})"
        return self.execute_query(query)
    
    def get_table_count(self, table_name):
        """Получение количества записей в таблице"""
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        result = self.execute_query(query)
        return result[0]['count'] if result else 0
    
    def close(self):
        """Закрытие соединения"""
        if self.conn:
            self.conn.close()
            self.conn = None

def print_results(results, limit=20):
    """Красивый вывод результатов"""
    if not results:
        print("❌ Нет результатов")
        return
    
    if len(results) == 0:
        print("📭 Результаты пусты")
        return
    
    # Ограничиваем вывод
    display_results = results[:limit]
    
    print(f"📊 Найдено записей: {len(results)}")
    if len(results) > limit:
        print(f"📋 Показано первых {limit} записей")
    
    print("\n" + "="*80)
    
    # Выводим заголовки
    if display_results:
        columns = list(display_results[0].keys())
        header = " | ".join([f"{col:15}" for col in columns])
        print(header)
        print("-" * len(header))
        
        # Выводим данные
        for row in display_results:
            values = []
            for col in columns:
                value = str(row[col]) if row[col] is not None else "NULL"
                if len(value) > 15:
                    value = value[:12] + "..."
                values.append(f"{value:15}")
            print(" | ".join(values))
    
    print("="*80)

def main():
    parser = argparse.ArgumentParser(description="🔧 Инструмент для работы с БД UFC Ranker")
    parser.add_argument("query", nargs="?", help="SQL запрос для выполнения")
    parser.add_argument("-f", "--file", help="Файл с SQL запросом")
    parser.add_argument("-t", "--tables", action="store_true", help="Показать все таблицы")
    parser.add_argument("-i", "--info", help="Показать информацию о таблице")
    parser.add_argument("-c", "--count", help="Показать количество записей в таблице")
    parser.add_argument("-l", "--limit", type=int, default=20, help="Лимит вывода записей (по умолчанию 20)")
    parser.add_argument("-p", "--pandas", action="store_true", help="Использовать pandas для вывода")
    parser.add_argument("-db", "--database", default="ufc_ranker_v2.db", help="Путь к базе данных")
    
    args = parser.parse_args()
    
    # Инициализация БД
    db = UFCDataBase(args.database)
    
    try:
        if args.tables:
            # Показать все таблицы
            tables = db.get_tables()
            print("📋 Таблицы в базе данных:")
            for table in tables:
                count = db.get_table_count(table)
                print(f"  📊 {table:20} - {count:4} записей")
        
        elif args.info:
            # Показать информацию о таблице
            info = db.get_table_info(args.info)
            if info:
                print(f"📋 Структура таблицы: {args.info}")
                print("-" * 50)
                for col in info:
                    print(f"  {col['name']:20} {col['type']:15} {'NOT NULL' if not col['notnull'] else 'NULL':8}")
            else:
                print(f"❌ Таблица {args.info} не найдена")
        
        elif args.count:
            # Показать количество записей
            count = db.get_table_count(args.count)
            print(f"📊 Таблица {args.count}: {count} записей")
        
        elif args.query:
            # Выполнить SQL запрос
            results = db.execute_query(args.query)
            if results is not None:
                print_results(results, args.limit)
        
        elif args.file:
            # Выполнить запрос из файла
            try:
                with open(args.file, 'r', encoding='utf-8') as f:
                    query = f.read()
                results = db.execute_query(query)
                if results is not None:
                    print_results(results, args.limit)
            except FileNotFoundError:
                print(f"❌ Файл {args.file} не найден")
        
        else:
            # Интерактивный режим
            print("🔧 Интерактивный режим работы с БД UFC Ranker")
            print("Введите SQL запросы (или 'exit' для выхода):")
            print("-" * 50)
            
            while True:
                try:
                    query = input("\nSQL> ").strip()
                    
                    if query.lower() in ['exit', 'quit', 'q']:
                        break
                    
                    if not query:
                        continue
                    
                    if query.lower() == 'tables':
                        tables = db.get_tables()
                        print("📋 Таблицы:")
                        for table in tables:
                            count = db.get_table_count(table)
                            print(f"  📊 {table:20} - {count:4} записей")
                        continue
                    
                    results = db.execute_query(query)
                    if results is not None:
                        print_results(results, args.limit)
                
                except KeyboardInterrupt:
                    print("\n👋 До свидания!")
                    break
                except Exception as e:
                    print(f"❌ Ошибка: {e}")
    
    finally:
        db.close()

if __name__ == "__main__":
    main()










