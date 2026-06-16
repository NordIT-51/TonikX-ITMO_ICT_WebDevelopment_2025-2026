# Отчёт по лабораторной работе №1: «Реализация серверного приложения FastAPI»

## Тема: «Попутчики» (Travel Companion API)

Сервис для поиска попутчиков в путешествия. Пользователи могут создавать поездки,
подавать заявки на участие, обмениваться сообщениями и оставлять отзывы.

---

## Модели базы данных

Используется PostgreSQL 18, ORM SQLAlchemy (синхронный).

| Таблица              | Описание          | Связи                                                                 |
|----------------------|-------------------|-----------------------------------------------------------------------|
| `users`              | Пользователи      | One-to-many с `trips`, `trip_applications`, `messages`, `reviews`    |
| `trips`              | Поездки           | One-to-many с `trip_applications`, `messages`, `reviews`             |
| `trip_applications`  | Заявки на участие | Ассоциативная сущность (many-to-many `users` ↔ `trips`) + поле `status` |
| `messages`           | Сообщения         | Привязка к поездке, отправитель/получатель (пользователи)            |
| `reviews`            | Отзывы            | Оценка попутчика, привязка к поездке                                 |

> **Дополнительное поле ассоциативной сущности:** `trip_applications.status`
> (`pending` / `accepted` / `rejected`) — характеризует состояние заявки.

---

## Схема подключения к БД (`app/database.py`)

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## Эндпоинты API (CRUD)

Базовый URL: `http://localhost:8000`  
Документация Swagger: `http://localhost:8000/docs`

### Пользователи

- `POST /users/register` — регистрация  
  Тело: `{"email": "...", "username": "...", "password": "..."}`
- `POST /users/login` — получение JWT (form-data: `username`, `password`)
- `GET /users/me` — профиль текущего пользователя *(требуется токен)*
- `GET /users/` — список всех пользователей *(требуется токен)*
- `PUT /users/change-password` — смена пароля *(требуется токен)*

### Поездки

- `POST /trips/` — создание поездки *(требуется токен)*
- `GET /trips/` — список поездок (фильтры: `destination`, `start_location`)
- `GET /trips/{id}` — поездка с вложенными `creator` и `applications`
- `PUT /trips/{id}` — обновление *(только создатель или админ)*
- `DELETE /trips/{id}` — удаление *(только создатель или админ)*

### Заявки (many-to-many)

- `POST /applications/` — подать заявку на участие в поездке
- `GET /applications/my` — мои заявки
- `GET /applications/for-trip/{trip_id}` — заявки на поездку *(только для создателя)*
- `PUT /applications/{id}` — изменить статус (принять / отклонить)

### Сообщения

- `POST /messages/` — отправить сообщение участнику поездки
- `GET /messages/trip/{trip_id}` — все сообщения поездки

### Отзывы

- `POST /reviews/` — оставить отзыв о попутчике
- `GET /reviews/user/{user_id}` — отзывы о пользователе

### Пример ответа с вложенными объектами

`GET /trips/1`:

```json
{
  "id": 1,
  "title": "Путешествие в Париж",
  "creator": { "id": 1, "username": "alice", "email": "alice@example.com" },
  "applications": [
    { "id": 2, "user_id": 2, "status": "accepted", "comment": "Хочу присоединиться!" }
  ]
}
```

---

## Инструкция по запуску

1. **Клонировать репозиторий:**

   ```bash
   git clone https://github.com/NordIT-51/TonikX-ITMO_ICT_WebDevelopment_2025-2026.git
   cd TonikX-ITMO_ICT_WebDevelopment_2025-2026/lab1
   ```

2. **Создать и активировать виртуальное окружение:**

   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/macOS
   .\venv\Scripts\activate    # Windows
   ```

3. **Установить зависимости:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Создать базу данных PostgreSQL:**

   ```sql
   CREATE DATABASE travel_companion;
   ```

5. **Создать файл `.env` с переменными:**

   ```text
   DATABASE_URL=postgresql://user:password@localhost/travel_companion
   SECRET_KEY=your_secret_key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

6. **Выполнить миграции Alembic:**

   ```bash
   alembic upgrade head
   ```

7. **Запустить приложение:**

   ```bash
   uvicorn app.main:app --reload
   ```

8. Открыть `http://localhost:8000/docs` для тестирования.

---

## Ссылки на выполненные практики

- **Практика 1.1** (базовое FastAPI + временная БД):
  [practice_1_1/](https://github.com/NordIT-51/TonikX-ITMO_ICT_WebDevelopment_2025-2026/tree/lab1/practice_1_1)
- **Практика 1.2** (SQLModel + PostgreSQL + Alembic):
  [practice_1_2/](https://github.com/NordIT-51/TonikX-ITMO_ICT_WebDevelopment_2025-2026/tree/lab1/practice_1_2)
- **Практика 1.3** (миграции через `.env`, `.gitignore`, добавление поля `level`):
  [practice_1_3/](https://github.com/NordIT-51/TonikX-ITMO_ICT_WebDevelopment_2025-2026/tree/lab1/practice_1_3)

---

## Авторизация и безопасность

- Пароли хэшируются с помощью `bcrypt`.
- JWT-токены генерируются через `python-jose` (HS256).
- Защита эндпоинтов реализована через `OAuth2PasswordBearer`.
- При обращении без токена возвращается `401 Unauthorized`.

---

## Заключение

Все требования лабораторной работы выполнены: 5 таблиц, связи one-to-many и
many-to-many (с дополнительным полем), CRUD, GET с вложенными объектами,
миграции Alembic, типизация, модульная структура, JWT-авторизация.