from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"

class TaskCreate(BaseModel):
    title: str = Field(..., example="Finish project")
    description: Optional[str] = Field(None, example="Complete the technical test")
    status: Optional[TaskStatus] = Field(TaskStatus.pending, example="pending")
    assigned_to: Optional[str] = Field(None, example="john@example.com")
    due_date: Optional[datetime] = Field(None, example="2025-08-08")

class TaskInDB(TaskCreate):
    id: str = Field(..., alias="_id")

class TaskUpdate(BaseModel):
    title: str = Field(..., example="Finish project")
    description: Optional[str] = Field(None, example="Complete the technical test")
    status: Optional[str] = Field(example="completed")
    assigned_to: Optional[str] = Field(None, example="john@example.com")

class TaskResponse(TaskCreate):
    id: str

class TaskDelete(BaseModel):
    deleted_id: str

