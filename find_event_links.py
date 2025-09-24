#!/usr/bin/env python3
"""
Скрипт для поиска ссылок на исторические события UFC
"""

import requests
from bs4 import BeautifulSoup

def find_event_links():
    """Находит ссылки на исторические события UFC"""
    
    print("🔍 ПОИСК ССЫЛОК НА ИСТОРИЧЕСКИЕ СОБЫТИЯ UFC")
    print("=" * 50)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get("https://en.wikipedia.org/wiki/List_of_UFC_events", headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Ищем ссылки на другие страницы с событиями
        print("🔍 Ссылки на другие страницы с событиями:")
        event_links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = link.get_text(strip=True)
            if 'UFC' in text and ('event' in href.lower() or 'ufc' in href.lower()):
                event_links.append((text, href))
                print(f"  {text} -> {href}")
        
        print(f"\n📊 Найдено {len(event_links)} ссылок на события")
        
        # Ищем конкретно ссылки на UFC 1-100
        print(f"\n🔍 Поиск ссылок на UFC 1-100:")
        for text, href in event_links:
            if any(f"UFC {i}" in text for i in range(1, 101)):
                print(f"  ⭐ {text} -> {href}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    find_event_links()
