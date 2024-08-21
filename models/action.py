from typing import Optional

from pydantic import BaseModel, Field

from models.base_model import Base


class ActionRequest(BaseModel):
    name: str = Field()
    path: str = Field()
    opposite_action_id: Optional[str] = Field(default='')
    description: str = Field()
    is_sensor: bool = Field(default=False)


class ActionUpdateRequest(BaseModel):
    id: str = Field()
    name: str = Field(default='')
    path: str = Field(default='')
    opposite_action_id: str = Field(default='')
    description: str = Field(default='')
    is_sensor: bool = Field(default=None)


class ActionResponse(Base):
    name: str = Field()
    path: str = Field()
    opposite_action_id: str = Field()
    description: str = Field()
    is_sensor: bool = Field(default=None)
