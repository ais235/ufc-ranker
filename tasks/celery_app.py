#!/usr/bin/env python3
"""
Celery приложение для фоновых задач UFC Ranker
"""

from celery import Celery
from celery.schedules import crontab
import os
from datetime import datetime

# Настройки Celery
broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Создаем Celery приложение
celery_app = Celery(
    'ufc_ranker',
    broker=broker_url,
    backend=result_backend,
    include=['tasks.data_tasks', 'tasks.analytics_tasks']
)

# Конфигурация Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут
    task_soft_time_limit=25 * 60,  # 25 минут
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Расписание задач
celery_app.conf.beat_schedule = {
    'update-rankings': {
        'task': 'tasks.data_tasks.update_rankings',
        'schedule': crontab(hour=6, minute=0),  # Каждый день в 6:00
    },
    'update-fighters': {
        'task': 'tasks.data_tasks.update_fighters',
        'schedule': crontab(hour=7, minute=0),  # Каждый день в 7:00
    },
    'update-events': {
        'task': 'tasks.data_tasks.update_events',
        'schedule': crontab(hour=8, minute=0),  # Каждый день в 8:00
    },
    'update-fight-stats': {
        'task': 'tasks.data_tasks.update_fight_stats',
        'schedule': crontab(hour=9, minute=0),  # Каждый день в 9:00
    },
    'generate-analytics': {
        'task': 'tasks.analytics_tasks.generate_daily_analytics',
        'schedule': crontab(hour=10, minute=0),  # Каждый день в 10:00
    },
    'cleanup-old-data': {
        'task': 'tasks.data_tasks.cleanup_old_data',
        'schedule': crontab(hour=2, minute=0, day_of_week=1),  # Каждый понедельник в 2:00
    },
}

# Настройки для разработки
if os.getenv('ENVIRONMENT') == 'development':
    celery_app.conf.update(
        task_always_eager=True,  # Выполнять задачи синхронно в разработке
        task_eager_propagates=True,
    )

if __name__ == '__main__':
    celery_app.start()

