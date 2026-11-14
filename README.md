# websocket-chat

Чат на WebSocket (FastAPI) с рассылкой сообщений через Redis Pub/Sub.
Несколько инстансов приложения могут работать за балансировщиком: сообщение,
отправленное в одну реплику, получат клиенты этого чата на всех репликах.

## Как это работает

```
клиент ──ws──▶ /ws/chats/{chat_id} ──PUBLISH chat:{chat_id}──▶ Redis
                                                                 │ PSUBSCRIBE chat:*
клиент ◀──ws── WebSocketConnectionManager.send_msg ◀── RedisListener
```

1. Клиент подключается к `ws://<host>:<port>/ws/chats/{chat_id}`.
2. Входящее сообщение валидируется по `EventSchema` и публикуется в канал Redis `chat:{chat_id}`.
3. `RedisListener` в каждом инстансе подписан на `chat:*` и передаёт сообщение
   `WebSocketConnectionManager`, который рассылает его всем локальным подключениям чата.

Формат сообщения:

```json
{"type": "message.send", "payload": {"text": "привет"}}
```

Невалидные сообщения логируются и пропускаются, соединение не закрывается.

## Структура

```
src/
├── main.py                      # точка входа: python src/main.py --uvicorn
├── core/
│   ├── settings.py              # настройки из .env (pydantic-settings)
│   └── container.py             # DI-контейнер (punq), сборка зависимостей
├── entrypoints/uvicorn_run.py   # create_app, lifespan (запуск RedisListener), запуск uvicorn
├── infra/
│   ├── ws_manager.py            # WebSocketConnectionManager: подключения и рассылка
│   └── redis/
│       ├── client.py            # AsyncRedis
│       └── listener.py          # RedisListener: PSUBSCRIBE chat:*
└── transport/websocket/
    ├── handlers.py              # роут /ws/chats/{chat_id}
    └── schemas.py               # EventSchema, ErrorSchema
tests/
├── unit/                        # без внешних зависимостей
└── integration/                 # реальный Redis в Docker (Testcontainers)
```

Зависимости передаются через поля dataclass-ов и собираются в `core/container.py`.

## Требования

- Docker и Docker Compose
- [uv](https://docs.astral.sh/uv/) и Python 3.14+ — только для локальной разработки и тестов

## Запуск

```bash
cp .env.example .env
docker compose up -d --build
```

Поднимутся два контейнера:

| Сервис  | Контейнер              | Порт                 |
|---------|------------------------|----------------------|
| `app`   | `websocket-chat-app`   | `${APP_PORT}` (8000) |
| `redis` | `websocket-chat-redis` | `${REDIS_PORT}` (6379) |

`app` стартует после того, как Redis пройдёт healthcheck. Внутри compose-сети приложение
обращается к Redis по имени сервиса `redis` (`REDIS_HOST` и `APP_HOST` переопределяются
в `docker-compose.yml`).

```bash
docker compose logs -f app     # логи
docker compose down            # остановить
docker compose down -v         # остановить и удалить данные Redis
```

Проверка (например, через [websocat](https://github.com/vi/websocat)), в двух терминалах:

```bash
websocat ws://localhost:8000/ws/chats/1
```

## Настройка

Переменные в `.env` (шаблон — `.env.example`):

| Переменная   | По умолчанию | Описание                 |
|--------------|--------------|--------------------------|
| `APP_HOST`   | `0.0.0.0`    | хост uvicorn             |
| `APP_PORT`   | `8000`       | порт приложения          |
| `REDIS_HOST` | `localhost`  | хост Redis (вне Docker)  |
| `REDIS_PORT` | `6379`       | порт Redis               |

## Локальная разработка

```bash
uv sync
docker compose up -d redis
uv run python src/main.py --uvicorn
```

## Тесты и проверки

```bash
uv run pytest                       # все тесты
uv run pytest tests/unit            # только юнит-тесты
uv run pytest tests/integration     # интеграционные (нужен запущенный Docker)

uv run coverage run -m pytest && uv run coverage report

uv run ruff check .                 # линтер
uv run ruff format .                # форматирование
uv run mypy                         # проверка типов (strict)
```
