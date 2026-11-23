# Taskich

Учебный менеджер задач и проектов. В проекте реализованы паттерны GoF, Repository, Service Layer, Unit of Work (SQLAlchemy Session), Pydantic DTO, FastAPI и минимальный интерфейс Jinja2.

## Запуск

Требуется Python 3.11 или новее.

```bash
pip install -e .
python main.py
```

Если используете uv, выполните `uv sync`, затем `uv run python main.py`.

При первом запуске автоматически создаётся SQLite-база `taskich.db` и добавляются демонстрационные пользователи, проекты и задачи. При последующих запусках данные сохраняются.

Откройте:
- UI: http://127.0.0.1:8000/
- Swagger API: http://127.0.0.1:8000/docs

## API

- `GET /api/tasks` — список задач; поддерживает `query`, `status`, `priority`, `project_id`, `assignee_id`, `tags`, `strategy` (`text` или `tag`).
- `POST /api/tasks` — создание задачи.
- `GET /api/tasks/{task_id}` — получение задачи.
- `PATCH /api/tasks/{task_id}` — изменение задачи.
- `DELETE /api/tasks/{task_id}` — удаление задачи.
- `GET/POST /api/projects` — просмотр и создание проектов.
- `GET/POST /api/users` — просмотр и создание пользователей.
- `GET/POST /api/filters`, `DELETE /api/filters/{name}` — сохранённые фильтры.
- `GET /api/filters/{name}/tasks` — применение сохранённого фильтра.

## Применённые паттерны

- **Repository:** для каждой сущности есть абстрактный контракт `ABC`, реализация `InMemory...Repository` и реализация `SqlAlchemy...Repository`. Сервисный слой зависит от интерфейса репозитория через Unit of Work, а не от деталей SQL-запросов.
- **Service Layer:** `TaskService` и `CatalogService` содержат бизнес-операции.
- **Unit of Work:** `SqlAlchemyUnitOfWork` управляет одной SQLAlchemy Session и транзакцией на операцию.
- **DTO:** `dtos/requests.py` и `dtos/responses.py` описывают контракт API.
- **Strategy (GoF):** `TextSearchStrategy` и `TagSearchStrategy` реализуют взаимозаменяемые алгоритмы поиска.
- **Factory Method (GoF):** `SearchStrategyFactory` создаёт выбранную стратегию поиска, не связывая сервис с конкретными классами стратегий.

## Структура

```text
src/taskich/
├── api/                 # FastAPI-маршруты и Depends-провайдеры
├── database/            # SQLAlchemy, ORM-модели и Unit of Work
├── dtos/                # Pydantic-схемы запросов и ответов
├── models/              # Доменные модели по сущностям
├── patterns/            # GoF Strategy и Factory Method
├── repositories/        # ABC + InMemory + SqlAlchemy по сущностям
├── services/            # Бизнес-логика (task.py, catalog.py)
├── templates/           # Jinja2
└── static/              # CSS
```

Стратегия поиска типизирована перечислением `SearchStrategyType` (`StrEnum`). Зависимости FastAPI описаны через `Annotated[..., Depends(...)]`.
