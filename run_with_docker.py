#!/usr/bin/env python3
"""
Скрипт для запуска UFC Ranker с Docker (если доступен)
"""

import subprocess
import sys
import os
from pathlib import Path


def check_docker():
    """Проверяет, установлен ли Docker"""
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Docker найден: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker не найден. Установите Docker для использования контейнеров.")
        return False


def check_docker_compose():
    """Проверяет, установлен ли Docker Compose"""
    try:
        result = subprocess.run(['docker-compose', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Docker Compose найден: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker Compose не найден. Установите Docker Compose.")
        return False


def run_docker_services():
    """Запускает Docker сервисы"""
    print("🐳 Запуск Docker сервисов...")
    
    try:
        # Запускаем PostgreSQL и Redis
        subprocess.run([
            'docker-compose', '-f', 'docker-compose.local.yml', 'up', '-d', 'postgres', 'redis'
        ], check=True)
        
        print("✅ PostgreSQL и Redis запущены")
        
        # Ждем немного для инициализации
        import time
        print("⏳ Ожидание инициализации сервисов...")
        time.sleep(10)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при запуске Docker сервисов: {e}")
        return False


def run_enhanced_parsers_with_docker():
    """Запускает улучшенные парсеры с Docker сервисами"""
    print("🚀 Запуск улучшенных парсеров с Docker...")
    
    # Устанавливаем переменные окружения для PostgreSQL
    os.environ['DATABASE_URL'] = 'postgresql://ufc_ranker:ufc_ranker_password@localhost:5432/ufc_ranker'
    os.environ['REDIS_URL'] = 'redis://localhost:6379/0'
    os.environ['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
    os.environ['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
    
    # Запускаем улучшенные парсеры
    try:
        subprocess.run([sys.executable, 'run_enhanced_parsers.py'], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при запуске парсеров: {e}")
        return False


def stop_docker_services():
    """Останавливает Docker сервисы"""
    print("🛑 Остановка Docker сервисов...")
    
    try:
        subprocess.run([
            'docker-compose', '-f', 'docker-compose.local.yml', 'down'
        ], check=True)
        print("✅ Docker сервисы остановлены")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при остановке Docker сервисов: {e}")
        return False


def main():
    """Главная функция"""
    print("🐳 UFC Ranker - Запуск с Docker")
    print("=" * 40)
    
    # Проверяем Docker
    if not check_docker():
        print("\n💡 Для использования Docker установите Docker Desktop")
        print("   Скачать можно с: https://www.docker.com/products/docker-desktop")
        return 1
    
    if not check_docker_compose():
        print("\n💡 Docker Compose обычно входит в состав Docker Desktop")
        return 1
    
    try:
        # Запускаем Docker сервисы
        if not run_docker_services():
            return 1
        
        # Запускаем улучшенные парсеры
        if not run_enhanced_parsers_with_docker():
            return 1
        
        print("\n🎉 UFC Ranker успешно запущен с Docker!")
        print("\n📊 Доступные сервисы:")
        print("  - PostgreSQL: localhost:5432")
        print("  - Redis: localhost:6379")
        print("  - API: localhost:8000 (если запущен backend)")
        
        input("\n⏸️ Нажмите Enter для остановки...")
        
    except KeyboardInterrupt:
        print("\n⏹️ Остановка по запросу пользователя...")
    
    finally:
        # Останавливаем Docker сервисы
        stop_docker_services()
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
