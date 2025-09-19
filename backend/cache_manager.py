#!/usr/bin/env python3
"""
Менеджер кэширования для UFC Ranker
"""

import redis
import json
import pickle
from typing import Any, Optional, Union
from datetime import timedelta
import os
from functools import wraps


class CacheManager:
    """Менеджер кэширования с Redis"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', '6379')),
            db=int(os.getenv('REDIS_DB', '0')),
            password=os.getenv('REDIS_PASSWORD', ''),
            decode_responses=True
        )
        
        # Префиксы для разных типов данных
        self.prefixes = {
            'fighters': 'ufc:fighters:',
            'rankings': 'ufc:rankings:',
            'events': 'ufc:events:',
            'fights': 'ufc:fights:',
            'stats': 'ufc:stats:',
            'analytics': 'ufc:analytics:'
        }
    
    def get(self, key: str, prefix: str = '') -> Optional[Any]:
        """Получает значение из кэша"""
        try:
            full_key = f"{prefix}{key}"
            value = self.redis_client.get(full_key)
            
            if value:
                # Пробуем десериализовать как JSON
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    # Если не JSON, возвращаем как есть
                    return value
            
            return None
            
        except Exception as e:
            print(f"❌ Ошибка при получении из кэша: {e}")
            return None
    
    def set(self, key: str, value: Any, prefix: str = '', ttl: int = 3600) -> bool:
        """Сохраняет значение в кэш"""
        try:
            full_key = f"{prefix}{key}"
            
            # Сериализуем в JSON
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value, ensure_ascii=False)
            else:
                serialized_value = str(value)
            
            return self.redis_client.setex(full_key, ttl, serialized_value)
            
        except Exception as e:
            print(f"❌ Ошибка при сохранении в кэш: {e}")
            return False
    
    def delete(self, key: str, prefix: str = '') -> bool:
        """Удаляет значение из кэша"""
        try:
            full_key = f"{prefix}{key}"
            return bool(self.redis_client.delete(full_key))
        except Exception as e:
            print(f"❌ Ошибка при удалении из кэша: {e}")
            return False
    
    def delete_pattern(self, pattern: str, prefix: str = '') -> int:
        """Удаляет все ключи по паттерну"""
        try:
            full_pattern = f"{prefix}{pattern}"
            keys = self.redis_client.keys(full_pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"❌ Ошибка при удалении по паттерну: {e}")
            return 0
    
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
    
    def get_fight_stats(self, key: str) -> Optional[list]:
        """Получает статистику боев из кэша"""
        return self.get(key, self.prefixes['stats'])
    
    def set_fight_stats(self, key: str, value: list, ttl: int = 1800) -> bool:
        """Сохраняет статистику боев в кэш"""
        return self.set(key, value, self.prefixes['stats'], ttl)
    
    def get_analytics(self, key: str) -> Optional[dict]:
        """Получает аналитику из кэша"""
        return self.get(key, self.prefixes['analytics'])
    
    def set_analytics(self, key: str, value: dict, ttl: int = 7200) -> bool:
        """Сохраняет аналитику в кэш"""
        return self.set(key, value, self.prefixes['analytics'], ttl)
    
    def clear_all(self) -> bool:
        """Очищает весь кэш"""
        try:
            return self.redis_client.flushdb()
        except Exception as e:
            print(f"❌ Ошибка при очистке кэша: {e}")
            return False
    
    def clear_fighters(self) -> int:
        """Очищает кэш бойцов"""
        return self.delete_pattern('*', self.prefixes['fighters'])
    
    def clear_rankings(self) -> int:
        """Очищает кэш рейтингов"""
        return self.delete_pattern('*', self.prefixes['rankings'])
    
    def clear_events(self) -> int:
        """Очищает кэш событий"""
        return self.delete_pattern('*', self.prefixes['events'])
    
    def get_stats(self) -> dict:
        """Получает статистику кэша"""
        try:
            info = self.redis_client.info()
            return {
                'used_memory': info.get('used_memory_human', '0B'),
                'connected_clients': info.get('connected_clients', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'hit_rate': self._calculate_hit_rate(info)
            }
        except Exception as e:
            print(f"❌ Ошибка при получении статистики кэша: {e}")
            return {}
    
    def _calculate_hit_rate(self, info: dict) -> float:
        """Вычисляет процент попаданий в кэш"""
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses
        
        if total == 0:
            return 0.0
        
        return round((hits / total) * 100, 2)


# Глобальный экземпляр менеджера кэша
cache_manager = CacheManager()


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
