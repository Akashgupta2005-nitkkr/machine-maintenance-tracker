"""Automated tests. Each test gets a fresh in-memory database."""
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)  # no "with": skips startup, so no real DB file is touched
    app.dependency_overrides.clear()


def make_machine(client, name="Lathe 1", location="Bay A"):
    return client.post("/machines", json={"name": name, "location": location})


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_create_and_list_machines(client):
    res = make_machine(client)
    assert res.status_code == 201
    assert res.json()["name"] == "Lathe 1"
    assert len(client.get("/machines").json()) == 1


def test_duplicate_machine_name_rejected(client):
    make_machine(client)
    assert make_machine(client).status_code == 409


def test_machine_validation(client):
    res = client.post("/machines", json={"name": "x"})  # too short
    assert res.status_code == 422


def test_task_needs_existing_machine(client):
    res = client.post("/machines/999/tasks", json={"title": "Oil change"})
    assert res.status_code == 404


def test_task_defaults_and_invalid_priority(client):
    mid = make_machine(client).json()["id"]
    ok = client.post(f"/machines/{mid}/tasks", json={"title": "Oil change"})
    assert ok.status_code == 201
    assert ok.json()["priority"] == "medium" and ok.json()["status"] == "open"
    bad = client.post(f"/machines/{mid}/tasks", json={"title": "Oil change", "priority": "urgent"})
    assert bad.status_code == 422


def test_filter_tasks(client):
    mid = make_machine(client).json()["id"]
    client.post(f"/machines/{mid}/tasks", json={"title": "Check belt", "priority": "high"})
    client.post(f"/machines/{mid}/tasks", json={"title": "Clean filter", "priority": "low"})
    high = client.get("/tasks", params={"priority": "high"}).json()
    assert [t["title"] for t in high] == ["Check belt"]


def test_update_task_partial(client):
    mid = make_machine(client).json()["id"]
    tid = client.post(f"/machines/{mid}/tasks", json={"title": "Check belt"}).json()["id"]
    res = client.patch(f"/tasks/{tid}", json={"status": "done"})
    assert res.json()["status"] == "done"
    assert res.json()["title"] == "Check belt"  # untouched field unchanged


def test_stats_counts_overdue(client):
    mid = make_machine(client).json()["id"]
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    client.post(f"/machines/{mid}/tasks", json={"title": "Late job", "due_date": yesterday})
    client.post(f"/machines/{mid}/tasks", json={"title": "Future job"})
    s = client.get("/stats").json()
    assert s == {"machines": 1, "open_tasks": 2, "done_tasks": 0, "overdue_tasks": 1}


def test_deleting_machine_deletes_its_tasks(client):
    mid = make_machine(client).json()["id"]
    client.post(f"/machines/{mid}/tasks", json={"title": "Check belt"})
    assert client.delete(f"/machines/{mid}").status_code == 204
    assert client.get("/tasks").json() == []
