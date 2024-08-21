import time
from typing import List

from fastapi import APIRouter, HTTPException

from db.models import SmartController, Action
from models.smart_controller import SmartControllerRequest, SmartControllerResponse, SmartControllerUpdateRequest

router = APIRouter()


@router.post("/")
def create_smart_controller(smart_controller_request: SmartControllerRequest):
    actions = Action.objects(id__in=smart_controller_request.actions)
    if len(actions) != len(smart_controller_request.actions):
        raise HTTPException(status_code=404, detail="Some actions provided are not found")

    smart_controller = SmartController(
        name=smart_controller_request.name,
        address=smart_controller_request.address,
        actions=actions
    )

    smart_controller.save()
    return SmartControllerResponse.from_orm(smart_controller)


@router.get("/")
def get_smart_controllers() -> List[SmartControllerResponse]:
    smart_controllers = SmartController.objects()
    return [SmartControllerResponse.from_orm(smart_controller) for smart_controller in smart_controllers]


@router.get("/{smart_controller_id}")
def get_smart_controller(smart_controller_id: str):
    smart_controller = SmartController.objects(id=smart_controller_id).first()
    if not smart_controller:
        raise HTTPException(status_code=404, detail="Smart controller not found")

    return SmartControllerResponse.from_orm(smart_controller)


@router.patch("/")
def patch_smart_controller(smart_controller_request: SmartControllerUpdateRequest):
    smart_controller: SmartController = SmartController.objects(id=smart_controller_request.id).first()

    if not smart_controller:
        raise HTTPException(status_code=404, detail="Smart controller not found")

    if smart_controller_request.address != "":
        smart_controller.address = smart_controller_request.address
    if smart_controller_request.name != "":
        smart_controller.name = smart_controller_request.name
    if smart_controller_request.actions is not None:
        actions = Action.objects(id__in=smart_controller_request.actions)
        if len(actions) != len(smart_controller_request.actions):
            raise HTTPException(status_code=404, detail="Some actions provided are not found")
        smart_controller.actions = actions

    smart_controller.save()

    return SmartControllerResponse.from_orm(smart_controller)
