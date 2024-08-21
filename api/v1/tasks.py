from typing import List

from fastapi import APIRouter, HTTPException

from db.models import SmartController, Action, Task, TaskType
from models.task import TaskRequest, TaskResponse, TaskUpdateRequest
from tools.scheduler.scheduler import scheduler, schedule_long_term_tasks

router = APIRouter()


@router.post("/")
def create_task(task_request: TaskRequest) -> TaskResponse:
    smart_controller = SmartController.objects(id=task_request.smart_controller_id).first()

    if smart_controller is None:
        raise HTTPException(status_code=404, detail="Smart controller not found")

    action = Action.objects(id=task_request.action_id).first()
    if action is None or task_request.action_id not in [str(action.id) for action in smart_controller.actions]:
        raise HTTPException(status_code=404, detail="Action not found")

    task = Task(
        smart_controller=smart_controller,
        type=task_request.type,
        action=action,
        minute=task_request.minute,
        hour=task_request.hour,
        week_day=task_request.week_day if task_request.type == TaskType.WEEKLY else 0,
        month_day=task_request.month_day if task_request.type == TaskType.MONTHLY else 1
    ).save()

    schedule_long_term_tasks(task=task)

    return TaskResponse.from_orm(task)


@router.get("/{smart_controller_id}")
def get_smart_controller_tasks(smart_controller_id: str) -> List[TaskResponse]:
    tasks = Task.objects(smart_controller=smart_controller_id)
    return [TaskResponse.from_orm(task) for task in tasks]


@router.get("/{task_id}")
def get_task(task_id: str) -> TaskResponse:
    task = Task.objects(id=task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskResponse.from_orm(task)


@router.get("/")
def get_tasks() -> List[TaskResponse]:
    tasks = Task.objects().all()
    if not tasks:
        raise HTTPException(status_code=404, detail="Tasks not found")

    return [TaskResponse.from_orm(task) for task in tasks]


@router.patch("/")
def patch_task(task_request: TaskUpdateRequest) -> TaskResponse:
    task: Task = Task.objects(id=task_request.id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task_request.type is not None:
        task.type = task_request.type
    if task_request.minute is not None:
        task.minute = task_request.minute
    if task_request.hour is not None:
        task.hour = task_request.hour
    if task_request.week_day is not None:
        task.week_day = task_request.week_day
    if task_request.month_day is not None:
        task.month_day = task_request.month_day

    if task_request.action is not None:
        action = Action.objects(id=task_request.action).first()
        if action is None:
            raise HTTPException(status_code=404, detail="Action not found")
        task.action = action

    task.save()

    return TaskResponse.from_orm(task)


@router.delete("/")
def delete_task(task_id: str) -> TaskResponse:
    task = Task.objects(id=task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    scheduler.remove_job(job_id=task.job_id, jobstore="default")

    task.delete()

    return TaskResponse.from_orm(task)
