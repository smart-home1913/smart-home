from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, Field

from db.automation import ConditionType, ReturnValueType, Operator
from models.base_model import Base


class Location(BaseModel):
    x: float = Field()
    y: float = Field()

    class Config:
        from_attributes = True
        populate_by_name = True


class GraphViewport(Location):
    zoom: float = Field()

    class Config:
        from_attributes = True
        populate_by_name = True


class AutomationNodeRequest(BaseModel):
    smart_controller_id: str = Field()
    action_id: str = Field()
    location: Location = Field()


class AutomationNodeUpdateRequest(BaseModel):
    smart_controller_id: str = Field()
    action_id: str = Field()
    location: Location = Field()


class AutomationNodeResponse(Base):
    unique_key: str = Field()
    smart_controller_id: str = Field()
    action_id: str = Field()
    location: Location = Field()


class AutomationEdgeConditionRequest(BaseModel):
    condition_type: ConditionType = Field()
    value_type: ReturnValueType = Field()
    operator: Operator = Field()
    value_number: Optional[float] = Field(default=None)
    value_boolean: Optional[bool] = Field(default=None)
    is_loop: bool = Field()

    class Config:
        from_attributes = True
        populate_by_name = True


class AutomationEdgeConditionUpdateRequest(BaseModel):
    id: str = Field()
    type: ConditionType = Field()
    value_type: ReturnValueType = Field()
    operator: Operator = Field()
    value_number: Optional[float] = Field(default=None)
    value_boolean: Optional[bool] = Field(default=None)


class AutomationEdgeConditionResponse(Base):
    type: ConditionType = Field()
    value_type: ReturnValueType = Field()
    operator: Operator = Field()
    value_number: Optional[float] = Field(default=None)
    value_boolean: Optional[bool] = Field(default=None)


class AutomationEdgeRequest(BaseModel):
    source: AutomationNodeResponse = Field()
    target: AutomationNodeResponse = Field()
    condition: AutomationEdgeConditionRequest = Field()


class AutomationEdgeUpdateRequest(BaseModel):
    id: str = Field()
    source: AutomationNodeResponse = Field()
    target: AutomationNodeResponse = Field()
    condition: AutomationEdgeConditionRequest = Field()


class AutomationEdgeResponse(Base):
    source: AutomationNodeResponse = Field()
    target: AutomationNodeResponse = Field()
    condition: AutomationEdgeConditionRequest = Field()


class AutomationRequest(BaseModel):
    name: str = Field()


class AutomationUpdateRequest(BaseModel):
    name: str = Field(default='')
    is_active: bool = Field()
    viewport: GraphViewport = Field()


class AutomationResponse(Base):
    name: str = Field()
    inserted_at: datetime = Field()
    nodes: List[AutomationNodeResponse] = Field()
    edges: List[AutomationEdgeResponse] = Field()
    is_active: bool = Field()
    viewport: GraphViewport = Field(default=GraphViewport(x=0.0, y=0.0, zoom=0.0))

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
