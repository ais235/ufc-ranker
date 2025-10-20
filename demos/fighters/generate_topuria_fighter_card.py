#!/usr/bin/env python3
"""
Генератор карточки бойца Topuria на основе .odg файла с чёрно-золотой стилистикой
"""

import sqlite3
import logging
from datetime import datetime
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TopuriaFighterCardGenerator:
    def __init__(self, db_path="ufc_ranker_v2.db"):
        self.db_path = db_path
        
    def get_fighter_data(self, fighter_name):
        """Получает данные бойца из базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Ищем бойца по имени (может быть на русском или английском)
        cursor.execute("""
            SELECT name_ru, name_en, nickname, country, height, weight, reach, 
                   age, birth_date, weight_class, wins, losses, draws, 
                   name, birth_place, stance, team, trainer, belt_rank,
                   years_active, current_division, image_url
            FROM fighters 
            WHERE name_ru LIKE ? OR name_en LIKE ? OR name LIKE ?
        """, (f"%{fighter_name}%", f"%{fighter_name}%", f"%{fighter_name}%"))
        
        fighter = cursor.fetchone()
        conn.close()
        
        if fighter:
            return {
                'name_ru': fighter[0] or '',
                'name_en': fighter[1] or '',
                'nickname': fighter[2] or '',
                'country': fighter[3] or '',
                'height': fighter[4] or 0,
                'weight': fighter[5] or 0,
                'reach': fighter[6] or 0,
                'age': fighter[7] or 0,
                'birth_date': fighter[8] or '',
                'weight_class': fighter[9] or '',
                'wins': fighter[10] or 0,
                'losses': fighter[11] or 0,
                'draws': fighter[12] or 0,
                'full_name': fighter[13] or '',
                'birth_place': fighter[14] or '',
                'stance': fighter[15] or '',
                'team': fighter[16] or '',
                'trainer': fighter[17] or '',
                'belt_rank': fighter[18] or '',
                'years_active': fighter[19] or '',
                'current_division': fighter[20] or '',
                'image_url': fighter[21] or ''
            }
        return None
    
    def get_fighter_fights(self, fighter_name, limit=5):
        """Получает последние бои бойца"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT f.event_name, f.fight_date, f.fighter1_name, f.fighter2_name,
                   f.fighter1_record, f.fighter2_record, f.is_win, f.method,
                   f.round, f.time, f.referee, f.weight_class
            FROM fights f
            WHERE f.fighter1_name LIKE ? OR f.fighter2_name LIKE ?
            ORDER BY f.fight_date DESC
            LIMIT ?
        """, (f"%{fighter_name}%", f"%{fighter_name}%", limit))
        
        fights = cursor.fetchall()
        conn.close()
        
        return fights
    
    def get_fighter_rankings(self, fighter_name):
        """Получает рейтинг бойца"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT r.rank_position, r.weight_class
            FROM rankings r
            JOIN fighters f ON r.fighter_id = f.id
            WHERE f.name_ru LIKE ? OR f.name_en LIKE ? OR f.name LIKE ?
            ORDER BY r.updated_at DESC
            LIMIT 1
        """, (f"%{fighter_name}%", f"%{fighter_name}%", f"%{fighter_name}%"))
        
        ranking = cursor.fetchone()
        conn.close()
        
        return ranking
    
    def get_upcoming_events(self, limit=5):
        """Получает предстоящие события"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT event_name, event_date, location
            FROM upcoming_fights
            WHERE event_date >= date('now')
            ORDER BY event_date ASC
            LIMIT ?
        """, (limit,))
        
        events = cursor.fetchall()
        conn.close()
        
        return events
    
    def generate_html(self, fighter_data, fights, ranking, upcoming_events, fighter_name="Topuria"):
        """Генерирует HTML карточку бойца"""
        
        # Определяем имя для отображения
        display_name = fighter_data['name_ru'] or fighter_data['name_en'] or fighter_data['full_name']
        nickname = fighter_data['nickname']
        country = fighter_data['country']
        weight_class = fighter_data['weight_class'] or fighter_data['current_division']
        
        # Физические характеристики
        height = fighter_data['height']
        weight = fighter_data['weight']
        reach = fighter_data['reach']
        age = fighter_data['age']
        
        # Статистика
        wins = fighter_data['wins']
        losses = fighter_data['losses']
        draws = fighter_data['draws']
        
        # Рейтинг
        if ranking and ranking[0]:
            if ranking[0] == 1:
                rank_text = "ЧЕМПИОН"
            else:
                rank_text = f"#{ranking[0]}"
        else:
            rank_text = "Н/Д"
        rank_weight_class = ranking[1] if ranking else ""
        
        # Генерируем HTML
        html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Карточка бойца - {display_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            color: #fff;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        /* Шапка сайта */
        .site-header {{
            background: linear-gradient(135deg, #d4af37 0%, #ffd700 100%);
            color: #000;
            padding: 15px 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(212, 175, 55, 0.3);
        }}
        .site-header h1 {{
            margin: 0;
            font-size: 2em;
            font-weight: bold;
        }}
        
        /* Основная карточка бойца */
        .fighter-main-card {{
            background: rgba(255, 255, 255, 0.1);
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 30px;
            position: relative;
        }}
        
        /* Фото бойца */
        .fighter-photo-section {{
            text-align: center;
        }}
        .fighter-photo {{
            width: 100%;
            max-width: 250px;
            height: 350px;
            object-fit: cover;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        }}
        .photo-placeholder {{
            width: 100%;
            max-width: 250px;
            height: 350px;
            background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2em;
            color: #bdc3c7;
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        }}
        
        /* Правый верхний угол с флагом */
        .country-info {{
            position: absolute;
            top: 25px;
            right: 25px;
            text-align: center;
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        .country-flag {{
            width: 40px;
            height: 30px;
            object-fit: cover;
            border-radius: 5px;
            margin-bottom: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }}
        .country-name {{
            font-size: 1.1em;
            font-weight: bold;
            color: #ffd700;
            margin-bottom: 5px;
        }}
        .birth-place {{
            font-size: 0.9em;
            color: #bdc3c7;
        }}
        
        /* Информация о бойце */
        .fighter-info {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr 1fr;
            gap: 15px;
        }}
        .info-section {{
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-radius: 10px;
        }}
        .fighter-name {{
            font-size: 2.5em;
            font-weight: bold;
            color: #d4af37;
            margin-bottom: 10px;
            grid-column: 1 / -1;
        }}
        .fighter-nickname {{
            font-size: 1.3em;
            font-style: italic;
            color: #bdc3c7;
            margin-bottom: 5px;
            grid-column: 1 / -1;
        }}
        .fighter-rank {{
            font-size: 1.1em;
            font-weight: bold;
            color: #d4af37;
            margin-top: 15px;
            text-align: center;
            background: rgba(212, 175, 55, 0.1);
            padding: 5px 10px;
            border-radius: 5px;
            border: 1px solid #d4af37;
        }}
        .info-label {{
            font-size: 0.9em;
            color: #bdc3c7;
            margin-bottom: 5px;
        }}
        .info-value {{
            font-size: 1.1em;
            font-weight: bold;
            color: #ffd700;
            margin-bottom: 15px;
        }}
        
        /* Статистика побед/поражений */
        .stats-section {{
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .stats-title {{
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 15px;
            color: #d4af37;
            text-align: center;
            border-bottom: 1px solid #d4af37;
            padding-bottom: 5px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
        }}
        .stat-card {{
            background: rgba(255, 255, 255, 0.05);
            padding: 12px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #ffd700;
            margin-bottom: 8px;
        }}
        .stat-label {{
            font-size: 0.9em;
            color: #bdc3c7;
            margin-bottom: 10px;
        }}
        .stat-breakdown {{
            font-size: 0.9em;
            color: #95a5a6;
        }}
        
        /* Подсветка побед и поражений */
        .stat-card.wins {{
            border: 2px solid #27ae60;
            background: rgba(39, 174, 96, 0.1);
        }}
        .stat-card.losses {{
            border: 2px solid #e74c3c;
            background: rgba(231, 76, 60, 0.1);
        }}
        .stat-card.draws {{
            border: 2px solid #f39c12;
            background: rgba(243, 156, 18, 0.1);
        }}
        
        /* Стили для возраста */
        .age-large {{
            font-size: 1.5em;
            font-weight: bold;
            color: #ffd700;
            margin-bottom: 5px;
        }}
        .birth-date {{
            font-size: 1.1em;
            color: #bdc3c7;
            margin-bottom: 15px;
        }}
        
        /* Стили для четвертой колонки с результатами */
        .results-section {{
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }}
        .result-item {{
            margin-bottom: 15px;
        }}
        .result-value {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
            padding: 10px;
            border-radius: 8px;
        }}
        .result-value.wins {{
            color: #27ae60;
            background: rgba(39, 174, 96, 0.1);
            border: 2px solid #27ae60;
        }}
        .result-value.losses {{
            color: #e74c3c;
            background: rgba(231, 76, 60, 0.1);
            border: 2px solid #e74c3c;
        }}
        .result-value.draws {{
            color: #f39c12;
            background: rgba(243, 156, 18, 0.1);
            border: 2px solid #f39c12;
        }}
        .result-label {{
            font-size: 0.9em;
            color: #bdc3c7;
        }}
        
        /* Последние бои */
        .fights-section {{
            background: rgba(255, 255, 255, 0.1);
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        .fights-title {{
            font-size: 1.8em;
            font-weight: bold;
            margin-bottom: 20px;
            color: #d4af37;
            text-align: center;
            border-bottom: 2px solid #d4af37;
            padding-bottom: 10px;
        }}
        .fight-card {{
            background: rgba(255, 255, 255, 0.05);
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 10px;
            border-left: 8px solid #d4af37;
            display: grid;
            grid-template-columns: auto 1fr auto;
            gap: 20px;
            align-items: center;
        }}
        .fight-card.win {{
            border-left-color: #27ae60;
        }}
        .fight-card.loss {{
            border-left-color: #e74c3c;
        }}
        .fight-method {{
            text-align: center;
            width: 120px;
            flex-shrink: 0;
        }}
        .fight-method-text {{
            font-size: 1.1em;
            font-weight: bold;
            color: #ffd700;
            margin-bottom: 5px;
            word-wrap: break-word;
            word-break: break-word;
            white-space: normal;
        }}
        .fight-round {{
            font-size: 0.9em;
            color: #bdc3c7;
            margin-bottom: 3px;
        }}
        .fight-time {{
            font-size: 0.9em;
            color: #bdc3c7;
        }}
        .fight-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        .fight-event {{
            font-weight: bold;
            font-size: 1.1em;
        }}
        .fight-date {{
            color: #bdc3c7;
            font-size: 0.9em;
        }}
        .fighters-info {{
            display: flex;
            align-items: center;
            gap: 15px;
            flex: 1;
        }}
        .fighter-photos {{
            display: flex;
            gap: 10px;
            justify-content: center;
        }}
        .fighter-photo-small {{
            width: 60px;
            height: 100%;
            min-height: 120px;
            object-fit: cover;
            border-radius: 5px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }}
        .fighter-photo-placeholder {{
            width: 60px;
            height: 100%;
            min-height: 120px;
            background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
            border-radius: 5px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.7em;
            color: #bdc3c7;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }}
        .fighter-info-small {{
            text-align: center;
        }}
        .fighter-name-small {{
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 5px;
        }}
        .fighter-record {{
            color: #bdc3c7;
            font-size: 0.9em;
            margin-bottom: 5px;
        }}
        .fighter-streak {{
            color: #95a5a6;
            font-size: 0.8em;
        }}
        .vs-text {{
            font-size: 1.5em;
            font-weight: bold;
            color: #d4af37;
        }}
        .fight-details {{
            text-align: right;
            width: 150px;
            flex-shrink: 0;
        }}
        .fight-detail-item {{
            margin-bottom: 8px;
        }}
        .fight-detail-label {{
            font-size: 0.8em;
            color: #bdc3c7;
            margin-bottom: 2px;
        }}
        .fight-detail-value {{
            font-size: 0.9em;
            color: #ffd700;
            font-weight: bold;
        }}
        .fight-result {{
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .result-text {{
            font-weight: bold;
            font-size: 1.2em;
            margin-bottom: 5px;
        }}
        .result-details {{
            color: #bdc3c7;
            font-size: 0.9em;
        }}
        .result-win {{ color: #27ae60; }}
        .result-loss {{ color: #e74c3c; }}
        .result-draw {{ color: #f39c12; }}
        
        /* Турниры */
        .tournaments-section {{
            background: rgba(255, 255, 255, 0.1);
            padding: 25px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        .tournaments-title {{
            font-size: 1.8em;
            font-weight: bold;
            margin-bottom: 20px;
            color: #d4af37;
            text-align: center;
            border-bottom: 2px solid #d4af37;
            padding-bottom: 10px;
        }}
        .tournament-item {{
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .tournament-date {{
            font-weight: bold;
            color: #ffd700;
            min-width: 80px;
        }}
        .tournament-name {{
            color: #bdc3c7;
            flex: 1;
            margin-left: 15px;
        }}
        
        @media (max-width: 768px) {{
            .fighter-main-card {{
                grid-template-columns: 1fr;
            }}
            .fighter-info {{
                grid-template-columns: 1fr;
            }}
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
            .fighters-info {{
                grid-template-columns: 1fr;
                gap: 10px;
            }}
            .vs-text {{
                order: -1;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Шапка сайта -->
        <div class="site-header">
            <h1>🥊 UFC RANKER - Карточка бойца</h1>
        </div>
        
        <!-- Основная карточка бойца -->
        <div class="fighter-main-card">
            <!-- Правый верхний угол с флагом -->
            <div class="country-info">
                <img src="https://flagcdn.com/w40/{country.lower().replace(' ', '-')}.png" alt="{country}" class="country-flag" onerror="this.style.display='none';">
                <div class="country-name">{country}</div>
                <div class="birth-place">{fighter_data['birth_place']}</div>
            </div>
            
            <div class="fighter-photo-section">
                <img src="Topuria.jpg" alt="{display_name}" class="fighter-photo" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                <div class="photo-placeholder" style="display: none;">Фото недоступно</div>
                <div class="fighter-rank">{rank_text}</div>
            </div>
            
            <div class="fighter-info">
                <div class="fighter-name">{display_name}</div>
                <div class="fighter-nickname">"{nickname}"</div>
                
                <!-- Первая колонка: Возраст, весовая, стиль -->
                <div class="info-section">
                    <div class="age-large">{age}</div>
                    <div class="birth-date">{fighter_data['birth_date']}</div>
                    <div class="info-label">Весовая категория</div>
                    <div class="info-value">{weight_class}</div>
                    <div class="info-label">Базовый стиль</div>
                    <div class="info-value">{fighter_data['stance']}</div>
                </div>
                
                <!-- Вторая колонка: Рост, вес, размах -->
                <div class="info-section">
                    <div class="info-label">Рост</div>
                    <div class="info-value">{height} см</div>
                    <div class="info-label">Вес</div>
                    <div class="info-value">{weight} кг</div>
                    <div class="info-label">Размах рук</div>
                    <div class="info-value">{reach} см</div>
                </div>
                
                <!-- Третья колонка: Стойка, команда, степень -->
                <div class="info-section">
                    <div class="info-label">Основная стойка</div>
                    <div class="info-value">{fighter_data['stance']}</div>
                    <div class="info-label">Команда</div>
                    <div class="info-value">{fighter_data['team']}</div>
                    <div class="info-label">Степень мастерства</div>
                    <div class="info-value">{fighter_data['belt_rank']}</div>
                </div>
                
                <!-- Четвертая колонка: Результаты в рамках -->
                <div class="results-section">
                    <div class="result-item">
                        <div class="result-value wins">{wins}</div>
                        <div class="result-label">Побед</div>
                    </div>
                    <div class="result-item">
                        <div class="result-value losses">{losses}</div>
                        <div class="result-label">Поражений</div>
                    </div>
                    <div class="result-item">
                        <div class="result-value draws">{draws}</div>
                        <div class="result-label">Ничьих</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Последние бои -->
        <div class="fights-section">
            <div class="fights-title">🥊 Последние бои</div>"""
        
        # Добавляем информацию о боях
        for fight in fights:
            event_name, fight_date, fighter1, fighter2, record1, record2, is_win, method, round_num, time, referee, weight_class = fight
            
            # Определяем результат для текущего бойца
            if fighter1 and fighter_name.lower() in fighter1.lower():
                result_class = "win" if is_win else "loss"
                result_text = "Победа" if is_win else "Поражение"
            elif fighter2 and fighter_name.lower() in fighter2.lower():
                result_class = "win" if is_win else "loss"
                result_text = "Победа" if is_win else "Поражение"
            else:
                result_class = "draw"
                result_text = "Ничья"
            
            html_content += f"""
            <div class="fight-card {result_class}">
                <!-- Левая часть: метод победы -->
                <div class="fight-method">
                    <div class="fight-method-text">{method or 'N/A'}</div>
                    <div class="fight-round">{round_num or 'N/A'} раунд</div>
                    <div class="fight-time">{time or 'N/A'}</div>
                </div>
                
                <!-- Центральная часть: фото и информация о бойцах -->
                <div class="fighters-info">
                    <div class="fighter-photos">
                        <img src="fighter1.jpg" alt="{fighter1 or 'N/A'}" class="fighter-photo-small" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                        <div class="fighter-photo-placeholder" style="display: none;">Фото</div>
                        <img src="fighter2.jpg" alt="{fighter2 or 'N/A'}" class="fighter-photo-small" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                        <div class="fighter-photo-placeholder" style="display: none;">Фото</div>
                    </div>
                    <div class="fighter-info-small">
                        <div class="fighter-name-small">{fighter1 or 'N/A'}</div>
                        <div class="fighter-record">{record1 or 'N/A'}</div>
                        <div class="fighter-streak">Серия: {record1 or 'N/A'}</div>
                    </div>
                    <div class="fighter-info-small">
                        <div class="fighter-name-small">{fighter2 or 'N/A'}</div>
                        <div class="fighter-record">{record2 or 'N/A'}</div>
                        <div class="fighter-streak">Серия: {record2 or 'N/A'}</div>
                    </div>
                </div>
                
                <!-- Правая часть: дата, событие, судья -->
                <div class="fight-details">
                    <div class="fight-detail-item">
                        <div class="fight-detail-label">Дата боя</div>
                        <div class="fight-detail-value">{fight_date or 'N/A'}</div>
                    </div>
                    <div class="fight-detail-item">
                        <div class="fight-detail-label">Событие</div>
                        <div class="fight-detail-value">{event_name or 'N/A'}</div>
                    </div>
                    <div class="fight-detail-item">
                        <div class="fight-detail-label">Судья</div>
                        <div class="fight-detail-value">{referee or 'N/A'}</div>
                    </div>
                </div>
            </div>"""
        
        html_content += """
        </div>
        
        <!-- Турниры -->
        <div class="tournaments-section">
            <div class="tournaments-title">📅 Предстоящие турниры</div>"""
        
        # Добавляем предстоящие события
        for event in upcoming_events:
            event_name, event_date, location = event
            html_content += f"""
            <div class="tournament-item">
                <div class="tournament-date">{event_date}</div>
                <div class="tournament-name">{event_name} - {location}</div>
            </div>"""
        
        html_content += """
        </div>
    </div>
</body>
</html>"""
        
        return html_content
    
    def generate_card(self, fighter_name="Topuria"):
        """Генерирует карточку бойца"""
        logger.info(f"Генерация карточки для бойца: {fighter_name}")
        
        # Получаем данные
        fighter_data = self.get_fighter_data(fighter_name)
        if not fighter_data:
            logger.error(f"Боец {fighter_name} не найден в базе данных")
            return None
        
        fights = self.get_fighter_fights(fighter_name)
        ranking = self.get_fighter_rankings(fighter_name)
        upcoming_events = self.get_upcoming_events()
        
        # Генерируем HTML
        html_content = self.generate_html(fighter_data, fights, ranking, upcoming_events, fighter_name)
        
        # Сохраняем файл
        filename = f"topuria_fighter_card.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Карточка сохранена как {filename}")
        return filename

if __name__ == "__main__":
    generator = TopuriaFighterCardGenerator()
    generator.generate_card("Topuria")
