#!/usr/bin/env python3
"""
Скрипт проверки настроек домена voltfighters.ru
"""
import requests
import socket
import ssl
import time
from urllib.parse import urlparse

def check_dns(domain):
    """Проверяет DNS записи"""
    print(f"Проверка DNS для {domain}...")
    
    try:
        # Проверяем A запись
        ip = socket.gethostbyname(domain)
        print(f"✓ A запись: {domain} -> {ip}")
        
        # Проверяем что IP принадлежит PythonAnywhere
        if ip == "185.199.108.153":
            print("✓ IP адрес принадлежит PythonAnywhere")
            return True
        else:
            print(f"⚠ IP адрес {ip} не принадлежит PythonAnywhere")
            return False
            
    except socket.gaierror as e:
        print(f"✗ Ошибка DNS: {e}")
        return False

def check_ssl(domain):
    """Проверяет SSL сертификат"""
    print(f"Проверка SSL для {domain}...")
    
    try:
        # Проверяем HTTPS соединение
        response = requests.get(f"https://{domain}", timeout=10)
        print(f"✓ HTTPS соединение работает: {response.status_code}")
        
        # Проверяем SSL сертификат
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                print(f"✓ SSL сертификат действителен")
                print(f"  Субъект: {cert.get('subject', 'N/A')}")
                return True
                
    except requests.exceptions.RequestException as e:
        print(f"✗ Ошибка HTTPS: {e}")
        return False
    except ssl.SSLError as e:
        print(f"✗ Ошибка SSL: {e}")
        return False
    except Exception as e:
        print(f"✗ Общая ошибка: {e}")
        return False

def check_website(domain):
    """Проверяет работу сайта"""
    print(f"Проверка работы сайта {domain}...")
    
    urls_to_check = [
        f"https://{domain}",
        f"https://{domain}/api/fighters",
        f"https://{domain}/docs"
    ]
    
    results = []
    
    for url in urls_to_check:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✓ {url} - работает")
                results.append(True)
            else:
                print(f"⚠ {url} - статус {response.status_code}")
                results.append(False)
        except requests.exceptions.RequestException as e:
            print(f"✗ {url} - ошибка: {e}")
            results.append(False)
    
    return all(results)

def check_cors(domain):
    """Проверяет CORS настройки"""
    print(f"Проверка CORS для {domain}...")
    
    try:
        # Проверяем CORS заголовки
        response = requests.options(f"https://{domain}/api/fighters", timeout=10)
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        
        print("CORS заголовки:")
        for header, value in cors_headers.items():
            if value:
                print(f"✓ {header}: {value}")
            else:
                print(f"⚠ {header}: не найден")
        
        return cors_headers['Access-Control-Allow-Origin'] is not None
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Ошибка проверки CORS: {e}")
        return False

def main():
    """Главная функция"""
    domain = "voltfighters.ru"
    
    print("=" * 60)
    print(f"Проверка настроек домена {domain}")
    print("=" * 60)
    
    # Проверяем DNS
    dns_ok = check_dns(domain)
    print()
    
    # Проверяем SSL
    ssl_ok = check_ssl(domain)
    print()
    
    # Проверяем работу сайта
    website_ok = check_website(domain)
    print()
    
    # Проверяем CORS
    cors_ok = check_cors(domain)
    print()
    
    # Итоговый результат
    print("=" * 60)
    print("ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print("=" * 60)
    
    if dns_ok:
        print("✓ DNS настроен правильно")
    else:
        print("✗ Проблемы с DNS")
    
    if ssl_ok:
        print("✓ SSL сертификат работает")
    else:
        print("✗ Проблемы с SSL")
    
    if website_ok:
        print("✓ Сайт работает")
    else:
        print("✗ Проблемы с сайтом")
    
    if cors_ok:
        print("✓ CORS настроен")
    else:
        print("✗ Проблемы с CORS")
    
    print()
    
    if all([dns_ok, ssl_ok, website_ok, cors_ok]):
        print("🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
        print(f"🌐 Ваш сайт доступен по адресу: https://{domain}")
    else:
        print("⚠️ ЕСТЬ ПРОБЛЕМЫ, ТРЕБУЕТСЯ ИСПРАВЛЕНИЕ")
        print("📖 Проверьте инструкцию в DOMAIN_SETUP_GUIDE.md")

if __name__ == "__main__":
    main()
