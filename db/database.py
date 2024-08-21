from mongoengine import connect
import logging

from config.settings import settings


async def connect_and_init_db():
    try:
        print(f"mongodb://{settings.MONGO_USERNAME}:{settings.MONGO_PASSWORD}@{settings.DB_ADDRESS}/{settings.MONGO_DATABASE}?authSource=admin")
        connect(
            host=f"mongodb://{settings.MONGO_USERNAME}:{settings.MONGO_PASSWORD}@{settings.DB_ADDRESS}/{settings.MONGO_DATABASE}?authSource=admin")
        logging.info('Connected to mongo.')
    except Exception as e:
        logging.exception(f'Could not connect to mongo: {e}')
        raise
