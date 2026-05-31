# BirthdayBuddy

Личный веб-сервис для учета дней рождения друзей: добавление друзей с датой
рождения, список ближайших ДР (с кэшем в Redis), напоминания.

## Стек

Python 3.12, Flask, SQLAlchemy, PostgreSQL 16, Redis 7, pytest, gunicorn.

## Локальный запуск (для разработки)

```bash
pip install -r requirements-dev.txt
python -m app.main            # http://127.0.0.1:8000
```

По умолчанию используется SQLite. Для PostgreSQL/Redis задай переменные из
`.env.example`.

## Тесты, линтер, безопасность

```bash
black --check .     # форматирование
flake8 .            # линтер
bandit -r app -ll   # статический анализ безопасности
pytest -v           # модульные тесты
```

## CI/CD

Пайплайн `.github/workflows/ci.yml` запускается на каждый PR и push в `main`
и состоит из трех последовательных этапов: Lint -> Test -> Security.

## Эндпоинты

| Метод | Путь | Назначение |
| --- | --- | --- |
| GET | `/` | Страница со списком друзей |
| GET | `/health` | Проверка живости |
| GET | `/api/friends` | Список друзей |
| POST | `/api/friends` | Добавить друга (JSON: name, birth_date) |
| GET | `/api/upcoming` | Ближайшие ДР на 30 дней (кэш Redis) |
