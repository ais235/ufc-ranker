#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Обновление страницы тяжелого веса с детальной статистикой
"""

import sqlite3
import sys
import codecs
from datetime import datetime

def get_heavyweight_rankings_with_detailed_stats():
    """Получает рейтинги тяжелого веса с детальной статистикой"""
    
    # Настройка кодировки для Windows
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    
    try:
        conn = sqlite3.connect("ufc_ranker_v2.db")
        cursor = conn.cursor()
        
        # Получаем рейтинги тяжелого веса с детальной статистикой
        cursor.execute("""
            SELECT 
                f.id,
                f.name_ru,
                f.name_en,
                f.nickname,
                f.country,
                f.country_flag_url,
                f.image_url,
                f.height,
                f.weight,
                f.reach,
                f.age,
                f.birth_date,
                f.full_name,
                f.birth_place,
                f.stance,
                f.team,
                f.trainer,
                f.belt_rank,
                f.years_active,
                f.current_division,
                f.fighting_out_of,
                r.rank_position,
                r.is_champion,
                fr.wins,
                fr.losses,
                fr.draws,
                fr.no_contests,
                fr.wins_by_ko,
                fr.losses_by_ko,
                fr.wins_by_submission,
                fr.losses_by_submission,
                fr.wins_by_decision,
                fr.losses_by_decision,
                fr.avg_fight_time_seconds,
                fr.total_fights
            FROM rankings r
            JOIN fighters f ON r.fighter_id = f.id
            LEFT JOIN fight_records fr ON f.id = fr.fighter_id
            WHERE r.weight_class_id = (
                SELECT id FROM weight_classes WHERE name_en = 'Heavyweights'
            )
            ORDER BY r.rank_position ASC
            LIMIT 15
        """)
        
        fighters = cursor.fetchall()
        conn.close()
        
        return fighters
        
    except Exception as e:
        print(f"❌ Ошибка при получении данных: {e}")
        return []

def get_country_flag_url(country):
    """Получает URL флага страны"""
    country_flags = {
        'United States': 'https://flagcdn.com/w20/us.png',
        'Russia': 'https://flagcdn.com/w20/ru.png',
        'Poland': 'https://flagcdn.com/w20/pl.png',
        'Australia': 'https://flagcdn.com/w20/au.png',
        'Brazil': 'https://flagcdn.com/w20/br.png',
        'England': 'https://flagcdn.com/w20/gb.png',
        'Great Britain': 'https://flagcdn.com/w20/gb.png',
        'United Kingdom': 'https://flagcdn.com/w20/gb.png',
        'France': 'https://flagcdn.com/w20/fr.png',
        'Germany': 'https://flagcdn.com/w20/de.png',
        'Canada': 'https://flagcdn.com/w20/ca.png',
        'Ukraine': 'https://flagcdn.com/w20/ua.png',
        'Georgia': 'https://flagcdn.com/w20/ge.png',
        'Armenia': 'https://flagcdn.com/w20/am.png',
        'Kazakhstan': 'https://flagcdn.com/w20/kz.png',
        'Uzbekistan': 'https://flagcdn.com/w20/uz.png',
        'Azerbaijan': 'https://flagcdn.com/w20/az.png',
        'Moldova': 'https://flagcdn.com/w20/md.png',
        'Belarus': 'https://flagcdn.com/w20/by.png',
        'Lithuania': 'https://flagcdn.com/w20/lt.png',
        'Latvia': 'https://flagcdn.com/w20/lv.png',
        'Estonia': 'https://flagcdn.com/w20/ee.png',
        'Finland': 'https://flagcdn.com/w20/fi.png',
        'Sweden': 'https://flagcdn.com/w20/se.png',
        'Norway': 'https://flagcdn.com/w20/no.png',
        'Denmark': 'https://flagcdn.com/w20/dk.png',
        'Netherlands': 'https://flagcdn.com/w20/nl.png',
        'Belgium': 'https://flagcdn.com/w20/be.png',
        'Switzerland': 'https://flagcdn.com/w20/ch.png',
        'Austria': 'https://flagcdn.com/w20/at.png',
        'Italy': 'https://flagcdn.com/w20/it.png',
        'Spain': 'https://flagcdn.com/w20/es.png',
        'Portugal': 'https://flagcdn.com/w20/pt.png',
        'Greece': 'https://flagcdn.com/w20/gr.png',
        'Turkey': 'https://flagcdn.com/w20/tr.png',
        'Israel': 'https://flagcdn.com/w20/il.png',
        'Lebanon': 'https://flagcdn.com/w20/lb.png',
        'Jordan': 'https://flagcdn.com/w20/jo.png',
        'Saudi Arabia': 'https://flagcdn.com/w20/sa.png',
        'United Arab Emirates': 'https://flagcdn.com/w20/ae.png',
        'Qatar': 'https://flagcdn.com/w20/qa.png',
        'Kuwait': 'https://flagcdn.com/w20/kw.png',
        'Bahrain': 'https://flagcdn.com/w20/bh.png',
        'Oman': 'https://flagcdn.com/w20/om.png',
        'Yemen': 'https://flagcdn.com/w20/ye.png',
        'Iraq': 'https://flagcdn.com/w20/iq.png',
        'Iran': 'https://flagcdn.com/w20/ir.png',
        'Afghanistan': 'https://flagcdn.com/w20/af.png',
        'Pakistan': 'https://flagcdn.com/w20/pk.png',
        'India': 'https://flagcdn.com/w20/in.png',
        'Bangladesh': 'https://flagcdn.com/w20/bd.png',
        'Sri Lanka': 'https://flagcdn.com/w20/lk.png',
        'Nepal': 'https://flagcdn.com/w20/np.png',
        'Bhutan': 'https://flagcdn.com/w20/bt.png',
        'Maldives': 'https://flagcdn.com/w20/mv.png',
        'China': 'https://flagcdn.com/w20/cn.png',
        'Japan': 'https://flagcdn.com/w20/jp.png',
        'South Korea': 'https://flagcdn.com/w20/kr.png',
        'North Korea': 'https://flagcdn.com/w20/kp.png',
        'Mongolia': 'https://flagcdn.com/w20/mn.png',
        'Taiwan': 'https://flagcdn.com/w20/tw.png',
        'Hong Kong': 'https://flagcdn.com/w20/hk.png',
        'Macau': 'https://flagcdn.com/w20/mo.png',
        'Vietnam': 'https://flagcdn.com/w20/vn.png',
        'Laos': 'https://flagcdn.com/w20/la.png',
        'Cambodia': 'https://flagcdn.com/w20/kh.png',
        'Thailand': 'https://flagcdn.com/w20/th.png',
        'Myanmar': 'https://flagcdn.com/w20/mm.png',
        'Malaysia': 'https://flagcdn.com/w20/my.png',
        'Singapore': 'https://flagcdn.com/w20/sg.png',
        'Indonesia': 'https://flagcdn.com/w20/id.png',
        'Philippines': 'https://flagcdn.com/w20/ph.png',
        'Brunei': 'https://flagcdn.com/w20/bn.png',
        'East Timor': 'https://flagcdn.com/w20/tl.png',
        'Papua New Guinea': 'https://flagcdn.com/w20/pg.png',
        'Fiji': 'https://flagcdn.com/w20/fj.png',
        'Samoa': 'https://flagcdn.com/w20/ws.png',
        'Tonga': 'https://flagcdn.com/w20/to.png',
        'Vanuatu': 'https://flagcdn.com/w20/vu.png',
        'Solomon Islands': 'https://flagcdn.com/w20/sb.png',
        'New Zealand': 'https://flagcdn.com/w20/nz.png',
        'Mexico': 'https://flagcdn.com/w20/mx.png',
        'Guatemala': 'https://flagcdn.com/w20/gt.png',
        'Belize': 'https://flagcdn.com/w20/bz.png',
        'El Salvador': 'https://flagcdn.com/w20/sv.png',
        'Honduras': 'https://flagcdn.com/w20/hn.png',
        'Nicaragua': 'https://flagcdn.com/w20/ni.png',
        'Costa Rica': 'https://flagcdn.com/w20/cr.png',
        'Panama': 'https://flagcdn.com/w20/pa.png',
        'Cuba': 'https://flagcdn.com/w20/cu.png',
        'Jamaica': 'https://flagcdn.com/w20/jm.png',
        'Haiti': 'https://flagcdn.com/w20/ht.png',
        'Dominican Republic': 'https://flagcdn.com/w20/do.png',
        'Puerto Rico': 'https://flagcdn.com/w20/pr.png',
        'Trinidad and Tobago': 'https://flagcdn.com/w20/tt.png',
        'Barbados': 'https://flagcdn.com/w20/bb.png',
        'Saint Lucia': 'https://flagcdn.com/w20/lc.png',
        'Saint Vincent and the Grenadines': 'https://flagcdn.com/w20/vc.png',
        'Grenada': 'https://flagcdn.com/w20/gd.png',
        'Antigua and Barbuda': 'https://flagcdn.com/w20/ag.png',
        'Saint Kitts and Nevis': 'https://flagcdn.com/w20/kn.png',
        'Dominica': 'https://flagcdn.com/w20/dm.png',
        'Argentina': 'https://flagcdn.com/w20/ar.png',
        'Chile': 'https://flagcdn.com/w20/cl.png',
        'Uruguay': 'https://flagcdn.com/w20/uy.png',
        'Paraguay': 'https://flagcdn.com/w20/py.png',
        'Bolivia': 'https://flagcdn.com/w20/bo.png',
        'Peru': 'https://flagcdn.com/w20/pe.png',
        'Ecuador': 'https://flagcdn.com/w20/ec.png',
        'Colombia': 'https://flagcdn.com/w20/co.png',
        'Venezuela': 'https://flagcdn.com/w20/ve.png',
        'Guyana': 'https://flagcdn.com/w20/gy.png',
        'Suriname': 'https://flagcdn.com/w20/sr.png',
        'French Guiana': 'https://flagcdn.com/w20/gf.png',
        'South Africa': 'https://flagcdn.com/w20/za.png',
        'Egypt': 'https://flagcdn.com/w20/eg.png',
        'Libya': 'https://flagcdn.com/w20/ly.png',
        'Tunisia': 'https://flagcdn.com/w20/tn.png',
        'Algeria': 'https://flagcdn.com/w20/dz.png',
        'Morocco': 'https://flagcdn.com/w20/ma.png',
        'Sudan': 'https://flagcdn.com/w20/sd.png',
        'South Sudan': 'https://flagcdn.com/w20/ss.png',
        'Ethiopia': 'https://flagcdn.com/w20/et.png',
        'Eritrea': 'https://flagcdn.com/w20/er.png',
        'Djibouti': 'https://flagcdn.com/w20/dj.png',
        'Somalia': 'https://flagcdn.com/w20/so.png',
        'Kenya': 'https://flagcdn.com/w20/ke.png',
        'Uganda': 'https://flagcdn.com/w20/ug.png',
        'Tanzania': 'https://flagcdn.com/w20/tz.png',
        'Rwanda': 'https://flagcdn.com/w20/rw.png',
        'Burundi': 'https://flagcdn.com/w20/bi.png',
        'Democratic Republic of the Congo': 'https://flagcdn.com/w20/cd.png',
        'Republic of the Congo': 'https://flagcdn.com/w20/cg.png',
        'Central African Republic': 'https://flagcdn.com/w20/cf.png',
        'Chad': 'https://flagcdn.com/w20/td.png',
        'Niger': 'https://flagcdn.com/w20/ne.png',
        'Nigeria': 'https://flagcdn.com/w20/ng.png',
        'Cameroon': 'https://flagcdn.com/w20/cm.png',
        'Equatorial Guinea': 'https://flagcdn.com/w20/gq.png',
        'Gabon': 'https://flagcdn.com/w20/ga.png',
        'São Tomé and Príncipe': 'https://flagcdn.com/w20/st.png',
        'Angola': 'https://flagcdn.com/w20/ao.png',
        'Zambia': 'https://flagcdn.com/w20/zm.png',
        'Zimbabwe': 'https://flagcdn.com/w20/zw.png',
        'Botswana': 'https://flagcdn.com/w20/bw.png',
        'Namibia': 'https://flagcdn.com/w20/na.png',
        'Lesotho': 'https://flagcdn.com/w20/ls.png',
        'Swaziland': 'https://flagcdn.com/w20/sz.png',
        'Madagascar': 'https://flagcdn.com/w20/mg.png',
        'Mauritius': 'https://flagcdn.com/w20/mu.png',
        'Seychelles': 'https://flagcdn.com/w20/sc.png',
        'Comoros': 'https://flagcdn.com/w20/km.png',
        'Cape Verde': 'https://flagcdn.com/w20/cv.png',
        'Guinea-Bissau': 'https://flagcdn.com/w20/gw.png',
        'Guinea': 'https://flagcdn.com/w20/gn.png',
        'Sierra Leone': 'https://flagcdn.com/w20/sl.png',
        'Liberia': 'https://flagcdn.com/w20/lr.png',
        'Ivory Coast': 'https://flagcdn.com/w20/ci.png',
        'Ghana': 'https://flagcdn.com/w20/gh.png',
        'Togo': 'https://flagcdn.com/w20/tg.png',
        'Benin': 'https://flagcdn.com/w20/bj.png',
        'Burkina Faso': 'https://flagcdn.com/w20/bf.png',
        'Mali': 'https://flagcdn.com/w20/ml.png',
        'Senegal': 'https://flagcdn.com/w20/sn.png',
        'Gambia': 'https://flagcdn.com/w20/gm.png',
        'Mauritania': 'https://flagcdn.com/w20/mr.png',
        'Western Sahara': 'https://flagcdn.com/w20/eh.png'
    }
    
    return country_flags.get(country, 'https://flagcdn.com/w20/xx.png')

def format_record(wins, losses, draws, nc):
    """Форматирует рекорд бойца"""
    record = f"{wins}-{losses}"
    if draws and draws > 0:
        record += f"-{draws}"
    if nc and nc > 0:
        record += f" ({nc} NC)"
    return record

def format_fight_time(seconds):
    """Форматирует время боя"""
    if not seconds or seconds == 0:
        return "N/A"
    
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"

def generate_fighter_card_with_detailed_stats(fighter, index):
    """Генерирует HTML карточку бойца с детальной статистикой"""
    
    (fighter_id, name_ru, name_en, nickname, country, country_flag_url, 
     image_url, height, weight, reach, age, birth_date, full_name, 
     birth_place, stance, team, trainer, belt_rank, years_active, 
     current_division, fighting_out_of, rank_position, is_champion, 
     wins, losses, draws, nc, wins_by_ko, losses_by_ko, wins_by_submission, 
     losses_by_submission, wins_by_decision, losses_by_decision, 
     avg_fight_time_seconds, total_fights) = fighter
    
    # Определяем позицию в рейтинге
    if is_champion:
        rank_display = "👑"
        rank_class = "champion-rank"
    else:
        rank_display = str(rank_position)
        rank_class = "rank-number"
    
    # Получаем URL флага
    flag_url = get_country_flag_url(country) if country else 'https://flagcdn.com/w20/xx.png'
    
    # Форматируем рекорд
    record = format_record(wins or 0, losses or 0, draws or 0, nc or 0)
    
    # Определяем прозвище
    nickname_display = f' "{nickname}"' if nickname else ""
    
    # Детальная статистика
    ko_stats = f"KO: {wins_by_ko or 0}W-{losses_by_ko or 0}L" if wins_by_ko is not None else ""
    sub_stats = f"SUB: {wins_by_submission or 0}W-{losses_by_submission or 0}L" if wins_by_submission is not None else ""
    dec_stats = f"DEC: {wins_by_decision or 0}W-{losses_by_decision or 0}L" if wins_by_decision is not None else ""
    
    return f'''
                    <!-- #{rank_position} {name_ru} -->
                    <div class="rankings-card bg-white border border-gray-200 rounded-lg overflow-hidden">
                        <div class="flex items-center justify-between p-4 bg-gray-50">
                            <div class="flex items-center">
                                <div class="{rank_class} text-white text-lg font-bold w-8 h-8 rounded-full flex items-center justify-center mr-3">{rank_display}</div>
                                <div>
                                    <h3 class="font-bold text-lg text-gray-900">{name_ru}</h3>
                                    <p class="text-sm text-gray-600">{name_en}{nickname_display}</p>
                                </div>
                            </div>
                            <img src="{flag_url}" alt="{country or 'Unknown'}" class="w-6 h-4">
                        </div>
                        <!-- Фото бойца -->
                        <div class="h-32 bg-gray-200 flex items-center justify-center relative">
                            <img src="{image_url or 'fighter.jpg'}" alt="{name_ru}" class="w-full h-full object-cover" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                            <div class="text-gray-400 text-4xl" style="display: none;">🥊</div>
                            <button class="absolute top-2 right-2 bg-blue-600 text-white text-xs px-2 py-1 rounded hover:bg-blue-700 add-to-compare" data-fighter-id="{fighter_id}">
                                + Сравнить
                            </button>
                        </div>
                        <div class="p-4">
                            <div class="space-y-2 text-sm">
                                <div class="flex justify-between">
                                    <span class="text-gray-600">Страна:</span>
                                    <span class="font-medium">{country or 'N/A'}</span>
                                </div>
                                {f'<div class="flex justify-between"><span class="text-gray-600">Возраст:</span><span class="font-medium">{age} лет</span></div>' if age else ''}
                                {f'<div class="flex justify-between"><span class="text-gray-600">Рост:</span><span class="font-medium">{height} см</span></div>' if height else ''}
                                {f'<div class="flex justify-between"><span class="text-gray-600">Вес:</span><span class="font-medium">{weight} кг</span></div>' if weight else ''}
                                {f'<div class="flex justify-between"><span class="text-gray-600">Размах рук:</span><span class="font-medium">{reach} см</span></div>' if reach else ''}
                                <div class="flex justify-between">
                                    <span class="text-gray-600">Рекорд:</span>
                                    <span class="font-bold text-blue-600">{record}</span>
                                </div>
                                {f'<div class="flex justify-between"><span class="text-gray-600">Стойка:</span><span class="font-medium">{stance}</span></div>' if stance else ''}
                                {f'<div class="flex justify-between"><span class="text-gray-600">Команда:</span><span class="font-medium">{team}</span></div>' if team else ''}
                                {f'<div class="flex justify-between"><span class="text-gray-600">Родился:</span><span class="font-medium">{birth_place}</span></div>' if birth_place else ''}
                                {f'<div class="flex justify-between"><span class="text-gray-600">Активен:</span><span class="font-medium">{years_active}</span></div>' if years_active else ''}
                                {f'<div class="flex justify-between"><span class="text-gray-600">Тренируется:</span><span class="font-medium">{fighting_out_of}</span></div>' if fighting_out_of else ''}
                                {f'<div class="flex justify-between"><span class="text-gray-600">Пояс:</span><span class="font-medium">{belt_rank}</span></div>' if belt_rank else ''}
                            </div>
                            
                            <!-- Детальная статистика -->
                            <div class="mt-3 pt-3 border-t border-gray-200">
                                <h4 class="text-xs font-semibold text-gray-700 mb-2">Детальная статистика</h4>
                                <div class="grid grid-cols-2 gap-2 text-xs">
                                    {f'<div class="text-center"><span class="text-gray-600">KO/TKO</span><br><span class="font-bold text-red-600">{wins_by_ko or 0}W-{losses_by_ko or 0}L</span></div>' if wins_by_ko is not None else ''}
                                    {f'<div class="text-center"><span class="text-gray-600">Submission</span><br><span class="font-bold text-blue-600">{wins_by_submission or 0}W-{losses_by_submission or 0}L</span></div>' if wins_by_submission is not None else ''}
                                    {f'<div class="text-center"><span class="text-gray-600">Decision</span><br><span class="font-bold text-green-600">{wins_by_decision or 0}W-{losses_by_decision or 0}L</span></div>' if wins_by_decision is not None else ''}
                                    {f'<div class="text-center"><span class="text-gray-600">Ср. время</span><br><span class="font-bold text-purple-600">{format_fight_time(avg_fight_time_seconds)}</span></div>' if avg_fight_time_seconds else ''}
                                </div>
                            </div>
                        </div>
                    </div>'''

def generate_updated_heavyweight_page():
    """Генерирует обновленную страницу рейтингов тяжелого веса"""
    
    print("🔍 Получение данных с детальной статистикой...")
    fighters = get_heavyweight_rankings_with_detailed_stats()
    
    if not fighters:
        print("❌ Нет данных о бойцах тяжелого веса")
        return
    
    print(f"✅ Найдено {len(fighters)} бойцов")
    
    # Находим чемпиона
    champion = None
    other_fighters = []
    
    for fighter in fighters:
        if fighter[22]:  # is_champion
            champion = fighter
        else:
            other_fighters.append(fighter)
    
    # Генерируем HTML
    html_content = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Рейтинг тяжёлого веса UFC - UFC Ranker</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .gradient-bg {{
            background: linear-gradient(135deg, #1e3a8a 0%, #7c3aed 100%);
        }}
        .champion-card {{
            background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
        }}
        .champion-rank {{
            background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
        }}
        .rankings-card {{
            transition: all 0.3s ease;
        }}
        .rankings-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        .rank-number {{
            background: linear-gradient(135deg, #1e3a8a 0%, #7c3aed 100%);
        }}
    </style>
</head>
<body class="bg-gray-100">
    <!-- Header -->
    <header class="bg-white shadow-lg">
        <div class="container mx-auto px-4 py-6">
            <div class="flex items-center justify-between">
                <h1 class="text-3xl font-bold text-gray-900">
                    🥊 UFC Ranker
                </h1>
                <nav class="space-x-4">
                    <a href="main_page_demo.html" class="px-4 py-2 rounded-lg text-gray-600 hover:bg-gray-100">🏠 Главная</a>
                    <a href="#" class="px-4 py-2 rounded-lg bg-blue-600 text-white">🥊 Рейтинги</a>
                    <a href="fighters_list_demo.html" class="px-4 py-2 rounded-lg text-gray-600 hover:bg-gray-100">👊 Бойцы</a>
                </nav>
            </div>
        </div>
    </header>

    <div class="container mx-auto px-4 py-8">
        <!-- Заголовок рейтинга -->
        <div class="text-center mb-8">
            <h1 class="text-4xl font-bold text-gray-900 mb-2">
                🏆 Рейтинг тяжёлого веса UFC
            </h1>
            <p class="text-xl text-gray-600">Топ-{len(fighters)} бойцов в весовой категории 93-120 кг</p>
            <p class="text-sm text-gray-500 mt-2">Обновлено: {datetime.now().strftime("%d.%m.%Y %H:%M")} | С детальной статистикой</p>
        </div>'''

    # Добавляем секцию чемпиона с детальной статистикой
    if champion:
        (fighter_id, name_ru, name_en, nickname, country, country_flag_url, 
         image_url, height, weight, reach, age, birth_date, full_name, 
         birth_place, stance, team, trainer, belt_rank, years_active, 
         current_division, fighting_out_of, rank_position, is_champion, 
         wins, losses, draws, nc, wins_by_ko, losses_by_ko, wins_by_submission, 
         losses_by_submission, wins_by_decision, losses_by_decision, 
         avg_fight_time_seconds, total_fights) = champion
        
        flag_url = get_country_flag_url(country) if country else 'https://flagcdn.com/w20/xx.png'
        record = format_record(wins or 0, losses or 0, draws or 0, nc or 0)
        nickname_display = f' "{nickname}"' if nickname else ""
        
        html_content += f'''
        <!-- Чемпион -->
        <div class="bg-white rounded-lg shadow-lg overflow-hidden mb-8">
            <div class="champion-card p-6">
                <div class="flex items-center justify-center mb-4">
                    <div class="text-6xl mr-4">👑</div>
                    <div class="text-center">
                        <h2 class="text-3xl font-bold text-white mb-2">ЧЕМПИОН</h2>
                        <p class="text-white text-lg">UFC Heavyweight Champion</p>
                    </div>
                </div>
            </div>
            
            <div class="md:flex">
                <!-- Фото чемпиона -->
                <div class="md:w-1/3">
                    <div class="h-96 md:h-full champion-card flex items-center justify-center">
                        <img
                            src="{image_url or 'https://via.placeholder.com/400x500/1E3A8A/FFFFFF?text=' + name_ru.replace(' ', '+')}"
                            alt="{name_ru}"
                            class="w-full h-full object-cover"
                        />
                    </div>
                </div>

                <!-- Информация о чемпионе -->
                <div class="md:w-2/3 p-8">
                    <div class="flex items-start justify-between mb-6">
                        <div>
                            <h1 class="text-4xl font-bold text-gray-900 mb-2">
                                {name_ru}
                            </h1>
                            <p class="text-xl text-gray-600 mb-2">{name_en}</p>
                            <p class="text-lg text-blue-600 font-semibold">{nickname_display}</p>
                        </div>
                        
                        <img
                            src="{flag_url}"
                            alt="{country or 'Unknown'}"
                            class="w-12 h-8 object-cover rounded"
                        />
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                        <div>
                            <h3 class="text-lg font-semibold text-gray-900 mb-3">Основная информация</h3>
                            <div class="space-y-2">
                                <div class="flex justify-between">
                                    <span class="text-gray-600">Страна:</span>
                                    <span class="font-medium">{country or 'N/A'}</span>
                                </div>
                                {f'<div class="flex justify-between"><span class="text-gray-600">Возраст:</span><span class="font-medium">{age} лет</span></div>' if age else ''}
                                {f'<div class="flex justify-between"><span class="text-gray-600">Рост:</span><span class="font-medium">{height} см</span></div>' if height else ''}
                                {f'<div class="flex justify-between"><span class="text-gray-600">Вес:</span><span class="font-medium">{weight} кг</span></div>' if weight else ''}
                                {f'<div class="flex justify-between"><span class="text-gray-600">Размах рук:</span><span class="font-medium">{reach} см</span></div>' if reach else ''}
                                <div class="flex justify-between">
                                    <span class="text-gray-600">Категория:</span>
                                    <span class="font-medium text-blue-600">Тяжёлый вес</span>
                                </div>
                                {f'<div class="flex justify-between"><span class="text-gray-600">Стойка:</span><span class="font-medium">{stance}</span></div>' if stance else ''}
                                {f'<div class="flex justify-between"><span class="text-gray-600">Команда:</span><span class="font-medium">{team}</span></div>' if team else ''}
                                {f'<div class="flex justify-between"><span class="text-gray-600">Родился:</span><span class="font-medium">{birth_place}</span></div>' if birth_place else ''}
                                {f'<div class="flex justify-between"><span class="text-gray-600">Активен:</span><span class="font-medium">{years_active}</span></div>' if years_active else ''}
                                {f'<div class="flex justify-between"><span class="text-gray-600">Тренируется:</span><span class="font-medium">{fighting_out_of}</span></div>' if fighting_out_of else ''}
                                {f'<div class="flex justify-between"><span class="text-gray-600">Пояс:</span><span class="font-medium">{belt_rank}</span></div>' if belt_rank else ''}
                            </div>
                        </div>

                        <div>
                            <h3 class="text-lg font-semibold text-gray-900 mb-3">Боевой рекорд</h3>
                            <div class="space-y-2">
                                <div class="flex justify-between">
                                    <span class="text-gray-600">Победы:</span>
                                    <span class="font-bold text-green-600 text-xl">{wins or 0}</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-gray-600">Поражения:</span>
                                    <span class="font-bold text-red-600 text-xl">{losses or 0}</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-gray-600">Ничьи:</span>
                                    <span class="font-bold text-yellow-600 text-xl">{draws or 0}</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-gray-600">Всего боев:</span>
                                    <span class="font-bold text-blue-600 text-xl">{(wins or 0) + (losses or 0) + (draws or 0)}</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-gray-600">% побед:</span>
                                    <span class="font-bold text-blue-600 text-xl">{((wins or 0) / ((wins or 0) + (losses or 0) + (draws or 0)) * 100):.1f}%</span>
                                </div>
                            </div>
                        </div>

                        <div>
                            <h3 class="text-lg font-semibold text-gray-900 mb-3">Детальная статистика</h3>
                            <div class="space-y-2">
                                {f'<div class="flex justify-between"><span class="text-gray-600">KO/TKO:</span><span class="font-bold text-red-600">{wins_by_ko or 0}W-{losses_by_ko or 0}L</span></div>' if wins_by_ko is not None else ''}
                                {f'<div class="flex justify-between"><span class="text-gray-600">Submission:</span><span class="font-bold text-blue-600">{wins_by_submission or 0}W-{losses_by_submission or 0}L</span></div>' if wins_by_submission is not None else ''}
                                {f'<div class="flex justify-between"><span class="text-gray-600">Decision:</span><span class="font-bold text-green-600">{wins_by_decision or 0}W-{losses_by_decision or 0}L</span></div>' if wins_by_decision is not None else ''}
                                {f'<div class="flex justify-between"><span class="text-gray-600">Ср. время боя:</span><span class="font-bold text-purple-600">{format_fight_time(avg_fight_time_seconds)}</span></div>' if avg_fight_time_seconds else ''}
                                {f'<div class="flex justify-between"><span class="text-gray-600">Всего боев:</span><span class="font-bold text-gray-600">{total_fights or 0}</span></div>' if total_fights else ''}
                            </div>
                        </div>
                    </div>

                    <!-- Статус чемпиона -->
                    <div class="bg-yellow-100 border-l-4 border-yellow-500 p-4 rounded">
                        <div class="flex items-center">
                            <div class="text-yellow-500 text-2xl mr-3">👑</div>
                            <div>
                                <p class="text-yellow-800 font-semibold">Чемпион UFC в тяжёлом весе</p>
                                <p class="text-yellow-700 text-sm">#1 в рейтинге тяжёлого веса</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>'''

    # Добавляем рейтинг бойцов
    html_content += '''
        <!-- Рейтинг бойцов -->
        <div class="bg-white rounded-lg shadow-lg p-6">
            <h2 class="text-2xl font-bold text-gray-900 mb-6">📊 Рейтинг бойцов</h2>
            
            <!-- Ряды по 3 карточки -->
            <div class="space-y-6">'''
    
    # Группируем бойцов по рядам
    for i in range(0, len(other_fighters), 3):
        row_fighters = other_fighters[i:i+3]
        html_content += f'''
                <!-- Ряд {i//3 + 1}: #{i+1}-{min(i+3, len(other_fighters))} -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">'''
        
        for fighter in row_fighters:
            html_content += generate_fighter_card_with_detailed_stats(fighter, i)
        
        html_content += '''
                </div>'''
    
    # Завершаем HTML
    html_content += '''
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white py-8 mt-12">
        <div class="container mx-auto px-4 text-center">
            <p>&copy; 2024 UFC Ranker. Все права защищены.</p>
            <p class="mt-2 text-sm text-gray-400">
                Рейтинг тяжёлого веса UFC - Топ-15 бойцов с детальной статистикой
            </p>
        </div>
    </footer>

    <script>
        // Анимация при загрузке
        document.addEventListener('DOMContentLoaded', function() {
            const cards = document.querySelectorAll('.rankings-card');
            cards.forEach((card, index) => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                setTimeout(() => {
                    card.style.transition = 'all 0.5s ease';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, index * 100);
            });

            // Функционал сравнения
            initializeCompare();
        });

        function initializeCompare() {
            // Обработчики для кнопок добавления в сравнение
            document.querySelectorAll('.add-to-compare').forEach(button => {
                button.addEventListener('click', function() {
                    const fighterId = parseInt(this.dataset.fighterId);
                    addToCompare(fighterId);
                });
            });
        }

        function addToCompare(fighterId) {
            // Сохраняем в localStorage
            let compareList = JSON.parse(localStorage.getItem('compareList') || '[]');
            
            if (compareList.length >= 2) {
                alert('Можно сравнить максимум 2 бойцов');
                return;
            }

            if (compareList.includes(fighterId)) {
                alert('Боец уже добавлен в сравнение');
                return;
            }

            compareList.push(fighterId);
            localStorage.setItem('compareList', JSON.stringify(compareList));
            
            // Обновляем UI
            updateCompareButtons();
            showCompareNotification();
        }

        function updateCompareButtons() {
            const compareList = JSON.parse(localStorage.getItem('compareList') || '[]');
            
            document.querySelectorAll('.add-to-compare').forEach(button => {
                const fighterId = parseInt(button.dataset.fighterId);
                if (compareList.includes(fighterId)) {
                    button.textContent = '✓ В сравнении';
                    button.classList.remove('bg-blue-600', 'hover:bg-blue-700');
                    button.classList.add('bg-green-600', 'hover:bg-green-700');
                    button.disabled = true;
                } else if (compareList.length >= 2) {
                    button.textContent = '+ Сравнить';
                    button.classList.remove('bg-green-600', 'hover:bg-green-700');
                    button.classList.add('bg-gray-400', 'hover:bg-gray-400');
                    button.disabled = true;
                } else {
                    button.textContent = '+ Сравнить';
                    button.classList.remove('bg-green-600', 'hover:bg-green-700', 'bg-gray-400', 'hover:bg-gray-400');
                    button.classList.add('bg-blue-600', 'hover:bg-blue-700');
                    button.disabled = false;
                }
            });
        }

        function showCompareNotification() {
            const compareList = JSON.parse(localStorage.getItem('compareList') || '[]');
            
            // Создаем уведомление
            const notification = document.createElement('div');
            notification.className = 'fixed top-20 right-4 bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg z-50';
            notification.innerHTML = `
                <div class="flex items-center">
                    <span>${compareList.length} бойцов в сравнении</span>
                    <a href="compare_fighters_demo.html" class="ml-2 bg-white text-blue-600 px-2 py-1 rounded text-sm hover:bg-gray-100">
                        Сравнить
                    </a>
                </div>
            `;
            
            document.body.appendChild(notification);
            
            // Удаляем уведомление через 3 секунды
            setTimeout(() => {
                notification.remove();
            }, 3000);
        }

        // Обновляем кнопки при загрузке страницы
        updateCompareButtons();
    </script>
</body>
</html>'''
    
    # Сохраняем файл
    with open('heavyweight_rankings_demo.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Страница обновлена: heavyweight_rankings_demo.html")
    print(f"📊 Показано {len(fighters)} бойцов с детальной статистикой")
    if champion:
        print(f"👑 Чемпион: {champion[1]} ({champion[2]})")

def main():
    """Главная функция"""
    print("🥊 ОБНОВЛЕНИЕ СТРАНИЦЫ С ДЕТАЛЬНОЙ СТАТИСТИКОЙ")
    print("=" * 60)
    generate_updated_heavyweight_page()

if __name__ == "__main__":
    main()




