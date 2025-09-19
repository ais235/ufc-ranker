#!/usr/bin/env python3
"""
Базовый класс для всех парсеров UFC
"""

import requests
import time
from pathlib import Path
from typing import Optional
from bs4 import BeautifulSoup


class BaseParser:
    """Базовый класс для всех парсеров"""
    
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def fetch(self, url: str, use_cache: bool = True) -> Optional[str]:
        """Загружает HTML страницу с кэшированием"""
        try:
            # Проверяем кэш
            if use_cache:
                cache_file = self.cache_dir / f"{hash(url)}.html"
                if cache_file.exists():
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        return f.read()
            
            # Загружаем страницу
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Сохраняем в кэш
            if use_cache:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    f.write(response.text)
            
            return response.text
            
        except Exception as e:
            print(f"❌ Ошибка при загрузке {url}: {e}")
            return None
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """Парсит HTML с помощью BeautifulSoup"""
        return BeautifulSoup(html, 'lxml')
    
    def clean_text(self, text: str) -> str:
        """Очищает текст от лишних символов"""
        if not text:
            return ""
        
        # Удаляем лишние пробелы и переносы строк
        text = ' '.join(text.split())
        
        # Удаляем специальные символы
        text = text.strip()
        
        return text
    
    def wait(self, seconds: float = 1.0):
        """Пауза между запросами"""
        time.sleep(seconds)
    
    def get_cache_stats(self) -> dict:
        """Получает статистику кэша"""
        cache_files = list(self.cache_dir.glob("*.html"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            'total_files': len(cache_files),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_dir': str(self.cache_dir)
        }
    
    def clear_cache(self):
        """Очищает кэш"""
        for cache_file in self.cache_dir.glob("*.html"):
            cache_file.unlink()
        print(f"✅ Кэш очищен: {self.cache_dir}")
