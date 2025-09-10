#!/usr/bin/env python3
"""
Извлечение данных из ufc_stats.rda файла
"""

import gzip
import re
import struct

def extract_ufc_stats():
    """Извлекаем данные из RDA файла"""
    print("🥊 ИЗВЛЕЧЕНИЕ ДАННЫХ UFC.STATS")
    print("=" * 50)
    
    try:
        with gzip.open('temp_ufc_stats/data/ufc_stats.rda', 'rb') as f:
            data = f.read()
        
        print(f"📊 Размер данных: {len(data):,} байт ({len(data)/1024/1024:.1f} MB)")
        
        # Ищем имена бойцов
        fighter_names = re.findall(rb'[A-Za-z\s]{10,30}', data)
        unique_fighters = list(set([name.decode('utf-8', errors='ignore').strip() 
                                  for name in fighter_names if len(name) > 5]))
        
        print(f"\n👊 Найдено уникальных бойцов: {len(unique_fighters)}")
        print("Первые 20 бойцов:")
        for i, fighter in enumerate(unique_fighters[:20]):
            print(f"  {i+1:2d}. {fighter}")
        
        # Ищем числовые данные
        numbers = re.findall(rb'\d+\.\d+', data)
        if numbers:
            print(f"\n📈 Найдено числовых значений: {len(numbers)}")
            print("Примеры значений:", [float(n.decode()) for n in numbers[:10]])
        
        # Ищем даты
        dates = re.findall(rb'\d{4}-\d{2}-\d{2}', data)
        if dates:
            print(f"\n📅 Найдено дат: {len(dates)}")
            print("Примеры дат:", [d.decode() for d in dates[:10]])
        
        # Ищем названия столбцов
        columns = re.findall(rb'[a-z_]+', data)
        unique_columns = list(set([col.decode('utf-8', errors='ignore') 
                                 for col in columns if len(col) > 3 and b'_' in col]))
        
        print(f"\n📋 Найдено столбцов: {len(unique_columns)}")
        print("Названия столбцов:")
        for i, col in enumerate(sorted(unique_columns)[:20]):
            print(f"  {i+1:2d}. {col}")
        
        # Сохраняем извлеченные данные
        with open('extracted_ufc_stats.txt', 'w', encoding='utf-8') as f:
            f.write("UFC STATS - Извлеченные данные\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Уникальных бойцов: {len(unique_fighters)}\n")
            f.write("Бойцы:\n")
            for fighter in unique_fighters:
                f.write(f"  - {fighter}\n")
            f.write(f"\nСтолбцов: {len(unique_columns)}\n")
            f.write("Столбцы:\n")
            for col in sorted(unique_columns):
                f.write(f"  - {col}\n")
        
        print(f"\n💾 Данные сохранены в extracted_ufc_stats.txt")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    extract_ufc_stats()
