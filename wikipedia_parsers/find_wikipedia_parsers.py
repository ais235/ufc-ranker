#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Поиск всех парсеров Википедии в проекте
"""

import os
import re
import glob

def find_wikipedia_parsers():
    """Находит все парсеры Википедии в проекте"""
    
    print("🔍 ПОИСК ПАРСЕРОВ ВИКИПЕДИИ В ПРОЕКТЕ")
    print("=" * 60)
    
    # Ищем все Python файлы
    python_files = glob.glob("*.py")
    
    wikipedia_parsers = []
    
    for file in python_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Проверяем, содержит ли файл упоминания Википедии
                if any(keyword in content.lower() for keyword in [
                    'wikipedia', 'wiki', 'en.wikipedia.org', 
                    'parse', 'парсер', 'парсинг'
                ]):
                    # Извлекаем информацию о файле
                    lines = content.split('\n')
                    
                    # Ищем описание/назначение файла
                    description = "Описание не найдено"
                    for line in lines[:20]:  # Первые 20 строк
                        if any(keyword in line.lower() for keyword in [
                            'парсер', 'parser', 'парсинг', 'parsing',
                            'события', 'events', 'бойцы', 'fighters',
                            'рейтинги', 'rankings', 'бои', 'fights'
                        ]):
                            if '#' in line or '"""' in line or "'''" in line:
                                description = line.strip().replace('#', '').replace('"""', '').replace("'''", '').strip()
                                break
                    
                    # Ищем URL Википедии
                    wikipedia_urls = re.findall(r'https?://[^\s\'"]*wikipedia[^\s\'"]*', content)
                    
                    # Ищем функции парсинга
                    functions = re.findall(r'def\s+(\w*parse\w*|parse_\w+)', content)
                    
                    wikipedia_parsers.append({
                        'file': file,
                        'description': description,
                        'wikipedia_urls': wikipedia_urls,
                        'parse_functions': functions,
                        'size': os.path.getsize(file)
                    })
                    
        except Exception as e:
            print(f"❌ Ошибка при чтении {file}: {e}")
    
    # Сортируем по размеру файла (большие файлы обычно основные парсеры)
    wikipedia_parsers.sort(key=lambda x: x['size'], reverse=True)
    
    print(f"📊 Найдено парсеров: {len(wikipedia_parsers)}")
    print()
    
    for i, parser in enumerate(wikipedia_parsers, 1):
        print(f"📋 {i}. {parser['file']}")
        print(f"   📝 Описание: {parser['description']}")
        print(f"   📏 Размер: {parser['size']:,} байт")
        
        if parser['wikipedia_urls']:
            print(f"   🌐 URL Википедии:")
            for url in parser['wikipedia_urls'][:3]:  # Показываем первые 3 URL
                print(f"      • {url}")
        
        if parser['parse_functions']:
            print(f"   🔧 Функции парсинга:")
            for func in parser['parse_functions'][:5]:  # Показываем первые 5 функций
                print(f"      • {func}")
        
        print()
    
    # Группируем по типу парсера
    print("📊 ГРУППИРОВКА ПО ТИПАМ ПАРСЕРОВ")
    print("=" * 60)
    
    event_parsers = [p for p in wikipedia_parsers if any(keyword in p['file'].lower() for keyword in ['event', 'события'])]
    fighter_parsers = [p for p in wikipedia_parsers if any(keyword in p['file'].lower() for keyword in ['fighter', 'бойц', 'rankings', 'рейтинг'])]
    fight_parsers = [p for p in wikipedia_parsers if any(keyword in p['file'].lower() for keyword in ['fight', 'бои'])]
    other_parsers = [p for p in wikipedia_parsers if p not in event_parsers + fighter_parsers + fight_parsers]
    
    print(f"🎪 ПАРСЕРЫ СОБЫТИЙ ({len(event_parsers)}):")
    for parser in event_parsers:
        print(f"   • {parser['file']}")
    
    print(f"\n🥊 ПАРСЕРЫ БОЙЦОВ И РЕЙТИНГОВ ({len(fighter_parsers)}):")
    for parser in fighter_parsers:
        print(f"   • {parser['file']}")
    
    print(f"\n⚔️ ПАРСЕРЫ БОЕВ ({len(fight_parsers)}):")
    for parser in fight_parsers:
        print(f"   • {parser['file']}")
    
    print(f"\n🔧 ДРУГИЕ ПАРСЕРЫ ({len(other_parsers)}):")
    for parser in other_parsers:
        print(f"   • {parser['file']}")
    
    return wikipedia_parsers

if __name__ == "__main__":
    find_wikipedia_parsers()
