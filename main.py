import uvicorn
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

from config.logging import setup_logging
from db.database import connect_and_init_db
from api.v1 import actions, smart_controllers, tasks, automations
from tools.scheduler import scheduler as scheduler

setup_logging()

app = FastAPI()


app.add_event_handler("startup", connect_and_init_db)
app.add_event_handler("startup", scheduler.startup_event)
app.add_event_handler("shutdown", scheduler.shutdown_event)


app.include_router(actions.router, prefix="/actions")
app.include_router(smart_controllers.router, prefix="/smartControllers")
app.include_router(tasks.router, prefix="/tasks")
app.include_router(automations.router, prefix="/automations")

# Start the scheduler
scheduler.scheduler.start()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="smart-home",
        version="1.0.0",
        description="Smart home control",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


origins = ["*"]


app.add_middleware(
   CORSMiddleware,
   allow_origins=origins,
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"],
)


app.openapi = custom_openapi

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
