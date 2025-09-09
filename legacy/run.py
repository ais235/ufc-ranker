#!/usr/bin/env python3
"""
UFC Rankings Extractor - Главный скрипт
"""

import requests
import os
import sys

def save_page():
    """Сохраняет страницу fight.ru"""
    url = "https://fight.ru/fighter-ratings/ufc/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        print("🔄 Загружаем страницу...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        print("✅ Страница успешно загружена!")
        
        # Очищаем HTML от &shy; символов
        print("🧹 Очищаем HTML от &shy; символов...")
        cleaned_html = response.text.replace('&shy;', '').replace('\u00ad', '')
        
        # Сохраняем в файл
        filename = "fight_ru_ufc.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(cleaned_html)
        
        print(f"💾 Страница сохранена в файл: {filename}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при загрузке страницы: {e}")
        return False

def main():
    """Основная функция"""
    print("🥊 UFC Rankings Extractor")
    print("=" * 40)
    
    # Проверяем, есть ли уже сохраненная страница
    if not os.path.exists('fight_ru_ufc.html'):
        print("📄 Сохраняем страницу...")
        if not save_page():
            return
    else:
        print("📄 Используем существующую страницу")
    
    # Извлечение рейтингов по категориям (в txt)
    print("\n🔍 Извлекаем рейтинги всех категорий в TXT...")
    try:
        from extract_all_categories import extract_all_categories
        extract_all_categories()
    except ImportError:
        print("⚠ Не удалось импортировать extract_all_categories — пропускаем шаг TXT")
    except Exception as e:
        print(f"⚠ Ошибка извлечения TXT рейтингов: {e}")

    # Генерация HTML страниц категорий с данными профилей
    print("\n🧩 Генерируем HTML страницы категорий c данными профилей...")
    try:
        from build_category_pages import build_pages
        build_pages()
        print("✅ HTML страницы категорий готовы (папка category_pages)")
    except ImportError:
        print("❌ Не удалось импортировать build_category_pages")
    except Exception as e:
        print(f"❌ Ошибка при сборке HTML страниц: {e}")

if __name__ == "__main__":
    main()
