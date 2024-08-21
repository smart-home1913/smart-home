from enum import Enum

from mongoengine import StringField, ListField, ReferenceField, EnumField, IntField, BooleanField

from db.base_model import MongoModel


class Action(MongoModel):
    name = StringField(unique=True)
    path = StringField()
    opposite_action_id = StringField(required=False, default="")
    description = StringField()
    is_sensor = BooleanField(default=False)
    meta = {
        'collection': 'actions'
    }


class TaskType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class SmartController(MongoModel):
    name = StringField()
    address = StringField()
    actions = ListField(ReferenceField(Action))
    scheduling = ListField()

    meta = {
        'collection': 'smart_controllers'
    }


class Task(MongoModel):
    type = EnumField(TaskType)
    smart_controller = ReferenceField(SmartController)
    action = ReferenceField(Action)
    minute = IntField(min_value=0, max_value=59)
    hour = IntField(min_value=0, max_value=23)
    week_day = IntField(min_value=0, max_value=6)
    month_day = IntField(min_value=1, max_value=31)
    job_id = StringField(required=False, default="")
