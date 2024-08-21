import logging
import time
from typing import Callable

from db.automation import Automation, AutomationNode, ConditionType, ReturnValueType, ConditionEdge
from db.models import SmartController, Action
from tools.automation_runner.utils import _string_to_bool, _string_to_float, _apply_comparison


class AutomationRunner:
    def __init__(self, automation: Automation, run_function: Callable):
        self.automation: Automation = automation
        self.run_function = run_function

    def next(self, previous_step_response, node: AutomationNode):
        # All the edges that their source is <node>
        edges = self.automation.get_edges(node=node)

        for edge in edges:
            if edge.condition.condition_type == ConditionType.BY_TRIGGER:
                self._handle_by_trigger(edge=edge)
            elif edge.condition.condition_type == ConditionType.BY_VALUE:
                self._handle_by_value(previous_step_response=previous_step_response, edge=edge, node=node)
            else:
                raise ValueError(f"Unsupported condition type {edge.condition.condition_type}")

    def _handle_by_trigger(self, edge: ConditionEdge):
        response = self._run(edge.target.smart_controller_id, edge.target.action_id)
        self.next(previous_step_response=response, node=edge.target)

    def _handle_by_value(self, previous_step_response, edge: ConditionEdge, node: AutomationNode):
        if edge.condition.value_type == ReturnValueType.BOOLEAN:
            try:
                if _string_to_bool(string=previous_step_response) == edge.condition.value_boolean:
                    response = self._run(edge.target.smart_controller_id, edge.target.action_id)
                    self.next(previous_step_response=response, node=edge.target)
                elif edge.condition.is_loop:
                    time.sleep(2)
                    response = self._run(smart_controller_id=node.smart_controller_id, action_id=node.action_id)
                    self.next(previous_step_response=response, node=node)

            except ValueError as e:
                logging.info(f"{e}: "
                             f"{previous_step_response} from action: {edge.target.action_id} "
                             f"of smart controller: {edge.target.smart_controller_id}")
        elif edge.condition.value_type == ReturnValueType.NUMBER:
            try:
                # convert response to float
                number = _string_to_float(previous_step_response)

                if _apply_comparison(edge.condition.operator, number, edge.condition.value_number):
                    response = self._run(edge.target.smart_controller_id, edge.target.action_id)
                    self.next(previous_step_response=response, node=edge.target)
                elif edge.condition.is_loop:
                    time.sleep(2)
                    response = self._run(smart_controller_id=node.smart_controller_id, action_id=node.action_id)
                    self.next(previous_step_response=response, node=node)
            except ValueError as e:
                logging.info(e)

    def _run(self, smart_controller_id: str, action_id: str):
        smart_controller = SmartController.objects(id=smart_controller_id).first()
        action = Action.objects(id=action_id).first()
        return self.run_function(controller=smart_controller, action=action, is_part_of_automation=True).text
