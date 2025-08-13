import asyncio, re, logging
from urllib.parse import quote
from typing import Optional
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.socket_mode.aiohttp import SocketModeClient  
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from app.config import conf
from app.utils.fetch import fetch_html
from app.utils.summarizer import HtmlSummarizer
from fastapi.exceptions import HTTPException
from .enums import ResponseEnum
logger = logging.getLogger(__name__)
HELLO_PATTERN = re.compile(r"\bhello\b|안녕", re.IGNORECASE)
SUMM_PATTERN  = re.compile(r"(?:^|\s)(?:요약|summary)\s*[:\-]?\s+(.+)", re.IGNORECASE | re.S)
CTI_PATTERN = re.compile(r"^\s*분석\s+(.+)$", re.IGNORECASE)

SLACK_BOT_TOKEN = conf['slack_bot_token']
SLACK_APP_TOKEN = conf['slack_app_token']
OPENAI_API_KEY = conf['openai_api_key']

BASE_WIKI = "https://kitribob.wiki/wiki/"

def build_wiki_url(name: str) -> str:
    return BASE_WIKI + quote(name.strip())

class SlackService:
    def __init__(self, bot_token: str, app_token: str):
        self.web: Optional[AsyncWebClient] = AsyncWebClient(token=bot_token)
        self.socket: Optional[SocketModeClient] = SocketModeClient(
            app_token=app_token, web_client=self.web
        )
        self._task: Optional[asyncio.Task] = None
        self._started = asyncio.Event()
        self.vt = None
        self.html_summarizer = HtmlSummarizer(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

    def set_vt(self, vt_service):
        self.vt = vt_service

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
        text = (event.get("text") or "").strip()
        channel = event.get("channel")
        user = event.get("user")
        if not channel or not user:
            return

        if HELLO_PATTERN.search(text):
            await self.say(channel, f"안녕하세요, <@{user}>님! :wave:")
            return

        b = SUMM_PATTERN.search(text)
        print(b)
        if b:
            name = b.group(1).strip()
            await self._handle_summary(channel, user, name)
            return
        
        m = CTI_PATTERN.search(text)
        if m:
            target = m.group(1).strip()
            print("IOC target:", target)

            try:
                result = await self.vt.analyze_ioc(target)
                msg = self.ioc_result_to_text(result)
                await self.say(channel, msg)
            except HTTPException as e:
                await self.say(channel, f"분석 실패 ({e.status_code}): {e.detail}")
            except Exception as e:
                await self.say(channel, ResponseEnum.ANALYSIS_FAIL.value)
            
            return
        
        await self.say(channel, ResponseEnum.NOT_MATCH_REGEX.value)
        return

            
    async def _handle_summary(self, channel: str, user: str, name: str):
        if not self.html_summarizer:
            await self.say(channel, ResponseEnum.OPENAI_API_KEY_ERROR.value)
            return

        url = build_wiki_url(name)
        try:
            await self.say(channel, f"*{name}*"+ ResponseEnum.WAIT_MENTION.value)
            status, html = await fetch_html(url)
            if status == 404 or not html:
                await self.say(channel, ResponseEnum.PAGE_NOT_FOUND.value)
                return

            summary = await self.html_summarizer.summarize_html(url, html, title_hint=name)
            out = f"*[{name}]* \n\n{summary}"
            if len(out) > 2800:
                out = out[:2700] + "\n…(생략)\n" + url
            await self.say(channel, out)

        except Exception as e:
            print("summary error")
            await self.say(channel, ResponseEnum.SUMMARY_ERROR.value + e)

    def ioc_result_to_text(self, res) -> str:
        print(res)
        if hasattr(res.result_msg, "value"):
            msg = res.result_msg.value
        else:
            msg = str(res.result_msg)

        parts = [f"*==분석 결과==*\n"]

        data = getattr(res, "data", None)
        if data:
            ioc = getattr(data, "ioc", "")
            ioc_type = getattr(data, "type", "")
            malicious_score = getattr(data, "malicious_score", None)
            vendor_count = getattr(data, "vendor_count", None)
            threat_label = getattr(data, "suggested_threat_label", "")

            detail = []
            if ioc:
                detail.append(f"IoC: `{ioc}` ({ioc_type})\n")
            if malicious_score is not None and vendor_count is not None:
                detail.append(f"*`{vendor_count}`개 보안 벤더 중 `{malicious_score}`개가 악성으로 판정*\n")
            if threat_label:
                detail.append(f"위협 레이블은 `{threat_label}`로 식별됨\n")

            if detail:
                parts.append("".join(detail))

        return " ".join(parts)

        
    async def say(self, channel: str, text: str):
        await self.web.chat_postMessage(channel=channel, text=text)


def from_env() -> SlackService:
    if not SLACK_BOT_TOKEN or not SLACK_APP_TOKEN:
        raise RuntimeError("Set SLACK_BOT_TOKEN and SLACK_APP_TOKEN")
    return SlackService(SLACK_BOT_TOKEN, SLACK_APP_TOKEN)
