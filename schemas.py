"""Pydantic schemas = the API's contract. They validate input and shape output."""
from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

Priority = Literal["low", "medium", "high"]
Status = Literal["open", "done"]


class MachineCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    location: str = Field(default="", max_length=100)


class MachineOut(MachineCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    priority: Priority = "medium"
    due_date: Optional[date] = None


class TaskUpdate(BaseModel):
    """PATCH body: every field optional, only sent fields are changed."""
    title: Optional[str] = Field(default=None, min_length=3, max_length=200)
    priority: Optional[Priority] = None
    status: Optional[Status] = None
    due_date: Optional[date] = None


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    machine_id: int
    title: str
    priority: Priority
    status: Status
    due_date: Optional[date]
    created_at: datetime


class Stats(BaseModel):
    machines: int
    open_tasks: int
    done_tasks: int
    overdue_tasks: int
