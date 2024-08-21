from typing import List, Optional

from pydantic import BaseModel, Field

from models.action import ActionResponse
from models.base_model import Base


class SmartControllerRequest(BaseModel):
    name: str
    address: str
    actions: List[str]


class SmartControllerUpdateRequest(BaseModel):
    id: str
    name: str = Field(default='')
    address: str = Field(default='')
    actions: Optional[List[str]] = Field(default=None)


class SmartControllerResponse(Base):
    name: str
    address: str
    actions: List[ActionResponse]
