from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TaskMetadata(BaseModel):
    task_id: str
    task_type: str = Field(description="Type of task, e.g., 'rate_limiting'")
    description: str
    endpoint: Optional[str] = None
    acceptance_criteria: list[str] = Field(default_factory=list)


class Task(BaseModel):
    metadata: TaskMetadata
    created_at: datetime = Field(default_factory=datetime.now)
