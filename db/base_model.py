import datetime

from mongoengine import Document, DateTimeField


class MongoModel(Document):
    inserted_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'allow_inheritance': True,
        'abstract': True
    }
