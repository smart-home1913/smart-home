import logging
from datetime import datetime, timedelta

import pytz
from apscheduler.job import Job
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import utc

from db.models import Task, TaskType

import tools.action_runner as action_runner
from db.scheduled_task import ScheduledTask
from tools.action_runner.action_runner import scheduled_run, run

scheduler = BackgroundScheduler(timezone=utc)
THRESHOLD_SECONDS = 10


def build_cron_expression(task: Task) -> CronTrigger:
    if task.type == TaskType.DAILY:
        cron = CronTrigger(
            minute=task.minute,
            hour=task.hour
        )
    elif task.type == TaskType.WEEKLY:
        cron = CronTrigger(
            minute=task.minute,
            hour=task.hour,
            day_of_week=task.week_day
        )
    else:
        cron = CronTrigger(
            minute=task.minute,
            hour=task.hour,
            day_of_week=task.week_day,
            day=task.month_day
        )

    return cron


def schedule_tasks():
    tasks_to_schedule = Task.objects().all()
    for task in tasks_to_schedule:
        schedule_long_term_tasks(task=task)

    scheduled_tasks = ScheduledTask.objects(is_active=True)
    for task in scheduled_tasks:
        run_at = calculate_running_time(task=task)
        schedule_short_term_tasks(task=task, run_at=run_at)


def shutdown_event():
    scheduler.shutdown()
    logging.info("Scheduler shutdown")


def startup_event():
    logging.info("Scheduler starting..")
    # Schedule tasks on application startup
    schedule_tasks()


def schedule_short_term_tasks(task: ScheduledTask, run_at=None):
    logging.info(
        f"setting scheduler in {task.minutes_to_run} minute/s for task action id: '{task.action.id}' "
        f"controller id: '{task.smart_controller.id}'"
    )
    run_time = datetime.now(pytz.UTC) + timedelta(minutes=task.minutes_to_run) if run_at is None else run_at

    job: Job = scheduler.add_job(scheduled_run, 'date', run_date=run_time, args=[run, task, scheduler],
                                 name=f"{task.smart_controller.name}->{task.action.name}")
    task.job_id = job.id
    task.save()


def schedule_long_term_tasks(task: Task):
    cron_trigger = build_cron_expression(task)

    job: Job = scheduler.add_job(
        action_runner.run,
        trigger=cron_trigger,
        args=[task.smart_controller, task.action],
        name=f"{task.smart_controller.name}->{task.action.name}"
    )
    task.job_id = job.id
    task.save()
    logging.info(f"Scheduled task: '{task.id}' with cron expression {cron_trigger}")


def calculate_running_time(task: ScheduledTask):
    original_run_time = task.inserted_at + timedelta(minutes=task.minutes_to_run)
    now = datetime.utcnow()
    time_difference = now - original_run_time
    return original_run_time if time_difference.total_seconds() <= THRESHOLD_SECONDS else (
            now + timedelta(seconds=10))