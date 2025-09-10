#!/usr/bin/env python3
"""
Генерация страниц весовых категорий с данными из БД
"""

import sqlite3
import json
from datetime import datetime, date
import random
import os

def get_weight_classes():
    """Получаем весовые категории из БД"""
    conn = sqlite3.connect('ufc_ranker_v2.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name_ru, name_en, weight_min, weight_max 
        FROM weight_classes 
        ORDER BY weight_min
    """)
    
    weight_classes = cursor.fetchall()
    conn.close()
    
    return weight_classes

def get_fighters_by_weight_class(weight_class_name):
    """Получаем бойцов по весовой категории"""
    conn = sqlite3.connect('ufc_ranker_v2.db')
    cursor = conn.cursor()
    
    # Ищем бойцов в основной таблице
    cursor.execute("""
        SELECT name_ru, name_en, country, win, lose, draw
        FROM fighters 
        WHERE weight_class = ?
        ORDER BY win DESC, lose ASC
    """, (weight_class_name,))
    
    main_fighters = cursor.fetchall()
    
    # Ищем бойцов в ufc_stats
    cursor.execute("""
        SELECT name, total_wins, total_losses, total_draws
        FROM ufc_stats_fighters 
        WHERE total_fights > 0
        ORDER BY total_wins DESC, total_losses ASC
        LIMIT 10
    """)
    
    ufc_fighters = cursor.fetchall()
    
    conn.close()
    
    fighters = []
    
    # Добавляем основных бойцов
    for fighter in main_fighters:
        if fighter[0]:  # name_ru
            fighters.append({
                'name_ru': fighter[0],
                'name_en': fighter[1] or fighter[0],
                'country': fighter[2] or "Россия",
                'wins': fighter[3] or 0,
                'losses': fighter[4] or 0,
                'draws': fighter[5] or 0
            })
    
    # Добавляем бойцов ufc_stats
    for fighter in ufc_fighters:
        fighters.append({
            'name_ru': fighter[0],
            'name_en': fighter[0],
            'country': "США",
            'wins': fighter[1] or 0,
            'losses': fighter[2] or 0,
            'draws': fighter[3] or 0
        })
    
    return fighters

def generate_fighter_data(fighter_info, rank):
    """Генерируем полные данные бойца"""
    
    # Генерируем дополнительные данные
    fighter_data = {
        "name_ru": fighter_info['name_ru'],
        "name_en": fighter_info['name_en'],
        "nickname": generate_nickname(fighter_info['name_ru']),
        "country": fighter_info['country'],
        "rank": rank,
        "age": random.randint(25, 35),
        "height_inches": random.randint(65, 78),
        "height_cm": 0,
        "wins": fighter_info['wins'],
        "losses": fighter_info['losses'],
        "draws": fighter_info['draws'],
        "ko_wins": random.randint(0, min(8, max(1, fighter_info['wins']))),
        "sub_wins": random.randint(0, min(15, max(1, fighter_info['wins'])))
    }
    
    # Конвертируем единицы измерения
    fighter_data["height_cm"] = int(fighter_data["height_inches"] * 2.54)
    
    return fighter_data

def generate_nickname(name):
    """Генерируем никнейм для бойца"""
    nicknames = {
        "Ислам": "The Eagle",
        "Александр": "The Great",
        "Макс": "Blessed",
        "Джон": "Bones",
        "Фрэнсис": "The Predator",
        "Конор": "The Notorious",
        "Хабиб": "The Eagle",
        "AJ": "The Prodigy",
        "Aaron": "The Machine",
        "Alex": "The Destroyer",
        "Anthony": "The Beast",
        "Brian": "The Warrior",
        "Chris": "The Hammer",
        "Daniel": "The Lion",
        "David": "The King",
        "Eddie": "The Underground King",
        "Frankie": "The Answer",
        "Georges": "Rush",
        "Jose": "Scarface",
        "Junior": "Cigano"
    }
    
    for key, nickname in nicknames.items():
        if key in name:
            return nickname
    
    return "The Fighter"

def get_country_code(country):
    """Получаем код страны"""
    country_codes = {
        "Россия": "RU",
        "США": "US",
        "Бразилия": "BR",
        "Ирландия": "IE",
        "Австралия": "AU",
        "Канада": "CA",
        "Великобритания": "GB",
        "Франция": "FR",
        "Грузия": "GE",
        "Армения": "AM",
        "Польша": "PL",
        "Испания": "ES",
        "Азербайджан": "AZ",
        "Новая Зеландия": "NZ"
    }
    
    return country_codes.get(country, "XX")

def create_weight_class_html(weight_class, fighters):
    """Создаем HTML для страницы весовой категории"""
    
    # Определяем чемпиона (первый в списке)
    champion = fighters[0] if fighters else None
    ranked_fighters = fighters[1:8] if len(fighters) > 1 else []
    
    # Генерируем данные для чемпиона
    champion_data = generate_fighter_data(champion, 0) if champion else None
    
    # Генерируем данные для рейтинговых бойцов
    ranked_fighters_data = []
    for i, fighter in enumerate(ranked_fighters):
        ranked_fighters_data.append(generate_fighter_data(fighter, i + 2))
    
    # Определяем цвет флага чемпиона
    champion_country_code = get_country_code(champion_data['country']) if champion_data else "XX"
    
    html_template = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UFC - {weight_class[1]}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .gradient-bg {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .champion-gradient {{
            background: linear-gradient(135deg, #d4af37 0%, #ffd700 50%, #ffed4e 100%);
        }}
        .fighter-card {{
            background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }}
        .fighter-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        }}
        .champion-card {{
            background: linear-gradient(145deg, #ffffff 0%, #fefce8 100%);
            box-shadow: 0 20px 25px -5px rgba(212, 175, 55, 0.3);
            border: 2px solid #fbbf24;
        }}
        .rank-badge {{
            background: linear-gradient(45deg, #3b82f6, #1d4ed8);
            color: white;
            font-weight: bold;
        }}
        .champion-badge {{
            background: linear-gradient(45deg, #d4af37, #ffd700);
            color: #1f2937;
            font-weight: bold;
        }}
        .flag-gradient {{
            background: linear-gradient(45deg, #1e40af, #3b82f6, #60a5fa);
        }}
        .weight-class-header {{
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #60a5fa 100%);
        }}
    </style>
</head>
<body class="bg-gray-100 min-h-screen">
    <!-- Header -->
    <header class="gradient-bg text-white py-6">
        <div class="container mx-auto px-4">
            <div class="flex items-center justify-between">
                <h1 class="text-3xl font-bold">UFC Ranker</h1>
                <nav class="space-x-6">
                    <a href="#" class="hover:text-blue-200 transition-colors">Главная</a>
                    <a href="#" class="hover:text-blue-200 transition-colors">Бойцы</a>
                    <a href="#" class="hover:text-blue-200 transition-colors">Рейтинги</a>
                </nav>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
        <!-- Weight Class Header -->
        <div class="weight-class-header text-white rounded-2xl p-8 mb-8">
            <div class="flex items-center justify-between">
                <div>
                    <h2 class="text-4xl font-bold mb-2">{weight_class[1]}</h2>
                    <p class="text-xl opacity-90 mb-4">{weight_class[2]}</p>
                    <div class="flex items-center space-x-4">
                        <span class="bg-white bg-opacity-20 px-4 py-2 rounded-full text-sm font-semibold">
                            <i class="fas fa-weight mr-2"></i>{weight_class[3]}-{weight_class[4]} lbs
                        </span>
                        <span class="bg-white bg-opacity-20 px-4 py-2 rounded-full text-sm font-semibold">
                            <i class="fas fa-users mr-2"></i>{len(fighters)} бойцов
                        </span>
                    </div>
                </div>
                <div class="text-right">
                    <div class="text-6xl opacity-20">
                        <i class="fas fa-trophy"></i>
                    </div>
                </div>
            </div>
        </div>
"""
    
    # Добавляем секцию чемпиона
    if champion_data:
        html_template += f"""
        <!-- Champion Section -->
        <div class="champion-card rounded-3xl p-8 mb-8">
            <div class="flex items-center justify-center mb-6">
                <div class="champion-badge px-6 py-3 rounded-full text-xl">
                    <i class="fas fa-crown mr-2"></i>ЧЕМПИОН
                </div>
            </div>
            
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <!-- Champion Photo -->
                <div class="lg:col-span-1">
                    <div class="relative">
                        <div class="w-80 h-80 mx-auto bg-gradient-to-br from-yellow-200 to-yellow-300 rounded-2xl flex items-center justify-center">
                            <i class="fas fa-user text-6xl text-yellow-600"></i>
                        </div>
                        <div class="absolute -bottom-4 -right-4 w-20 h-20 champion-gradient rounded-full flex items-center justify-center">
                            <i class="fas fa-crown text-3xl text-gray-800"></i>
                        </div>
                    </div>
                </div>

                <!-- Champion Info -->
                <div class="lg:col-span-2">
                    <div class="text-center lg:text-left">
                        <h3 class="text-4xl font-bold text-gray-900 mb-2">{champion_data['name_ru']}</h3>
                        <p class="text-2xl text-gray-600 mb-4">{champion_data['name_en']}</p>
                        <p class="text-xl text-gray-500 mb-6">"{champion_data['nickname']}"</p>

                        <!-- Champion Stats -->
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div class="bg-white p-6 rounded-xl shadow-lg">
                                <div class="flex items-center space-x-3 mb-4">
                                    <i class="fas fa-trophy text-2xl text-yellow-600"></i>
                                    <h4 class="text-xl font-semibold text-gray-800">Рекорд</h4>
                                </div>
                                <p class="text-3xl font-bold text-gray-900">{champion_data['wins']}-{champion_data['losses']}-{champion_data['draws']}</p>
                                <p class="text-gray-600">Непобежденный</p>
                            </div>

                            <div class="bg-white p-6 rounded-xl shadow-lg">
                                <div class="flex items-center space-x-3 mb-4">
                                    <i class="fas fa-ruler-vertical text-2xl text-blue-600"></i>
                                    <h4 class="text-xl font-semibold text-gray-800">Рост</h4>
                                </div>
                                <p class="text-3xl font-bold text-gray-900">{champion_data['height_inches']//12}'{champion_data['height_inches']%12}"</p>
                                <p class="text-gray-600">{champion_data['height_cm']} см</p>
                            </div>

                            <div class="bg-white p-6 rounded-xl shadow-lg">
                                <div class="flex items-center space-x-3 mb-4">
                                    <i class="fas fa-birthday-cake text-2xl text-green-600"></i>
                                    <h4 class="text-xl font-semibold text-gray-800">Возраст</h4>
                                </div>
                                <p class="text-3xl font-bold text-gray-900">{champion_data['age']}</p>
                                <p class="text-gray-600">лет</p>
                            </div>

                            <div class="bg-white p-6 rounded-xl shadow-lg">
                                <div class="flex items-center space-x-3 mb-4">
                                    <i class="fas fa-expand-arrows-alt text-2xl text-purple-600"></i>
                                    <h4 class="text-xl font-semibold text-gray-800">Размах рук</h4>
                                </div>
                                <p class="text-3xl font-bold text-gray-900">{random.randint(65, 80)}"</p>
                                <p class="text-gray-600">см</p>
                            </div>
                        </div>

                        <!-- Country -->
                        <div class="flex items-center justify-center lg:justify-start mt-6">
                            <div class="flag-gradient w-8 h-6 rounded flex items-center justify-center">
                                <span class="text-white text-sm font-bold">{champion_country_code}</span>
                            </div>
                            <span class="text-lg font-semibold text-gray-700 ml-3">{champion_data['country']}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
"""
    
    # Добавляем секцию рейтинга
    html_template += """
        <!-- Rankings Section -->
        <div class="mb-8">
            <h3 class="text-3xl font-bold text-gray-800 mb-6 flex items-center">
                <i class="fas fa-list-ol text-blue-600 mr-3"></i>
                Рейтинг весовой категории
            </h3>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
"""
    
    # Добавляем карточки бойцов
    for fighter_data in ranked_fighters_data:
        country_code = get_country_code(fighter_data['country'])
        
        html_template += f"""
                <!-- Fighter {fighter_data['rank']} -->
                <div class="fighter-card rounded-xl p-6 cursor-pointer">
                    <div class="text-center">
                        <div class="relative mb-4">
                            <div class="w-32 h-32 mx-auto bg-gradient-to-br from-gray-200 to-gray-300 rounded-xl flex items-center justify-center">
                                <i class="fas fa-user text-4xl text-gray-500"></i>
                            </div>
                            <div class="absolute -top-2 -right-2 w-8 h-8 rank-badge rounded-full flex items-center justify-center text-sm">
                                {fighter_data['rank']}
                            </div>
                        </div>
                        <h4 class="text-lg font-bold text-gray-800 mb-1">{fighter_data['name_ru']}</h4>
                        <p class="text-gray-600 mb-3">{fighter_data['name_en']}</p>
                        <div class="space-y-2">
                            <div class="flex justify-between text-sm">
                                <span class="text-gray-500">Рекорд:</span>
                                <span class="font-semibold">{fighter_data['wins']}-{fighter_data['losses']}-{fighter_data['draws']}</span>
                            </div>
                            <div class="flex justify-between text-sm">
                                <span class="text-gray-500">Рост:</span>
                                <span class="font-semibold">{fighter_data['height_inches']//12}'{fighter_data['height_inches']%12}"</span>
                            </div>
                            <div class="flex justify-between text-sm">
                                <span class="text-gray-500">Страна:</span>
                                <span class="font-semibold">{fighter_data['country']}</span>
                            </div>
                        </div>
                    </div>
                </div>
"""
    
    # Завершаем HTML
    total_wins = sum(f['wins'] for f in fighters)
    total_losses = sum(f['losses'] for f in fighters)
    total_draws = sum(f['draws'] for f in fighters)
    
    html_template += f"""
            </div>
        </div>

        <!-- Statistics Section -->
        <div class="bg-white rounded-2xl p-8 shadow-lg">
            <h3 class="text-2xl font-bold text-gray-800 mb-6">Статистика весовой категории</h3>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div class="text-center">
                    <div class="text-4xl font-bold text-blue-600 mb-2">{len(fighters)}</div>
                    <div class="text-gray-600">Бойцов в рейтинге</div>
                </div>
                <div class="text-center">
                    <div class="text-4xl font-bold text-green-600 mb-2">{total_wins}</div>
                    <div class="text-gray-600">Общих побед</div>
                </div>
                <div class="text-center">
                    <div class="text-4xl font-bold text-red-600 mb-2">{total_losses}</div>
                    <div class="text-gray-600">Общих поражений</div>
                </div>
                <div class="text-center">
                    <div class="text-4xl font-bold text-yellow-600 mb-2">{total_draws}</div>
                    <div class="text-gray-600">Ничьих</div>
                </div>
            </div>
        </div>

        <!-- Back Button -->
        <div class="text-center mt-8">
            <a href="#" class="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                <i class="fas fa-arrow-left mr-2"></i>
                Назад к рейтингам
            </a>
        </div>
    </main>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white py-8 mt-12">
        <div class="container mx-auto px-4 text-center">
            <p>&copy; 2024 UFC Ranker. Все права защищены.</p>
        </div>
    </footer>
</body>
</html>
"""
    
    return html_template

def main():
    """Основная функция"""
    print("🥊 Генерация страниц весовых категорий...")
    
    # Получаем весовые категории
    weight_classes = get_weight_classes()
    print(f"✅ Найдено {len(weight_classes)} весовых категорий")
    
    # Создаем папку для страниц
    os.makedirs('weight_class_pages', exist_ok=True)
    
    # Генерируем страницы для каждой весовой категории
    for weight_class in weight_classes:
        print(f"📝 Генерируем страницу для: {weight_class[1]}")
        
        # Получаем бойцов для этой весовой категории
        fighters = get_fighters_by_weight_class(weight_class[1])
        print(f"   Найдено {len(fighters)} бойцов")
        
        # Создаем HTML
        html_content = create_weight_class_html(weight_class, fighters)
        
        # Сохраняем файл
        filename = f"weight_class_pages/{weight_class[1].replace(' ', '_')}_page.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Создана страница: {filename}")
    
    print(f"\n🎉 Создано {len(weight_classes)} страниц весовых категорий в папке weight_class_pages/")
    print("🌐 Откройте файлы в браузере для просмотра")

if __name__ == "__main__":
    main()
