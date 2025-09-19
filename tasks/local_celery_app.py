#!/usr/bin/env python3
"""
Упрощенная версия Celery для локальной разработки без Redis
"""

import os
import time
from datetime import datetime
from typing import Any, Callable, Dict
import threading
import queue


class LocalTask:
    """Локальная задача для выполнения"""
    
    def __init__(self, func: Callable, args: tuple = (), kwargs: dict = None):
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}
        self.id = f"{func.__name__}_{int(time.time())}"
        self.status = 'PENDING'
        self.result = None
        self.error = None
        self.created_at = datetime.now()
    
    def execute(self):
        """Выполняет задачу"""
        try:
            self.status = 'STARTED'
            self.result = self.func(*self.args, **self.kwargs)
            self.status = 'SUCCESS'
        except Exception as e:
            self.status = 'FAILURE'
            self.error = str(e)
            print(f"❌ Ошибка в задаче {self.id}: {e}")


class LocalCeleryApp:
    """Упрощенная версия Celery для локальной разработки"""
    
    def __init__(self):
        self.tasks = {}
        self.task_queue = queue.Queue()
        self.worker_thread = None
        self.running = False
        self.task_registry = {}
    
    def task(self, bind=False, max_retries=3):
        """Декоратор для регистрации задач"""
        def decorator(func):
            self.task_registry[func.__name__] = func
            
            def wrapper(*args, **kwargs):
                if bind:
                    # Добавляем self как первый аргумент
                    args = (self,) + args
                
                task = LocalTask(func, args, kwargs)
                self.tasks[task.id] = task
                self.task_queue.put(task)
                
                # Если worker не запущен, запускаем его
                if not self.running:
                    self.start_worker()
                
                return task
            
            return wrapper
        return decorator
    
    def start_worker(self):
        """Запускает worker в отдельном потоке"""
        if self.running:
            return
        
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        print("🔄 Локальный Celery worker запущен")
    
    def _worker_loop(self):
        """Основной цикл worker'а"""
        while self.running:
            try:
                # Получаем задачу из очереди с таймаутом
                task = self.task_queue.get(timeout=1)
                print(f"🔄 Выполняем задачу: {task.func.__name__}")
                task.execute()
                print(f"✅ Задача {task.func.__name__} выполнена")
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Ошибка в worker: {e}")
    
    def stop_worker(self):
        """Останавливает worker"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join()
        print("⏹️ Локальный Celery worker остановлен")
    
    def get_task_result(self, task_id: str) -> Dict[str, Any]:
        """Получает результат задачи"""
        task = self.tasks.get(task_id)
        if not task:
            return {'status': 'NOT_FOUND'}
        
        return {
            'id': task.id,
            'status': task.status,
            'result': task.result,
            'error': task.error,
            'created_at': task.created_at.isoformat()
        }
    
    def get_all_tasks(self) -> Dict[str, Dict[str, Any]]:
        """Получает все задачи"""
        return {task_id: self.get_task_result(task_id) for task_id in self.tasks}


# Глобальный экземпляр локального Celery
local_celery_app = LocalCeleryApp()


# Декораторы для совместимости с Celery
def task(bind=False, max_retries=3):
    """Декоратор для создания задач"""
    return local_celery_app.task(bind=bind, max_retries=max_retries)


# Имитация Celery Beat для планировщика
class LocalBeatScheduler:
    """Локальный планировщик задач"""
    
    def __init__(self):
        self.scheduled_tasks = []
        self.running = False
        self.scheduler_thread = None
    
    def add_periodic_task(self, schedule, task_func, name=None):
        """Добавляет периодическую задачу"""
        self.scheduled_tasks.append({
            'schedule': schedule,
            'task': task_func,
            'name': name or task_func.__name__,
            'last_run': None
        })
        print(f"📅 Добавлена периодическая задача: {name or task_func.__name__}")
    
    def start(self):
        """Запускает планировщик"""
        if self.running:
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        print("⏰ Локальный планировщик запущен")
    
    def _scheduler_loop(self):
        """Основной цикл планировщика"""
        while self.running:
            try:
                current_time = datetime.now()
                
                for task_info in self.scheduled_tasks:
                    # Простая логика для ежедневных задач в 6:00
                    if (current_time.hour == 6 and 
                        (task_info['last_run'] is None or 
                         task_info['last_run'].date() != current_time.date())):
                        
                        print(f"⏰ Запускаем запланированную задачу: {task_info['name']}")
                        task_info['task'].delay()
                        task_info['last_run'] = current_time
                
                time.sleep(60)  # Проверяем каждую минуту
                
            except Exception as e:
                print(f"❌ Ошибка в планировщике: {e}")
                time.sleep(60)
    
    def stop(self):
        """Останавливает планировщик"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        print("⏹️ Локальный планировщик остановлен")


# Глобальный экземпляр планировщика
beat_scheduler = LocalBeatScheduler()


# Имитация crontab для совместимости
class Crontab:
    """Имитация crontab для локальной разработки"""
    
    def __init__(self, hour=None, minute=None, day_of_week=None):
        self.hour = hour
        self.minute = minute
        self.day_of_week = day_of_week


# Функции для совместимости
def crontab(hour=None, minute=None, day_of_week=None):
    """Создает объект crontab"""
    return Crontab(hour=hour, minute=minute, day_of_week=day_of_week)


if __name__ == "__main__":
    # Тестируем локальный Celery
    @task
    def test_task(message):
        print(f"Тестовая задача: {message}")
        return f"Выполнено: {message}"
    
    # Запускаем тестовую задачу
    result = test_task("Привет, локальный Celery!")
    print(f"Результат: {result}")
    
    # Ждем выполнения
    time.sleep(2)
    
    # Показываем результат
    task_result = local_celery_app.get_task_result(result.id)
    print(f"Статус задачи: {task_result}")
