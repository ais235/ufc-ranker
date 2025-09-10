#!/usr/bin/env python3
"""
Генерация данных бойца из базы данных для карточки
"""

import sqlite3
import json
from datetime import datetime, date
import random

def get_fighter_data(fighter_name="Ислам Махачев"):
    """Получаем данные бойца из БД"""
    conn = sqlite3.connect('ufc_ranker_v2.db')
    cursor = conn.cursor()
    
    # Ищем бойца в нашей БД
    cursor.execute("""
        SELECT id, name_ru, name_en, country, weight_class, win, lose, draw
        FROM fighters 
        WHERE name_ru LIKE ? OR name_en LIKE ?
    """, (f"%{fighter_name}%", f"%{fighter_name}%"))
    
    fighter = cursor.fetchone()
    
    if not fighter:
        # Если не найден в нашей БД, ищем в ufc_stats
        cursor.execute("""
            SELECT id, name, total_fights, total_wins, total_losses, total_draws
            FROM ufc_stats_fighters 
            WHERE name LIKE ?
        """, (f"%{fighter_name}%",))
        
        ufc_fighter = cursor.fetchone()
        if ufc_fighter:
            fighter = (ufc_fighter[0], ufc_fighter[1], ufc_fighter[1], "Россия", "Легкий вес", 
                      ufc_fighter[3], ufc_fighter[4], ufc_fighter[5])
    
    conn.close()
    
    if not fighter:
        return None
    
    # Генерируем дополнительные данные для тестирования
    fighter_data = {
        "id": fighter[0],
        "name_ru": fighter[1],
        "name_en": fighter[2] if fighter[2] else fighter[1],
        "nickname": generate_nickname(fighter[1]),
        "country": fighter[3] if fighter[3] else "Россия",
        "age": random.randint(25, 35),
        "birth_date": generate_birth_date(),
        "height_inches": random.randint(65, 78),
        "height_cm": 0,
        "reach_inches": random.randint(65, 80),
        "reach_cm": 0,
        "weight_class": fighter[4] if fighter[4] else "Легкий вес",
        "weight_lbs": random.randint(145, 170),
        "weight_kg": 0,
        "wins": fighter[5] if fighter[5] else random.randint(15, 30),
        "losses": fighter[6] if fighter[6] else random.randint(0, 5),
        "draws": fighter[7] if fighter[7] else random.randint(0, 2),
        "ko_wins": random.randint(2, 8),
        "sub_wins": random.randint(5, 15),
        "recent_fights": generate_recent_fights(),
        "stats": generate_fighter_stats()
    }
    
    # Конвертируем единицы измерения
    fighter_data["height_cm"] = int(fighter_data["height_inches"] * 2.54)
    fighter_data["reach_cm"] = int(fighter_data["reach_inches"] * 2.54)
    fighter_data["weight_kg"] = round(fighter_data["weight_lbs"] * 0.453592, 1)
    
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
        "Джон": "Bones"
    }
    
    for key, nickname in nicknames.items():
        if key in name:
            return nickname
    
    return "The Fighter"

def generate_birth_date():
    """Генерируем дату рождения"""
    year = random.randint(1985, 1995)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{day:02d}.{month:02d}.{year}"

def generate_recent_fights():
    """Генерируем последние бои"""
    opponents = [
        "Александр Волкановски", "Чарльз Оливейра", "Бобби Грин", 
        "Дэн Хукер", "Дрю Добер", "Тиагу Мойзес"
    ]
    
    events = [
        "UFC 294", "UFC 280", "UFC Vegas 49", 
        "UFC 257", "UFC 242", "UFC 229"
    ]
    
    dates = [
        "21 октября 2023", "22 октября 2022", "26 февраля 2022",
        "23 января 2021", "7 сентября 2019", "6 октября 2018"
    ]
    
    results = ["Победа", "Победа", "Победа", "Победа", "Победа", "Поражение"]
    rounds = ["1-й раунд, 3:06", "2-й раунд, 3:16", "1-й раунд, 3:23", 
             "2-й раунд, 2:32", "3-й раунд, 4:12", "3-й раунд, 5:00"]
    
    fights = []
    for i in range(3):
        fights.append({
            "opponent": opponents[i],
            "event": events[i],
            "date": dates[i],
            "result": results[i],
            "round": rounds[i]
        })
    
    return fights

def generate_fighter_stats():
    """Генерируем статистику бойца"""
    return {
        "striking_accuracy": random.randint(65, 80),
        "strikes_per_minute": round(random.uniform(3.5, 5.5), 1),
        "defense": random.randint(60, 75),
        "takedowns_per_15min": round(random.uniform(2.5, 4.5), 1),
        "takedown_accuracy": random.randint(45, 70),
        "submission_attempts": random.randint(0, 3)
    }

def create_fighter_html(fighter_data):
    """Создаем HTML для карточки бойца"""
    
    html_template = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{fighter_data['name_ru']} - Карточка бойца</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .gradient-bg {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .fighter-card {{
            background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }}
        .stat-card {{
            background: linear-gradient(145deg, #f1f5f9 0%, #e2e8f0 100%);
            transition: all 0.3s ease;
        }}
        .stat-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }}
        .flag-gradient {{
            background: linear-gradient(45deg, #1e40af, #3b82f6, #60a5fa);
        }}
        .weight-class-badge {{
            background: linear-gradient(45deg, #dc2626, #ef4444, #f87171);
        }}
        .record-badge {{
            background: linear-gradient(45deg, #059669, #10b981, #34d399);
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
        <!-- Fighter Card -->
        <div class="fighter-card rounded-3xl p-8 mb-8">
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <!-- Left Column - Photo and Basic Info -->
                <div class="lg:col-span-1">
                    <!-- Fighter Photo -->
                    <div class="relative mb-6">
                        <div class="w-80 h-80 mx-auto bg-gradient-to-br from-gray-200 to-gray-300 rounded-2xl flex items-center justify-center">
                            <i class="fas fa-user text-6xl text-gray-500"></i>
                        </div>
                        <div class="absolute -bottom-4 -right-4 w-16 h-16 bg-yellow-400 rounded-full flex items-center justify-center">
                            <span class="text-2xl font-bold text-white">#{random.randint(1, 15)}</span>
                        </div>
                    </div>

                    <!-- Basic Info -->
                    <div class="space-y-4">
                        <div class="text-center">
                            <h2 class="text-3xl font-bold text-gray-900 mb-2">{fighter_data['name_ru']}</h2>
                            <p class="text-xl text-gray-600 mb-1">{fighter_data['name_en']}</p>
                            <p class="text-lg text-gray-500">"{fighter_data['nickname']}"</p>
                        </div>

                        <!-- Country -->
                        <div class="flex items-center justify-center space-x-2">
                            <div class="flag-gradient w-8 h-6 rounded flex items-center justify-center">
                                <span class="text-white text-sm font-bold">RU</span>
                            </div>
                            <span class="text-lg font-semibold text-gray-700">{fighter_data['country']}</span>
                        </div>

                        <!-- Weight Class -->
                        <div class="text-center">
                            <span class="weight-class-badge text-white px-4 py-2 rounded-full text-lg font-semibold">
                                {fighter_data['weight_class']} ({fighter_data['weight_lbs']} lbs)
                            </span>
                        </div>
                    </div>
                </div>

                <!-- Right Column - Detailed Stats -->
                <div class="lg:col-span-2">
                    <!-- Personal Info -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                        <div class="stat-card p-6 rounded-xl">
                            <div class="flex items-center space-x-3 mb-4">
                                <i class="fas fa-birthday-cake text-2xl text-blue-600"></i>
                                <h3 class="text-xl font-semibold text-gray-800">Возраст</h3>
                            </div>
                            <p class="text-3xl font-bold text-gray-900">{fighter_data['age']} лет</p>
                            <p class="text-gray-600">{fighter_data['birth_date']}</p>
                        </div>

                        <div class="stat-card p-6 rounded-xl">
                            <div class="flex items-center space-x-3 mb-4">
                                <i class="fas fa-ruler-vertical text-2xl text-green-600"></i>
                                <h3 class="text-xl font-semibold text-gray-800">Рост</h3>
                            </div>
                            <p class="text-3xl font-bold text-gray-900">{fighter_data['height_inches']//12}'{fighter_data['height_inches']%12}"</p>
                            <p class="text-gray-600">{fighter_data['height_cm']} см</p>
                        </div>

                        <div class="stat-card p-6 rounded-xl">
                            <div class="flex items-center space-x-3 mb-4">
                                <i class="fas fa-expand-arrows-alt text-2xl text-purple-600"></i>
                                <h3 class="text-xl font-semibold text-gray-800">Размах рук</h3>
                            </div>
                            <p class="text-3xl font-bold text-gray-900">{fighter_data['reach_inches']}"</p>
                            <p class="text-gray-600">{fighter_data['reach_cm']} см</p>
                        </div>

                        <div class="stat-card p-6 rounded-xl">
                            <div class="flex items-center space-x-3 mb-4">
                                <i class="fas fa-weight text-2xl text-red-600"></i>
                                <h3 class="text-xl font-semibold text-gray-800">Вес</h3>
                            </div>
                            <p class="text-3xl font-bold text-gray-900">{fighter_data['weight_lbs']} lbs</p>
                            <p class="text-gray-600">{fighter_data['weight_kg']} кг</p>
                        </div>
                    </div>

                    <!-- Fight Record -->
                    <div class="mb-8">
                        <h3 class="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                            <i class="fas fa-trophy text-yellow-500 mr-3"></i>
                            Боевой рекорд
                        </h3>
                        
                        <div class="grid grid-cols-3 gap-4">
                            <div class="text-center p-6 bg-green-100 rounded-xl">
                                <div class="text-4xl font-bold text-green-600 mb-2">{fighter_data['wins']}</div>
                                <div class="text-lg font-semibold text-green-800">Побед</div>
                                <div class="text-sm text-green-600 mt-1">
                                    <span class="record-badge text-white px-2 py-1 rounded text-xs">{fighter_data['ko_wins']} KO</span>
                                    <span class="record-badge text-white px-2 py-1 rounded text-xs ml-1">{fighter_data['sub_wins']} SUB</span>
                                </div>
                            </div>
                            
                            <div class="text-center p-6 bg-gray-100 rounded-xl">
                                <div class="text-4xl font-bold text-gray-600 mb-2">{fighter_data['losses']}</div>
                                <div class="text-lg font-semibold text-gray-800">Поражений</div>
                                <div class="text-sm text-gray-600 mt-1">{random.randint(0, fighter_data['losses'])} KO</div>
                            </div>
                            
                            <div class="text-center p-6 bg-blue-100 rounded-xl">
                                <div class="text-4xl font-bold text-blue-600 mb-2">{fighter_data['draws']}</div>
                                <div class="text-lg font-semibold text-blue-800">Ничьих</div>
                                <div class="text-sm text-blue-600 mt-1">-</div>
                            </div>
                        </div>
                    </div>

                    <!-- Recent Fights -->
                    <div>
                        <h3 class="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                            <i class="fas fa-fist-raised text-red-500 mr-3"></i>
                            Последние бои
                        </h3>
                        
                        <div class="space-y-4">
"""
    
    # Добавляем последние бои
    for fight in fighter_data['recent_fights']:
        result_color = "green" if fight['result'] == "Победа" else "red"
        result_bg = "green-100" if fight['result'] == "Победа" else "red-100"
        result_text = "green-800" if fight['result'] == "Победа" else "red-800"
        border_color = "green-500" if fight['result'] == "Победа" else "red-500"
        
        html_template += f"""
                            <div class="bg-white p-4 rounded-lg border-l-4 border-{border_color}">
                                <div class="flex justify-between items-center">
                                    <div>
                                        <p class="font-semibold text-gray-800">vs {fight['opponent']}</p>
                                        <p class="text-sm text-gray-600">{fight['event']} • {fight['date']}</p>
                                    </div>
                                    <div class="text-right">
                                        <span class="bg-{result_bg} text-{result_text} px-3 py-1 rounded-full text-sm font-semibold">{fight['result']}</span>
                                        <p class="text-sm text-gray-600 mt-1">{fight['round']}</p>
                                    </div>
                                </div>
                            </div>
"""
    
    html_template += """
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Statistics Section -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div class="stat-card p-6 rounded-xl text-center">
                <i class="fas fa-bullseye text-3xl text-blue-600 mb-4"></i>
                <h4 class="text-lg font-semibold text-gray-800 mb-2">Точность ударов</h4>
                <p class="text-3xl font-bold text-gray-900">""" + str(fighter_data['stats']['striking_accuracy']) + """%</p>
            </div>
            
            <div class="stat-card p-6 rounded-xl text-center">
                <i class="fas fa-fist-raised text-3xl text-red-600 mb-4"></i>
                <h4 class="text-lg font-semibold text-gray-800 mb-2">Ударов в минуту</h4>
                <p class="text-3xl font-bold text-gray-900">""" + str(fighter_data['stats']['strikes_per_minute']) + """</p>
            </div>
            
            <div class="stat-card p-6 rounded-xl text-center">
                <i class="fas fa-shield-alt text-3xl text-green-600 mb-4"></i>
                <h4 class="text-lg font-semibold text-gray-800 mb-2">Защита</h4>
                <p class="text-3xl font-bold text-gray-900">""" + str(fighter_data['stats']['defense']) + """%</p>
            </div>
            
            <div class="stat-card p-6 rounded-xl text-center">
                <i class="fas fa-wrestling text-3xl text-purple-600 mb-4"></i>
                <h4 class="text-lg font-semibold text-gray-800 mb-2">Тейкдауны</h4>
                <p class="text-3xl font-bold text-gray-900">""" + str(fighter_data['stats']['takedowns_per_15min']) + """</p>
            </div>
        </div>

        <!-- Back Button -->
        <div class="text-center">
            <a href="#" class="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                <i class="fas fa-arrow-left mr-2"></i>
                Назад к списку бойцов
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
    print("🥊 Генерация карточки бойца...")
    
    # Получаем данные бойца
    fighter_data = get_fighter_data("Ислам Махачев")
    
    if not fighter_data:
        print("❌ Боец не найден в базе данных")
        return
    
    print(f"✅ Найден боец: {fighter_data['name_ru']}")
    print(f"📊 Рекорд: {fighter_data['wins']}-{fighter_data['losses']}-{fighter_data['draws']}")
    
    # Создаем HTML
    html_content = create_fighter_html(fighter_data)
    
    # Сохраняем в файл
    with open('fighter_card_generated.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ HTML карточка создана: fighter_card_generated.html")
    print("🌐 Откройте файл в браузере для просмотра")

if __name__ == "__main__":
    main()
