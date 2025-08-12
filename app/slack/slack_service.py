# app/slack/slack_service.py
import asyncio, re, logging
from typing import Optional
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.socket_mode.aiohttp import SocketModeClient  
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from app.config import conf

logger = logging.getLogger(__name__)
HELLO_PATTERN = re.compile(r"\bhello\b|안녕", re.IGNORECASE)
SLACK_BOT_TOKEN = conf['slack_bot_token']
SLACK_APP_TOKEN = conf['slack_app_token']

class SlackService:
    def __init__(self, bot_token: str, app_token: str):
        self.web: Optional[AsyncWebClient] = AsyncWebClient(token=bot_token)
        self.socket: Optional[SocketModeClient] = SocketModeClient(
            app_token=app_token, web_client=self.web
        )
        self._task: Optional[asyncio.Task] = None
        self._started = asyncio.Event()

    async def start(self):
        if self._task and not self._task.done():
            return
        self.socket.socket_mode_request_listeners.append(self._on_request)
        self._task = asyncio.create_task(self._run())
        await self._started.wait()
        logger.info("Slack Socket Mode started")

    async def stop(self):
        if self.socket:
            await self.socket.disconnect()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Slack Socket Mode stopped")

    async def _run(self):
        await self.socket.connect()
        self._started.set()
        while True:
            await asyncio.sleep(3600)

    async def _on_request(self, client: SocketModeClient, req: SocketModeRequest):
        await client.send_socket_mode_response(SocketModeResponse(envelope_id=req.envelope_id))
        if req.type == "events_api":
            event = (req.payload or {}).get("event", {}) or {}
            if event.get("type") == "message" and not event.get("subtype") and "bot_id" not in event:
                await self._handle_message(event)

    async def _handle_message(self, event: dict):
        text = event.get("text", "")
        channel = event.get("channel")
        user = event.get("user")
        if not channel or not user:
            return
        if HELLO_PATTERN.search(text):
            await self.say(channel, f"Hello, <@{user}>! :wave:")

    async def say(self, channel: str, text: str):
        await self.web.chat_postMessage(channel=channel, text=text)


def from_env() -> SlackService:
    if not SLACK_BOT_TOKEN or not SLACK_APP_TOKEN:
        raise RuntimeError("Set SLACK_BOT_TOKEN and SLACK_APP_TOKEN")
    return SlackService(SLACK_BOT_TOKEN, SLACK_APP_TOKEN)
