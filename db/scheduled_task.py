
from mongoengine import ReferenceField, IntField, BooleanField, StringField

from db.base_model import MongoModel
from db.models import SmartController, Action


class ScheduledTask(MongoModel):
    smart_controller = ReferenceField(SmartController)
    action = ReferenceField(Action)
    minutes_to_run = IntField(min_value=1, max_value=240)
    is_active = BooleanField(default=True)
    retires_count = IntField(required=False, default=0)
    job_id = StringField(required=False, default="")
