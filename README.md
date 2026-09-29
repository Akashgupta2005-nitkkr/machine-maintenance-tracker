# Machine Maintenance Tracker

A small full-stack web app to track machines and the maintenance jobs they need.
Built with **Python, FastAPI, SQLAlchemy (SQLite) and plain HTML/JavaScript**, with automated tests, Docker and a CI pipeline.

## Features
- Add and delete machines (unique names enforced)
- Add maintenance tasks with priority (low / medium / high) and due date
- Mark tasks done or reopen them, filter by status and priority
- Dashboard: machine count, open, done and overdue tasks
- Input validation on both server and browser; safe rendering (no `innerHTML`)

## Architecture
```
Browser (static/index.html)  --fetch/JSON-->  FastAPI (app/main.py)
                                                 |  validates with Pydantic (app/schemas.py)
                                                 |  talks to DB with SQLAlchemy (app/models.py)
                                                 v
                                             SQLite file
```

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
- App: http://localhost:8000
- Auto-generated API docs (Swagger): http://localhost:8000/docs

## Run tests
```bash
pytest -v
```

## Run with Docker
```bash
docker build -t maintenance-tracker .
docker run -p 8000:8000 maintenance-tracker
```

## API summary
| Method | Path | Purpose |
|---|---|---|
| GET | /health | Liveness check |
| POST / GET | /machines | Create / list machines |
| DELETE | /machines/{id} | Delete machine and its tasks |
| POST | /machines/{id}/tasks | Add a task to a machine |
| GET | /tasks?status=&priority=&machine_id= | List tasks with optional filters |
| PATCH / DELETE | /tasks/{id} | Update (partial) / delete a task |
| GET | /stats | Dashboard numbers |

## How I used AI while building this
_Fill this in honestly after you build it yourself. Example points:_
- Used an AI assistant to explain FastAPI dependency injection, then rewrote the endpoints myself.
- Asked AI to suggest test cases; ran them and fixed anything wrong (add a real example here).
- Checked every AI suggestion by running it and reading the docs before keeping it.

## Ideas for next steps
- Add user login (JWT)
- Switch SQLite to PostgreSQL
- Deploy to Render / Railway / Azure App Service
- Add an AI feature: summarise open tasks using the Claude API
