from fastapi import APIRouter, Request, Depends
from app.common.models.request import SendMessageBody
from .slack_service import from_env

router = APIRouter()

slack_service = from_env()

def get_slack(request: Request):
    return request.app.state.slack

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.post("/send")
async def send_message(body: SendMessageBody, slack=Depends(get_slack)):
    await slack.say(body.channel, body.text)
    return {"sent": True}
