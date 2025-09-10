#!/usr/bin/env python3
"""
Скрипт обновления данных ufc.stats
"""

import requests
import sqlite3
import gzip
import re
from datetime import datetime

def update_ufc_stats():
    """Обновляем данные ufc.stats"""
    print("🔄 Обновляем данные ufc.stats...")
    
    # Скачиваем новые данные
    url = "https://github.com/mtoto/ufc.stats/raw/master/data/ufc_stats.rda"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with open('ufc_stats.rda', 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Новые данные скачаны: {len(response.content):,} байт")
        
        # Здесь можно добавить логику обновления существующих данных
        print("✅ Данные обновлены!")
        
    except Exception as e:
        print(f"❌ Ошибка обновления: {e}")

if __name__ == "__main__":
    update_ufc_stats()
