#!/usr/bin/env python3
"""
Скрипт для запуска улучшенных парсеров UFC Ranker
"""

import sys
import os
from datetime import datetime

# Добавляем корневую папку в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parsers.data_source_manager import DataSourceManager
from database.local_config import init_database
from tasks.local_data_tasks import setup_periodic_tasks, local_celery_app, beat_scheduler


def main():
    """Главная функция для запуска улучшенных парсеров"""
    print("🚀 UFC Ranker - Запуск улучшенных парсеров")
    print("=" * 50)
    print(f"⏰ Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 1. Инициализируем базу данных
        print("\n📊 Инициализация базы данных...")
        init_database()
        print("✅ База данных готова")
        
        # 2. Запускаем worker для фоновых задач
        print("\n🔄 Запуск фоновых задач...")
        local_celery_app.start_worker()
        
        # 3. Настраиваем периодические задачи
        print("\n📅 Настройка периодических задач...")
        setup_periodic_tasks()
        beat_scheduler.start()
        
        # 4. Запускаем менеджер источников данных
        print("\n🔄 Инициализация менеджера источников данных...")
        manager = DataSourceManager()
        
        # 5. Получаем все данные с приоритетных источников
        print("\n📥 Получение данных с приоритетных источников...")
        results = manager.update_all_data()
        
        # 6. Показываем статистику
        print("\n📊 Статистика обновления:")
        for data_type, data in results.items():
            if isinstance(data, dict) and 'status' in data:
                status_icon = "✅" if data.get('status') == 'success' else "❌"
                print(f"  {status_icon} {data_type}: {data.get('status', 'unknown')}")
            elif isinstance(data, list):
                print(f"  ✅ {data_type}: {len(data)} записей")
            elif isinstance(data, dict):
                print(f"  ✅ {data_type}: {len(data)} категорий")
        
        # 7. Показываем статус источников
        print("\n🔍 Статус источников данных:")
        sources_status = results.get('sources_status', {})
        for source_name, status in sources_status.items():
            enabled = "✅" if status.get('enabled') else "❌"
            success_rate = status.get('success_rate', 0)
            print(f"  {enabled} {source_name}: {success_rate:.1%} успешность")
        
        # 8. Показываем статистику задач
        print("\n📈 Статистика фоновых задач:")
        all_tasks = local_celery_app.get_all_tasks()
        if all_tasks:
            for task_id, task_info in all_tasks.items():
                status_icon = "✅" if task_info['status'] == 'SUCCESS' else "❌" if task_info['status'] == 'FAILURE' else "🔄"
                print(f"  {status_icon} {task_info.get('id', 'unknown')}: {task_info['status']}")
        else:
            print("  ℹ️ Нет выполненных задач")
        
        print("\n🎉 Улучшенные парсеры успешно запущены!")
        print("\n💡 Доступные команды:")
        print("  - Парсеры работают в фоновом режиме")
        print("  - Данные обновляются автоматически")
        print("  - Для остановки нажмите Ctrl+C")
        
        # 9. Ждем пользовательского ввода для остановки
        try:
            input("\n⏸️ Нажмите Enter для остановки...")
        except KeyboardInterrupt:
            print("\n⏹️ Остановка по запросу пользователя...")
        
    except Exception as e:
        print(f"\n❌ Ошибка при запуске улучшенных парсеров: {e}")
        return 1
    
    finally:
        # Останавливаем все сервисы
        print("\n🛑 Остановка сервисов...")
        beat_scheduler.stop()
        local_celery_app.stop_worker()
        print("✅ Все сервисы остановлены")
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
