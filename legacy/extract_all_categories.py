#!/usr/bin/env python3
"""
Универсальный скрипт для извлечения рейтингов всех весовых категорий UFC
"""

from bs4 import BeautifulSoup
import re
import os

def clean_text(text):
    """Очищает текст от лишних пробелов"""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def extract_fighters_from_category(category_section, category_name):
    """Извлекает список бойцов из конкретной весовой категории"""
    
    fighters = []
    
    # Извлекаем чемпиона (first-fighter)
    champion = category_section.find('div', class_='first-fighter')
    if champion:
        name_elem = champion.find('div', class_='fighter-name')
        if name_elem:
            name = clean_text(name_elem.get_text())
            fighters.append({
                'rank': 'Ч',
                'name': name,
                'status': 'Чемпион'
            })
    
    # Извлекаем остальных бойцов (next-fighter)
    next_fighters = category_section.find_all('div', class_='next-fighter')
    
    for fighter in next_fighters:
        # Получаем номер в рейтинге
        number_elem = fighter.find('div', class_='fighter-number')
        if not number_elem:
            continue
            
        rank = clean_text(number_elem.get_text())
        
        # Получаем имя
        name_elem = fighter.find('div', class_='fighter-name')
        if not name_elem:
            continue
            
        name = clean_text(name_elem.get_text())
        
        # Проверяем, есть ли изменения в рейтинге
        move_elem = fighter.find('div', class_='move')
        move_info = ""
        if move_elem:
            move_text = clean_text(move_elem.get_text())
            if 'up' in move_elem.get('class', []):
                move_info = f"↑{move_text}"
            elif 'down' in move_elem.get('class', []):
                move_info = f"↓{move_text}"
        
        fighters.append({
            'rank': rank,
            'name': name,
            'status': f"#{rank}",
            'move': move_info
        })
    
    return fighters

def save_category_to_file(fighters, category_name, filename):
    """Сохраняет рейтинг категории в текстовый файл"""
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"🥊 UFC - {category_name}\n")
            f.write("=" * 50 + "\n\n")
            
            for i, fighter in enumerate(fighters, 1):
                status = fighter['status']
                move = fighter.get('move', '')
                f.write(f"{i:2d}. {status:>3} | {fighter['name']:<30} {move}\n")
            
            f.write("\n" + "=" * 50 + "\n")
            f.write(f"Всего бойцов: {len(fighters)}\n")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка при сохранении {filename}: {e}")
        return False

def extract_all_categories():
    """Извлекает рейтинги всех весовых категорий"""
    
    try:
        # Читаем HTML файл
        with open('fight_ru_ufc.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print("📄 HTML файл загружен")
        
        # Парсим HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Ищем все секции весовых категорий
        weight_sections = soup.find_all('div', class_='weight-name')
        
        print(f"📊 Найдено весовых категорий: {len(weight_sections)}")
        
        # Создаем папку для результатов
        results_dir = "rankings"
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
            print(f"📁 Создана папка: {results_dir}")
        
        total_fighters = 0
        processed_categories = 0
        
        for section in weight_sections:
            category_name = clean_text(section.get_text())
            
            # Пропускаем пустые или служебные категории
            if not category_name or category_name in ['Весовая категория', 'Все']:
                continue
            
            print(f"\n🔍 Обрабатываем: {category_name}")
            
            # Находим родительскую секцию с бойцами
            category_section = section.find_parent('div', class_='org-single')
            if not category_section:
                print(f"   ⚠️ Секция с бойцами не найдена")
                continue
            
            # Извлекаем бойцов
            fighters = extract_fighters_from_category(category_section, category_name)
            
            if not fighters:
                print(f"   ⚠️ Бойцы не найдены")
                continue
            
            print(f"   ✅ Найдено бойцов: {len(fighters)}")
            
            # Создаем безопасное имя файла
            safe_filename = re.sub(r'[<>:"/\\|?*]', '_', category_name.lower())
            safe_filename = re.sub(r'\s+', '_', safe_filename)
            filename = os.path.join(results_dir, f"{safe_filename}.txt")
            
            # Сохраняем в файл
            if save_category_to_file(fighters, category_name, filename):
                print(f"   💾 Сохранено в: {filename}")
                total_fighters += len(fighters)
                processed_categories += 1
            else:
                print(f"   ❌ Ошибка сохранения")
        
        print(f"\n🎉 Обработка завершена!")
        print(f"📊 Обработано категорий: {processed_categories}")
        print(f"👥 Всего бойцов: {total_fighters}")
        print(f"📁 Результаты сохранены в папке: {results_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при извлечении данных: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция"""
    print("🥊 UFC All Categories Rankings Extractor")
    print("=" * 50)
    
    success = extract_all_categories()
    
    if success:
        print("\n✅ Все рейтинги успешно извлечены и сохранены!")
    else:
        print("\n❌ Произошла ошибка при извлечении рейтингов")

if __name__ == "__main__":
    main()

