from typing import List, Optional

from fastapi import APIRouter, HTTPException
from mongoengine import NotUniqueError, Q

from db.models import Action, SmartController
from db.scheduled_task import ScheduledTask
from models.action import ActionRequest, ActionResponse, ActionUpdateRequest
from tools.action_runner import run
from tools.action_runner.action_runner import read_sensor
from tools.scheduler import scheduler

router = APIRouter()


@router.post("/")
def create_action(action_request: ActionRequest) -> ActionResponse:
    opposite_action = Action.objects(opposite_action_id=action_request.opposite_action_id).first()
    if action_request.opposite_action_id != "" and opposite_action is None:
        raise HTTPException(status_code=404, detail="Opposite Action not found")
    action = Action(name=action_request.name, path=action_request.path,
                    opposite_action_id=action_request.opposite_action_id, description=action_request.description,
                    is_sensor=action_request.is_sensor)
    try:
        action.save()
    except NotUniqueError as e:
        raise HTTPException(status_code=409, detail=f"Action named {action.name} already exists")
    return ActionResponse.from_orm(action)


@router.get("/")
def get_actions(include_sensors: bool = False, include_actions: bool = False) -> List[ActionResponse]:
    query = Q()
    if include_actions:
        query = query & Q(is_sensor=False)
    if include_sensors:
        query = query & Q(is_sensor=True)

    actions = Action.objects(query)
    return [ActionResponse.from_orm(action) for action in actions]


@router.get("/{action_id}")
def get_action(action_id: str) -> ActionResponse:
    action = Action.objects(id=action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    return ActionResponse.from_orm(action)


@router.patch("/")
def patch_action(action_request: ActionUpdateRequest) -> ActionResponse:
    action: Action = Action.objects(id=action_request.id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    if action_request.path != "":
        action.path = action_request.path
    if action_request.name != "":
        action.name = action_request.name
    if action_request.description != "":
        action.description = action_request.description
    if action_request.is_sensor is not None:
        action.is_sensor = action_request.is_sensor
    if action_request.opposite_action_id != "":
        # If not empty find the action and raise exception if not found
        opposite_action = Action.objects(id=action_request.opposite_action_id).first()
        if opposite_action is None:
            raise HTTPException(status_code=404, detail="Opposite Action not found")
    # Update the opposite action anyway as its valid as empty field
    action.opposite_action_id = action_request.opposite_action_id

    action.save()

    return ActionResponse.from_orm(action)


@router.get("/run/{controller_id}/{action_id}")
def run_action(controller_id: str, action_id: str, minutes_to_run_opposite: Optional[int] = None) -> float:
    smart_controller: SmartController = SmartController.objects(id=controller_id).first()
    if not smart_controller:
        raise HTTPException(status_code=404, detail="Smart Controller not found")
    action: Action = next(action for action in smart_controller.actions if str(action.id) == action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    if action.is_sensor:
        return read_sensor(controller=smart_controller, action=action)
    else:
        if minutes_to_run_opposite is not None:
            opposite_action: Action = Action.objects(id=action.opposite_action_id).first()
            if not opposite_action:
                raise HTTPException(status_code=404, detail="Opposite action not found. Aborting action")
            task = ScheduledTask(
                action=opposite_action,
                smart_controller=smart_controller,
                minutes_to_run=minutes_to_run_opposite
            ).save()
            scheduler.schedule_short_term_tasks(task)
        return run(controller=smart_controller, action=action).ok


@router.delete("/{action_id}")
def delete_action(action_id: str) -> ActionResponse:
    action = Action.objects(id=action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    action.delete()

    return ActionResponse.from_orm(action)
