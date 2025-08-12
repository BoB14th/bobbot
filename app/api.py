from fastapi import FastAPI
from app.users import user_controller
from app.vt import vt_controller
from app.common.handlers.error_handler import setup_exception_handlers


app = FastAPI()

setup_exception_handlers(app)

app.include_router(user_controller.router, prefix="/users")
app.include_router(vt_controller.router, prefix="/vt")