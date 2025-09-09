#!/usr/bin/env python3
"""
Build compact HTML pages per weight category with fighter profile data
- Reads saved page fight_ru_ufc.html
- Finds each weight category and fighter links
- Fetches each fighter profile and extracts:
  - Photo URL (img[itemprop="url"]) or primary profile image
  - Name RU and EN
  - Country name (class="fighter-country-name")
  - Country flag (class="fighter-country-flag")
  - Fight score (class="fight-score")
  - Height / Weight
  - Age
  - Reach
  - Nickname
- Generates category_pages/<category>.html
"""

import os
import re
import time
import json
import hashlib
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
REQUEST_DELAY_SEC = 0.75
TIMEOUT_SEC = 12
BASE_URL = 'https://fight.ru'
SAVED_HTML = 'fight_ru_ufc.html'
OUTPUT_DIR = 'category_pages'
CACHE_DIR = os.path.join('.cache', 'fighters')


def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)


def clean_text(text: Optional[str]) -> str:
    if not text:
        return ''
    text = text.replace('\u00ad', '').replace('&shy;', '')
    return re.sub(r'\s+', ' ', text).strip()


def safe_filename(name: str) -> str:
    name = name.lower()
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = re.sub(r'\s+', '_', name)
    return name


def load_saved_page() -> BeautifulSoup:
    with open(SAVED_HTML, 'r', encoding='utf-8') as f:
        html = f.read()
    html = html.replace('&shy;', '').replace('\u00ad', '')
    return BeautifulSoup(html, 'html.parser')


def cache_key(url: str) -> str:
    return hashlib.sha1(url.encode('utf-8')).hexdigest()


def read_cache(url: str) -> Optional[str]:
    key = cache_key(url)
    path = os.path.join(CACHE_DIR, f'{key}.html')
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None
    return None


def write_cache(url: str, content: str) -> None:
    key = cache_key(url)
    path = os.path.join(CACHE_DIR, f'{key}.html')
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception:
        pass


def fetch(url: str) -> Optional[str]:
    cached = read_cache(url)
    if cached:
        return cached
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SEC)
        resp.raise_for_status()
        html = resp.text.replace('&shy;', '').replace('\u00ad', '')
        write_cache(url, html)
        time.sleep(REQUEST_DELAY_SEC)
        return html
    except Exception:
        return None


def extract_profile_data(profile_html: str) -> Dict[str, str]:
    soup = BeautifulSoup(profile_html, 'html.parser')

    # Image
    image_url = None
    img = soup.find('img', attrs={'itemprop': 'url'})
    if img and img.get('src'):
        image_url = img['src']
    if not image_url:
        og = soup.find('meta', property='og:image')
        if og and og.get('content'):
            image_url = og['content']
    if not image_url:
        first_img = soup.find('img')
        if first_img and first_img.get('src'):
            image_url = first_img['src']

    # Names - ищем по правильной структуре
    name_ru = ''
    name_en = ''
    
    # Русское имя из h1 с классом fighter-name
    h1_name = soup.find('h1', class_='fighter-name')
    if h1_name:
        name_ru = clean_text(h1_name.get_text())
    
    # Английское имя из div с классом fighter-latin-name
    latin_name = soup.find('div', class_='fighter-latin-name')
    if latin_name:
        name_en = clean_text(latin_name.get_text())
    
    # Если не нашли через правильные классы, пробуем альтернативные способы
    if not name_ru:
        h1 = soup.find(['h1', 'h2'])
        if h1:
            name_ru = clean_text(h1.get_text())
    
    if not name_en:
        # Пробуем другие варианты
        en_candidates = [
            soup.find(class_='fighter-eng-name'),
            soup.find('div', class_='eng-name'),
            soup.find('span', class_='eng-name'),
        ]
        
        for cand in en_candidates:
            if cand and clean_text(cand.get_text()):
                text = clean_text(cand.get_text())
                # Проверяем, что это не слишком длинный текст
                if len(text) < 50 and re.search(r'^[A-Za-z\s\.\-\']+$', text):
                    name_en = text
                    break

    # Country name and flag
    country_name = ''
    country_flag = ''
    cn = soup.find(class_='fighter-country-name')
    if cn:
        country_name = clean_text(cn.get_text())
    cf = soup.find(class_='fighter-country-flag')
    if cf:
        flag_img = cf.find('img')
        if flag_img and flag_img.get('src'):
            country_flag = flag_img['src']

    # Fight score
    fight_score = ''
    fs = soup.find(class_='fight-score')
    if fs:
        fight_score = clean_text(fs.get_text())

    # Height / Weight / Reach / Age / Nickname
    height = ''
    weight = ''
    reach = ''
    age = ''
    nickname = ''

    # Ищем данные в структуре <li><span class="text">Label</span><span class="sub">Value</span></li>
    for li in soup.find_all('li'):
        text_span = li.find('span', class_='text')
        sub_span = li.find('span', class_='sub')
        
        if not text_span or not sub_span:
            continue
            
        label = clean_text(text_span.get_text())
        value = clean_text(sub_span.get_text())
        
        if not label or not value:
            continue
            
        label_lower = label.lower()
        
        # Проверяем, что значение не содержит слишком много текста (это означает, что мы нашли не тот элемент)
        if len(value) > 100:  # Если значение слишком длинное, пропускаем
            continue
        
        if 'рост' in label_lower and 'вес' in label_lower:
            # Рост / Вес в одном поле
            height_weight = value
            if ' / ' in height_weight:
                parts = height_weight.split(' / ')
                if len(parts) >= 2:
                    height = parts[0].strip()
                    weight = parts[1].strip()
            else:
                # Пробуем извлечь из meta тегов
                height_meta = li.find('meta', {'itemprop': 'height'})
                weight_meta = li.find('meta', {'itemprop': 'weight'})
                if height_meta and height_meta.get('content'):
                    height = clean_text(height_meta['content'])
                if weight_meta and weight_meta.get('content'):
                    weight = clean_text(weight_meta['content'])
        elif 'рост' in label_lower:
            height = value
        elif 'вес' in label_lower:
            weight = value
        elif 'размах рук' in label_lower:
            reach = value
        elif 'возраст' in label_lower:
            age = value
        elif 'ник' in label_lower:
            nickname = value

    # Дополнительно ищем в meta тегах
    if not height:
        height_meta = soup.find('meta', {'itemprop': 'height'})
        if height_meta and height_meta.get('content'):
            height = clean_text(height_meta['content'])
    
    if not weight:
        weight_meta = soup.find('meta', {'itemprop': 'weight'})
        if weight_meta and weight_meta.get('content'):
            weight = clean_text(weight_meta['content'])
    
    if not age:
        birth_meta = soup.find('meta', {'itemprop': 'birthDate'})
        if birth_meta and birth_meta.get('content'):
            # Извлекаем возраст из даты рождения или используем дату как есть
            birth_date = birth_meta['content']
            age = birth_date  # Можно добавить вычисление возраста, но пока оставим дату

    # Дополнительный поиск по более точным селекторам
    # Ищем блоки с данными бойца
    fighter_info_blocks = soup.find_all(['div', 'section'], class_=re.compile(r'fighter|profile|info'))
    
    for block in fighter_info_blocks:
        # Ищем все li элементы в блоке
        for li in block.find_all('li'):
            text_span = li.find('span', class_='text')
            sub_span = li.find('span', class_='sub')
            
            if not text_span or not sub_span:
                continue
                
            label = clean_text(text_span.get_text())
            value = clean_text(sub_span.get_text())
            
            if not label or not value or len(value) > 50:  # Ограничиваем длину значения
                continue
                
            label_lower = label.lower()
            
            if 'рост' in label_lower and 'вес' in label_lower and not height and not weight:
                if ' / ' in value:
                    parts = value.split(' / ')
                    if len(parts) >= 2:
                        height = parts[0].strip()
                        weight = parts[1].strip()
            elif 'рост' in label_lower and not height:
                height = value
            elif 'вес' in label_lower and not weight:
                weight = value
            elif 'размах рук' in label_lower and not reach:
                reach = value
            elif 'возраст' in label_lower and not age:
                age = value
            elif 'ник' in label_lower and not nickname:
                nickname = value

    return {
        'image_url': image_url or '',
        'name_ru': name_ru,
        'name_en': name_en,
        'country_name': country_name,
        'country_flag': country_flag,
        'fight_score': fight_score,
        'height': height,
        'weight': weight,
        'reach': reach,
        'age': age,
        'nickname': nickname,
    }


def parse_categories_and_fighters(soup: BeautifulSoup) -> Dict[str, List[Dict[str, str]]]:
    """Return mapping: category_name -> list of fighters dict with minimal info and profile link"""
    result: Dict[str, List[Dict[str, str]]] = {}

    for title_div in soup.find_all('div', class_='weight-name'):
        category_name = clean_text(title_div.get_text())
        if not category_name:
            continue
        container = title_div.find_parent('div', class_='org-single')
        if not container:
            continue

        fighters: List[Dict[str, str]] = []

        # Champion block
        champ = container.find('div', class_='first-fighter')
        if champ:
            a = champ.find('a')
            profile_url = a['href'] if a and a.get('href') else None
            name_el = champ.find('div', class_='fighter-name')
            name = clean_text(name_el.get_text()) if name_el else ''
            fighters.append({
                'rank': 'Ч',
                'name': name,
                'profile_url': profile_url or ''
            })

        # Ranked fighters
        for nf in container.find_all('div', class_='next-fighter'):
            a = nf.find('a')
            profile_url = a['href'] if a and a.get('href') else None
            num_el = nf.find('div', class_='fighter-number')
            name_el = nf.find('div', class_='fighter-name')
            if not num_el or not name_el:
                continue
            fighters.append({
                'rank': clean_text(num_el.get_text()),
                'name': clean_text(name_el.get_text()),
                'profile_url': profile_url or ''
            })

        if fighters:
            result[category_name] = fighters

    return result


def build_category_html(category_name: str, fighters: List[Dict[str, str]]) -> str:
    # CSS for new layout with champion and 3 fighters per row
    css = (
        "*{box-sizing:border-box} body{font-family:Arial,sans-serif;background:#f6f7fb;margin:0;padding:20px;}"
        ".container{max-width:1400px;margin:0 auto;background:#fff;border-radius:12px;box-shadow:0 10px 25px rgba(0,0,0,.08);overflow:hidden;}"
        ".header{background:#202733;color:#fff;padding:20px 24px;} .header h1{margin:0;font-size:22px;}"
        ".champion{background:linear-gradient(135deg,#d4af37,#ffd700);padding:30px;margin:20px;border-radius:15px;box-shadow:0 8px 20px rgba(212,175,55,0.3);}"
        ".champion-content{display:flex;gap:30px;align-items:center;}"
        ".champion-img{width:240px;height:262px;border-radius:12px;object-fit:cover;border:3px solid #fff;box-shadow:0 4px 12px rgba(0,0,0,0.2);}"
        ".champion-info{flex:1;color:#fff;}"
        ".champion-title{font-size:28px;font-weight:700;margin:0 0 8px;text-shadow:1px 1px 2px rgba(0,0,0,0.3);}"
        ".champion-subtitle{font-size:18px;margin:0 0 20px;opacity:0.9;}"
        ".champion-badge{background:rgba(255,255,255,0.2);color:#fff;padding:8px 16px;border-radius:20px;font-weight:700;font-size:16px;display:inline-block;margin-bottom:15px;}"
        ".champion-data{display:flex;flex-direction:column;gap:8px;margin-top:20px;}"
        ".champion-row{display:flex;align-items:center;margin:6px 0;font-size:16px;background:rgba(255,255,255,0.1);padding:8px 12px;border-radius:8px;}"
        ".champion-flag{width:24px;height:16px;object-fit:cover;border:1px solid rgba(255,255,255,0.3);border-radius:3px;margin-left:8px;}"
        ".fighters-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:16px;padding:20px;}"
        ".fighter-card{background:#fafbff;border:1px solid #eef0f5;border-radius:12px;padding:16px;text-align:center;box-shadow:0 4px 8px rgba(0,0,0,0.05);transition:transform 0.2s,box-shadow 0.2s;}"
        ".fighter-card:hover{transform:translateY(-2px);box-shadow:0 6px 16px rgba(0,0,0,0.1);}"
        ".fighter-img{width:160px;height:175px;border-radius:10px;object-fit:cover;border:2px solid #e3e6ef;background:#fff;margin:0 auto 12px;display:block;}"
        ".fighter-title{font-weight:700;color:#1f2430;margin:0 0 4px;font-size:16px;}"
        ".fighter-subtitle{color:#566075;font-size:14px;margin:0 0 12px;}"
        ".fighter-badge{background:#2f49d1;color:#fff;padding:6px 12px;border-radius:8px;font-weight:700;font-size:14px;display:inline-block;margin-bottom:12px;box-shadow:0 2px 4px rgba(47,73,209,0.3);}"
        ".fighter-data{display:flex;flex-direction:column;gap:6px;margin-top:12px;}"
        ".fighter-row{display:flex;align-items:center;justify-content:flex-start;margin:3px 0;font-size:12px;color:#30374a;background:#f8f9fa;padding:6px 8px;border-radius:6px;border-left:3px solid #2f49d1;}"
        ".fighter-value{font-size:18px;font-weight:600;color:#1f2430;}"
        ".fighter-flag{width:18px;height:12px;object-fit:cover;border:1px solid #d4d7de;border-radius:2px;margin-left:6px;}"
        ".muted{color:#6f778a;margin-right:6px;font-weight:600;}"
        ".icon{font-size:14px;margin-right:4px;}"
        "@media (max-width:1400px){.fighters-grid{grid-template-columns:repeat(4,1fr);}}"
        "@media (max-width:1100px){.fighters-grid{grid-template-columns:repeat(3,1fr);}}"
        "@media (max-width:768px){.fighters-grid{grid-template-columns:1fr;}.champion-content{flex-direction:column;text-align:center;}.champion-img{width:200px;height:218px;}}"
    )

    html = [
        '<!DOCTYPE html>',
        '<html lang="ru">',
        '<head>',
        '<meta charset="utf-8"/>',
        f'<title>UFC — {category_name}</title>',
        f'<style>{css}</style>',
        '</head>',
        '<body>',
        '<div class="container">',
        f'<div class="header"><h1>UFC — {category_name}</h1></div>'
    ]

    # Разделяем чемпиона и остальных бойцов
    champion = None
    other_fighters = []
    
    for fighter in fighters:
        if fighter.get('rank') == 'Ч':
            champion = fighter
        else:
            other_fighters.append(fighter)

    # Секция чемпиона
    if champion:
        badge = champion.get('rank', '')
        name_ru = champion.get('name_ru') or champion.get('name') or ''
        name_en = champion.get('name_en', '')
        country_name = champion.get('country_name', '')
        country_flag = champion.get('country_flag', '')
        fight_score = champion.get('fight_score', '')
        height = champion.get('height', '')
        weight = champion.get('weight', '')
        age = champion.get('age', '')
        reach = champion.get('reach', '')
        nickname = champion.get('nickname', '')
        image_url = champion.get('image_url', '')

        # Очищаем данные от лишнего текста
        if name_en and len(name_en) > 50:
            name_en = ''

        champion_rows: List[str] = []
        if fight_score:
            champion_rows.append(f'<div class="champion-row"><span class="icon">🏆</span><span class="muted">Рекорд:</span> <span class="fighter-value">{fight_score}</span></div>')
        if height or weight:
            hw = ' / '.join([p for p in [height, weight] if p])
            champion_rows.append(f'<div class="champion-row"><span class="icon">📏</span><span class="muted">Рост/Вес:</span> <span class="fighter-value">{hw}</span></div>')
        if age:
            champion_rows.append(f'<div class="champion-row"><span class="icon">🎂</span><span class="muted">Возраст:</span> <span class="fighter-value">{age}</span></div>')
        if reach:
            champion_rows.append(f'<div class="champion-row"><span class="icon">📐</span><span class="muted">Размах рук:</span> <span class="fighter-value">{reach}</span></div>')
        if nickname:
            champion_rows.append(f'<div class="champion-row"><span class="icon">🏷️</span><span class="muted">Ник:</span> <span class="fighter-value">{nickname}</span></div>')

        flag_html = f'<img class="champion-flag" src="{country_flag}" alt="flag">' if country_flag else ''
        country_html = f'<div class="champion-row"><span class="icon">🌍</span><span class="muted">Страна:</span> <span class="fighter-value">{country_name}</span>{flag_html}</div>' if (country_name or country_flag) else ''

        html.extend([
            '<div class="champion">',
            '<div class="champion-content">',
            f'<img class="champion-img" src="{image_url}" alt="{name_ru or name_en or "Champion"}" onerror="this.style.display=\'none\'">',
            '<div class="champion-info">',
            f'<div class="champion-badge">👑 ЧЕМПИОН</div>' if badge else '',
            f'<h2 class="champion-title">{name_ru}</h2>' if name_ru else '',
            f'<p class="champion-subtitle">{name_en}</p>' if name_en and len(name_en) < 50 else '',
            '<div class="champion-data">',
            *champion_rows,
            country_html,
            '</div>',
            '</div>',
            '</div>',
            '</div>'
        ])

    # Сетка остальных бойцов (5 в ряд)
    if other_fighters:
        html.append('<div class="fighters-grid">')
        
        for fighter in other_fighters:
            badge = fighter.get('rank', '')
            name_ru = fighter.get('name_ru') or fighter.get('name') or ''
            name_en = fighter.get('name_en', '')
            country_name = fighter.get('country_name', '')
            country_flag = fighter.get('country_flag', '')
            fight_score = fighter.get('fight_score', '')
            height = fighter.get('height', '')
            weight = fighter.get('weight', '')
            age = fighter.get('age', '')
            reach = fighter.get('reach', '')
            nickname = fighter.get('nickname', '')
            image_url = fighter.get('image_url', '')

            # Очищаем данные от лишнего текста
            if name_en and len(name_en) > 50:
                name_en = ''

            fighter_rows: List[str] = []
            if fight_score:
                fighter_rows.append(f'<div class="fighter-row"><span class="icon">🏆</span><span class="muted">Рекорд:</span> <span class="fighter-value">{fight_score}</span></div>')
            if height or weight:
                hw = ' / '.join([p for p in [height, weight] if p])
                fighter_rows.append(f'<div class="fighter-row"><span class="icon">📏</span><span class="muted">Рост/Вес:</span> <span class="fighter-value">{hw}</span></div>')
            if age:
                fighter_rows.append(f'<div class="fighter-row"><span class="icon">🎂</span><span class="muted">Возраст:</span> <span class="fighter-value">{age}</span></div>')
            if reach:
                fighter_rows.append(f'<div class="fighter-row"><span class="icon">📐</span><span class="muted">Размах рук:</span> <span class="fighter-value">{reach}</span></div>')
            if nickname:
                fighter_rows.append(f'<div class="fighter-row"><span class="icon">🏷️</span><span class="muted">Ник:</span> <span class="fighter-value">{nickname}</span></div>')

            flag_html = f'<img class="fighter-flag" src="{country_flag}" alt="flag">' if country_flag else ''
            country_html = f'<div class="fighter-row"><span class="icon">🌍</span><span class="muted">Страна:</span> <span class="fighter-value">{country_name}</span>{flag_html}</div>' if (country_name or country_flag) else ''

            html.extend([
                '<div class="fighter-card">',
                f'<img class="fighter-img" src="{image_url}" alt="{name_ru or name_en or "Fighter"}" onerror="this.style.display=\'none\'">',
                f'<div class="fighter-badge">{badge}</div>' if badge else '',
                f'<h3 class="fighter-title">{name_ru}</h3>' if name_ru else '',
                f'<p class="fighter-subtitle">{name_en}</p>' if name_en and len(name_en) < 50 else '',
                '<div class="fighter-data">',
                *fighter_rows,
                country_html,
                '</div>',
                '</div>'
            ])
        
        html.append('</div>')

    html.extend(['</div>', '</body>', '</html>'])
    return '\n'.join([part for part in html if part is not None])


def build_pages() -> None:
    ensure_dirs()
    soup = load_saved_page()

    categories = parse_categories_and_fighters(soup)
    total_categories = 0
    total_profiles = 0

    for category_name, fighters in categories.items():
        enriched: List[Dict[str, str]] = []
        for f in fighters:
            profile_url = f.get('profile_url')
            profile_html = fetch(profile_url) if profile_url else None
            profile_data: Dict[str, str] = extract_profile_data(profile_html) if profile_html else {}
            enriched.append({
                **f,
                **profile_data,
            })
            total_profiles += 1
        page_html = build_category_html(category_name, enriched)
        out_path = os.path.join(OUTPUT_DIR, f'{safe_filename(category_name)}.html')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(page_html)
        total_categories += 1

    print(f'✔ Создано страниц категорий: {total_categories}')
    print(f'👥 Обработано профилей: {total_profiles}')


if __name__ == '__main__':
    build_pages()
