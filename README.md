# Athlete Status Bot 🏋️‍♂🚴‍♀️

Telegram-бот для щоденного моніторингу готовності спортсмена до тренування. Бот проводить просте опитування, фіксує відповіді в базі даних і видає рекомендації.

## 📦 Особливості

- ✅ Щоденний чек-ін опитувальник для оцінки стану
- 💾 Збереження результатів у PostgreSQL
- ⏰ Щоденна автоматична розсилка через APScheduler
- 📊 Потенціал для тижневої/місячної статистики
- 🔐 Підтримка багатьох користувачів

## 🚀 Як запустити

### 1. Клонувати репозиторій

```bash
git clone https://github.com/ValkoVolodya/athlete_status.git
cd athlete_status
```

### 2. Запустити Docker
Переконайтесь, що у вас встановлений Docker та Docker Compose

```bash
docker-compose up --build
```

### 3. Налаштувати змінні середовища
Створіть .env файл або налаштуйте змінні в docker-compose.yml:

```env
TELEGRAM_BOT_TOKEN=your_token_here
POSTGRES_DB=athlete_status
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
DATABASE_URL=postgresql://postgres:password@db:5432/athlete_status
```

### 4. Застосувати міграції

```bash
docker-compose exec bot yoyo apply --database $DATABASE_URL --path ./migrations
```

## 🛠 Структура проекту
```text
.
├── bot/                # Логіка Telegram-бота
├── scheduler/          # Планувальник щоденних задач (APScheduler)
├── migrations/         # SQL-міграції для бази
├── docker-compose.yml  # Контейнери бота та бази даних
├── .env                # Змінні середовища
```

## 🧠 Технології

* Python 3.11+

* python-telegram-bot v20+

* PostgreSQL

* asyncpg

* yoyo-migrations

* APScheduler

* Docker + Docker Compose

## 🧪 Плани на розвиток

* 📅 Відображення календаря тренувань

* 📈 Тижнева/місячна аналітика

* 📥 Експорт у CSV

* 🔐 Адмінка для аналізу даних

* 🗣 Підтримка декількох мов
