import random
import urllib.parse
import logging
from datetime import datetime, timedelta
from typing import Callable, Any, List

import pytz
import requests
from apscheduler.job import Job
from apscheduler.schedulers.background import BackgroundScheduler

from db.automation import Automation, AutomationNode
from db.models import Action, SmartController
from db.scheduled_task import ScheduledTask
from tools.automation_runner.automation_runner import AutomationRunner

RETRY_THRESHOLD = 5
RETRY_WINDOW = 10


def run(controller: SmartController, action: Action, is_part_of_automation=False):
    try:
        url = urllib.parse.urljoin(f"http://{controller.address}", action.path)
        logging.info(f"Running action: {action.name} on controller: {controller.name} -> {url}")
        response = requests.get(url)
        if response.ok and not is_part_of_automation:
            controller_id_str = str(controller.id)
            action_id_str = str(action.id)

            all_automations = Automation.objects()
            automations = [automation for automation in all_automations if
                           len([node.smart_controller_id == controller_id_str and node.action_id == action_id_str for
                                node
                                in automation.nodes]) > 0]
            logging.info(
                f"Found {len(automations)} automations with action: {action.name} of controller: {controller.name}")
            for automation in automations:
                roots: List[AutomationNode] = automation.get_roots()
                try:
                    relevant_node = next(iter([node for node in roots if
                                               node.smart_controller_id == controller_id_str and node.action_id == action_id_str]),
                                         None)
                except StopIteration:
                    relevant_node = None
                if relevant_node:
                    runner = AutomationRunner(automation=automation, run_function=run)
                    runner.next(previous_step_response=response.text, node=relevant_node)
        return response

    except Exception as e:
        logging.error(e)
        fake_response = requests.Response()
        fake_response.status_code = 500
        return fake_response


def scheduled_run(run_func: Callable, task: ScheduledTask, scheduler: BackgroundScheduler) -> Any:
    if task.retires_count == RETRY_THRESHOLD:
        task.is_active = False
        task.save()
        return

    result = run_func(task.smart_controller, task.action)

    if result.ok:
        task.is_active = False
    else:
        task.retires_count += 1

        job: Job = scheduler.add_job(scheduled_run, 'date',
                                     run_date=datetime.now(pytz.UTC) + timedelta(seconds=RETRY_WINDOW),
                                     args=[run_func, task, scheduler],
                                     name=f"{task.smart_controller.name}->{task.action.name}")
        task.job_id = job.id
    task.save()

    return result


def read_sensor(controller: SmartController, action: Action) -> float:
    url = urllib.parse.urljoin(f"http://{controller.address}", action.path)
    # logging.info(f"Running sensor reading: {action.name} on controller: {controller.name} -> {url}")
    response = requests.get(url)
    if response.ok:
        return float(response.text)
    else:
        raise Exception(f"Failed to read sensor {action.name} on url {action.path}")
