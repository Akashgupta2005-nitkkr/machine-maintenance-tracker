"""Machine Maintenance Tracker - a small REST API built with FastAPI."""
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas
from .database import Base, engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # create tables on startup
    yield


app = FastAPI(title="Machine Maintenance Tracker", version="1.0.0", lifespan=lifespan)


@app.get("/health")
def health():
    """Used by Docker / cloud platforms to check the app is alive."""
    return {"status": "ok"}


# ---------- Machines ----------
@app.post("/machines", response_model=schemas.MachineOut, status_code=201)
def create_machine(payload: schemas.MachineCreate, db: Session = Depends(get_db)):
    machine = models.Machine(**payload.model_dump())
    db.add(machine)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A machine with this name already exists")
    db.refresh(machine)
    return machine


@app.get("/machines", response_model=list[schemas.MachineOut])
def list_machines(db: Session = Depends(get_db)):
    return db.scalars(select(models.Machine).order_by(models.Machine.name)).all()


@app.delete("/machines/{machine_id}", status_code=204)
def delete_machine(machine_id: int, db: Session = Depends(get_db)):
    machine = db.get(models.Machine, machine_id)
    if machine is None:
        raise HTTPException(status_code=404, detail="Machine not found")
    db.delete(machine)
    db.commit()


# ---------- Tasks ----------
@app.post("/machines/{machine_id}/tasks", response_model=schemas.TaskOut, status_code=201)
def create_task(machine_id: int, payload: schemas.TaskCreate, db: Session = Depends(get_db)):
    if db.get(models.Machine, machine_id) is None:
        raise HTTPException(status_code=404, detail="Machine not found")
    task = models.Task(machine_id=machine_id, **payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.get("/tasks", response_model=list[schemas.TaskOut])
def list_tasks(
    status: Optional[schemas.Status] = None,
    priority: Optional[schemas.Priority] = None,
    machine_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Optional filters: /tasks?status=open&priority=high"""
    query = select(models.Task)
    if status:
        query = query.where(models.Task.status == status)
    if priority:
        query = query.where(models.Task.priority == priority)
    if machine_id:
        query = query.where(models.Task.machine_id == machine_id)
    return db.scalars(query.order_by(models.Task.due_date.is_(None), models.Task.due_date)).all()


@app.patch("/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, payload: schemas.TaskUpdate, db: Session = Depends(get_db)):
    task = db.get(models.Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(models.Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()


# ---------- Dashboard numbers ----------
@app.get("/stats", response_model=schemas.Stats)
def stats(db: Session = Depends(get_db)):
    T = models.Task
    count = lambda *conds: db.scalar(select(func.count()).select_from(T).where(*conds)) or 0
    return schemas.Stats(
        machines=db.scalar(select(func.count()).select_from(models.Machine)) or 0,
        open_tasks=count(T.status == "open"),
        done_tasks=count(T.status == "done"),
        overdue_tasks=count(T.status == "open", T.due_date < date.today()),
    )


# Serve the frontend. Must be mounted LAST so it doesn't shadow the API routes.
app.mount("/", StaticFiles(directory=Path(__file__).parent.parent / "static", html=True), name="static")
