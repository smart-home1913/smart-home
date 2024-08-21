from enum import Enum
from typing import List

from mongoengine import EmbeddedDocumentField, EmbeddedDocument, StringField, EnumField, FloatField, BooleanField, \
    ListField, ReferenceField

from db.base_model import MongoModel


class ConditionType(str, Enum):
    BY_VALUE = "by_value"
    BY_TRIGGER = "by_trigger"


class ReturnValueType(str, Enum):
    BOOLEAN = "boolean"
    NUMBER = "number"


class Operator(str, Enum):
    GREATER = ">"
    LESS = "<"
    LESS_EQUAL = "<="
    GREATER_EQUAL = ">="
    EQUAL = "=="
    NOT_EQUAL = "!="


class Location(EmbeddedDocument):
    x = FloatField()
    y = FloatField()
    meta = {
        'allow_inheritance': True
    }


class AutomationNode(MongoModel):
    unique_key = StringField()
    smart_controller_id = StringField()
    action_id = StringField()
    location = EmbeddedDocumentField(Location)


class Condition(EmbeddedDocument):
    condition_type = EnumField(ConditionType)
    value_type = EnumField(ReturnValueType)
    operator = EnumField(Operator)
    value_number = FloatField(default=0.0, required=False)
    value_boolean = BooleanField(default=False, required=False)
    is_loop = BooleanField(default=False)


class ConditionEdge(MongoModel):
    source = ReferenceField(AutomationNode, required=True)
    target = ReferenceField(AutomationNode, required=True)
    condition = EmbeddedDocumentField(Condition)


class GraphViewport(Location):
    zoom = FloatField()


class Automation(MongoModel):
    name = StringField(required=True, unique=True)
    nodes = ListField(ReferenceField(AutomationNode))
    edges = ListField(ReferenceField(ConditionEdge))
    viewport = EmbeddedDocumentField(GraphViewport, default=GraphViewport(x=float(0.0), y=float(0.0), zoom=float(1.0)))
    is_active = BooleanField(default=True)

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes.append(node)
            self.save()

    def add_edge(self, edge: ConditionEdge):
        edge.save()
        self.edges.append(edge)
        self.save()

    def get_children(self, node: AutomationNode) -> List[AutomationNode]:
        return [edge.target for edge in self.edges if edge.source == node]

    def get_roots(self) -> List[AutomationNode]:
        return [node for node in self.nodes if self._is_root(node=node)]

    def _is_root(self, node: AutomationNode) -> bool:
        return len([edge for edge in self.edges if edge.target.id == node.id]) == 0

    def get_edges(self, node: AutomationNode) -> List[ConditionEdge]:
        return [edge for edge in self.edges if edge.source.id == node.id]
