from typing import Optional

from pydantic import BaseModel, Field

from db.models import TaskType
from models.action import ActionResponse
from models.base_model import Base
from models.smart_controller import SmartControllerResponse


class TaskRequest(BaseModel):
    type: TaskType
    action_id: str
    smart_controller_id: str
    minute: int
    hour: int
    week_day: int
    month_day: int


class TaskUpdateRequest(BaseModel):
    id: str
    type: Optional[TaskType] = Field(default=None)
    action: Optional[str] = Field(default=None)
    minute: Optional[int] = Field(default=None)
    hour: Optional[int] = Field(default=None)
    week_day: Optional[int] = Field(default=None)
    month_day: Optional[int] = Field(default=None)


class TaskResponse(Base):
    type: TaskType
    action: ActionResponse
    smart_controller: SmartControllerResponse
    minute: int
    hour: int
    week_day: int
    month_day: int
