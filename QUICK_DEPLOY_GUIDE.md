# 🚀 Быстрый деплой UFC Ranker на reg.ru

## ⚡ Экспресс-инструкция (30 минут)

### 1. Подготовка файлов (5 минут)

```bash
# Соберите фронтенд
cd frontend
npm run build
cd ..

# Проверьте что все файлы готовы
ls -la start_production.py requirements-prod.txt Procfile
```

### 2. Выбор способа деплоя

#### 🟢 Вариант A: Heroku (самый простой)

```bash
# Установите Heroku CLI
# Создайте аккаунт на heroku.com

# В корне проекта
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
git add .
git commit -m "Deploy to production"
git push heroku main

# Мигрируйте данные
heroku run python migrate_to_postgres.py
```

**Результат:** https://your-app-name.herokuapp.com

#### 🟡 Вариант B: reg.ru VPS

```bash
# 1. Закажите VPS на reg.ru
# 2. Подключитесь по SSH
ssh root@your-vps-ip

# 3. Установите зависимости
apt update && apt upgrade -y
apt install python3.11 python3.11-pip python3.11-venv postgresql nginx git -y

# 4. Создайте пользователя
adduser ufcranker
usermod -aG sudo ufcranker
su - ufcranker

# 5. Клонируйте проект
git clone https://github.com/your-username/ufc-ranker.git
cd ufc-ranker

# 6. Настройте окружение
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements-prod.txt

# 7. Настройте базу данных
sudo -u postgres psql
CREATE DATABASE ufc_ranker;
CREATE USER ufcranker WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ufc_ranker TO ufcranker;
\q

# 8. Мигрируйте данные
python migrate_to_postgres.py

# 9. Настройте сервис
sudo cp ufc-ranker.service.example /etc/systemd/system/ufc-ranker.service
sudo systemctl daemon-reload
sudo systemctl enable ufc-ranker
sudo systemctl start ufc-ranker

# 10. Настройте Nginx
sudo cp nginx.conf.example /etc/nginx/sites-available/ufc-ranker
sudo ln -s /etc/nginx/sites-available/ufc-ranker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# 11. Настройте SSL
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 3. Проверка работы

```bash
# Проверьте статус сервисов
sudo systemctl status ufc-ranker
sudo systemctl status nginx

# Проверьте API
curl http://localhost:8000/api/stats

# Проверьте сайт
curl https://your-domain.com
```

---

## 📋 Чек-лист деплоя

### Перед деплоем:
- [ ] Собрать фронтенд (`npm run build`)
- [ ] Проверить файлы: `start_production.py`, `requirements-prod.txt`
- [ ] Подготовить переменные окружения
- [ ] Создать резервную копию БД

### После деплоя:
- [ ] Сайт доступен по HTTPS
- [ ] API отвечает на запросы
- [ ] Карточки бойцов загружаются
- [ ] Рейтинги отображаются
- [ ] События загружаются

---

## 🆘 Быстрое решение проблем

### Проблема: Сайт не загружается
```bash
# Проверьте статус сервисов
sudo systemctl status ufc-ranker nginx

# Проверьте логи
sudo journalctl -u ufc-ranker -f
sudo tail -f /var/log/nginx/error.log
```

### Проблема: API не отвечает
```bash
# Проверьте подключение к БД
python -c "from database.production_config import test_connection; test_connection()"

# Проверьте порты
sudo netstat -tlnp | grep :8000
```

### Проблема: CORS ошибки
```bash
# Проверьте настройки CORS в backend/app.py
# Убедитесь что домен указан в ALLOWED_ORIGINS
```

---

## 💡 Советы

1. **Начните с Heroku** - самый простой способ
2. **Используйте готовые скрипты** - `deploy.sh`, `migrate_to_postgres.py`
3. **Настройте мониторинг** - логи, алерты
4. **Сделайте резервные копии** - БД, код, конфигурации

---

## 📞 Поддержка

- **Heroku:** https://devcenter.heroku.com
- **reg.ru:** https://help.reg.ru
- **Nginx:** https://nginx.org/en/docs/

**Удачи! 🚀**
