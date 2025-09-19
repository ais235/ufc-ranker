#!/usr/bin/env python3
"""
Локальный менеджер кэширования без Redis (для разработки)
"""

import json
import time
from typing import Any, Optional, Dict
from functools import wraps
import os


class LocalCacheManager:
    """Локальный менеджер кэширования с файловым хранилищем"""
    
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        # Префиксы для разных типов данных
        self.prefixes = {
            'fighters': 'ufc:fighters:',
            'rankings': 'ufc:rankings:',
            'events': 'ufc:events:',
            'fights': 'ufc:fights:',
            'stats': 'ufc:stats:',
            'analytics': 'ufc:analytics:'
        }
    
    def _get_cache_file(self, key: str, prefix: str = '') -> str:
        """Получает путь к файлу кэша"""
        safe_key = key.replace('/', '_').replace(':', '_')
        return os.path.join(self.cache_dir, f"{prefix}{safe_key}.json")
    
    def get(self, key: str, prefix: str = '') -> Optional[Any]:
        """Получает значение из кэша"""
        try:
            cache_file = self._get_cache_file(key, prefix)
            
            if not os.path.exists(cache_file):
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Проверяем TTL
            if 'expires_at' in data and time.time() > data['expires_at']:
                os.remove(cache_file)
                return None
            
            return data.get('value')
            
        except Exception as e:
            print(f"❌ Ошибка при получении из кэша: {e}")
            return None
    
    def set(self, key: str, value: Any, prefix: str = '', ttl: int = 3600) -> bool:
        """Сохраняет значение в кэш"""
        try:
            cache_file = self._get_cache_file(key, prefix)
            
            data = {
                'value': value,
                'expires_at': time.time() + ttl,
                'created_at': time.time()
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при сохранении в кэш: {e}")
            return False
    
    def delete(self, key: str, prefix: str = '') -> bool:
        """Удаляет значение из кэша"""
        try:
            cache_file = self._get_cache_file(key, prefix)
            if os.path.exists(cache_file):
                os.remove(cache_file)
                return True
            return False
        except Exception as e:
            print(f"❌ Ошибка при удалении из кэша: {e}")
            return False
    
    def clear_all(self) -> bool:
        """Очищает весь кэш"""
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, filename))
            return True
        except Exception as e:
            print(f"❌ Ошибка при очистке кэша: {e}")
            return False
    
    def get_fighters(self, key: str = 'all') -> Optional[list]:
        """Получает бойцов из кэша"""
        return self.get(key, self.prefixes['fighters'])
    
    def set_fighters(self, key: str, value: list, ttl: int = 3600) -> bool:
        """Сохраняет бойцов в кэш"""
        return self.set(key, value, self.prefixes['fighters'], ttl)
    
    def get_rankings(self, key: str) -> Optional[dict]:
        """Получает рейтинги из кэша"""
        return self.get(key, self.prefixes['rankings'])
    
    def set_rankings(self, key: str, value: dict, ttl: int = 1800) -> bool:
        """Сохраняет рейтинги в кэш"""
        return self.set(key, value, self.prefixes['rankings'], ttl)
    
    def get_events(self, key: str = 'all') -> Optional[list]:
        """Получает события из кэша"""
        return self.get(key, self.prefixes['events'])
    
    def set_events(self, key: str, value: list, ttl: int = 3600) -> bool:
        """Сохраняет события в кэш"""
        return self.set(key, value, self.prefixes['events'], ttl)
    
    def get_analytics(self, key: str) -> Optional[dict]:
        """Получает аналитику из кэша"""
        return self.get(key, self.prefixes['analytics'])
    
    def set_analytics(self, key: str, value: dict, ttl: int = 7200) -> bool:
        """Сохраняет аналитику в кэш"""
        return self.set(key, value, self.prefixes['analytics'], ttl)
    
    def get_stats(self) -> dict:
        """Получает статистику кэша"""
        try:
            cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json')]
            total_files = len(cache_files)
            
            # Подсчитываем размер кэша
            total_size = 0
            for filename in cache_files:
                filepath = os.path.join(self.cache_dir, filename)
                total_size += os.path.getsize(filepath)
            
            return {
                'total_files': total_files,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'cache_dir': self.cache_dir
            }
        except Exception as e:
            print(f"❌ Ошибка при получении статистики кэша: {e}")
            return {}


# Глобальный экземпляр менеджера кэша
cache_manager = LocalCacheManager()


def cached(prefix: str, ttl: int = 3600, key_func=None):
    """Декоратор для кэширования результатов функций"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Генерируем ключ кэша
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Пробуем получить из кэша
            cached_result = cache_manager.get(cache_key, prefix)
            if cached_result is not None:
                return cached_result
            
            # Выполняем функцию
            result = func(*args, **kwargs)
            
            # Сохраняем в кэш
            cache_manager.set(cache_key, result, prefix, ttl)
            
            return result
        return wrapper
    return decorator


def cache_fighters(ttl: int = 3600):
    """Декоратор для кэширования данных бойцов"""
    return cached(cache_manager.prefixes['fighters'], ttl)


def cache_rankings(ttl: int = 1800):
    """Декоратор для кэширования рейтингов"""
    return cached(cache_manager.prefixes['rankings'], ttl)


def cache_events(ttl: int = 3600):
    """Декоратор для кэширования событий"""
    return cached(cache_manager.prefixes['events'], ttl)


def cache_analytics(ttl: int = 7200):
    """Декоратор для кэширования аналитики"""
    return cached(cache_manager.prefixes['analytics'], ttl)
