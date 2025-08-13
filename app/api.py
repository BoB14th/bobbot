from fastapi import FastAPI
from app.users import user_controller
from app.vt import vt_controller
from app.slack import slack_controller
from app.common.handlers.error_handler import setup_exception_handlers
from contextlib import asynccontextmanager
from app.vt.vt_service import VtService
from app.database import SessionFactory

@asynccontextmanager
async def lifespan(app: FastAPI):
    vt = VtService(SessionFactory)
    app.state.vt = vt
    
    app.state.slack = slack_controller.slack_service
    app.state.slack.set_vt(vt)

    await app.state.slack.start()
    try:
        yield
    finally:
        await app.state.slack.stop()

app = FastAPI(lifespan=lifespan)

setup_exception_handlers(app)

app.include_router(user_controller.router, prefix="/users")
app.include_router(vt_controller.router, prefix="/vt")
app.include_router(slack_controller.router, prefix="/slack")