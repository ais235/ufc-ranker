#!/usr/bin/env python3
"""
Базовый класс для всех парсеров UFC
"""

import os
import time
import hashlib
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup


class BaseParser(ABC):
    """Базовый класс для всех парсеров"""
    
    def __init__(self, cache_dir: str = ".cache", delay: float = 0.75):
        self.cache_dir = cache_dir
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Создаем папку для кэша
        os.makedirs(cache_dir, exist_ok=True)
    
    def clean_text(self, text: Optional[str]) -> str:
        """Очищает текст от лишних символов"""
        if not text:
            return ''
        text = text.replace('\u00ad', '').replace('&shy;', '')
        return ' '.join(text.split()).strip()
    
    def cache_key(self, url: str) -> str:
        """Генерирует ключ кэша для URL"""
        return hashlib.sha1(url.encode('utf-8')).hexdigest()
    
    def read_cache(self, url: str) -> Optional[str]:
        """Читает данные из кэша"""
        key = self.cache_key(url)
        path = os.path.join(self.cache_dir, f'{key}.html')
        
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception:
                return None
        return None
    
    def write_cache(self, url: str, content: str) -> None:
        """Записывает данные в кэш"""
        key = self.cache_key(url)
        path = os.path.join(self.cache_dir, f'{key}.html')
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception:
            pass
    
    def fetch(self, url: str, use_cache: bool = True) -> Optional[str]:
        """Загружает страницу с кэшированием"""
        if use_cache:
            cached = self.read_cache(url)
            if cached:
                return cached
        
        try:
            response = self.session.get(url, timeout=12)
            response.raise_for_status()
            
            html = response.text.replace('&shy;', '').replace('\u00ad', '')
            
            if use_cache:
                self.write_cache(url, html)
            
            time.sleep(self.delay)
            return html
            
        except Exception as e:
            print(f"❌ Ошибка при загрузке {url}: {e}")
            return None
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """Парсит HTML с помощью BeautifulSoup"""
        return BeautifulSoup(html, 'html.parser')
    
    @abstractmethod
    def parse(self, *args, **kwargs) -> Any:
        """Основной метод парсинга - должен быть реализован в наследниках"""
        pass
    
    def safe_filename(self, name: str) -> str:
        """Создает безопасное имя файла"""
        import re
        name = name.lower()
        name = re.sub(r'[<>:"/\\|?*]', '_', name)
        name = re.sub(r'\s+', '_', name)
        return name
