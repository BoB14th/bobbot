import asyncio
from openai import OpenAI

SYSTEM_PROMPT = (
    "You are a concise Korean technical summarizer. "
    "Given raw HTML of a web page, ignore navigation/ads/menus and summarize ONLY the main article "
    "into 4-6 Korean bullet points with key facts (names, dates, definitions)."
)

class HtmlSummarizer:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    async def summarize_html(self, url: str, html: str, title_hint: str | None = None) -> str:
        if not html.strip():
            return "본문을 찾지 못해 요약할 수 없었어요."
        
        clipped = html[:15000]
        user_prompt = (
            f"[URL]: {url}\n"
            f"[TITLE_HINT]: {title_hint or ''}\n"
            "다음은 웹페이지의 원본 HTML입니다. 태그/메뉴/광고는 무시하고 본문만 요약해 주세요.\n\n"
            f"{clipped}"
        )

        def _call():
            return self.client.responses.create(
                model="gpt-5-mini",
                input=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                max_output_tokens=500,
            )

        resp = await asyncio.to_thread(_call)
        return resp.output_text.strip()
