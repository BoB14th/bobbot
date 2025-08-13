import asyncio
from openai import OpenAI
from .enums import ResponseEnum

# 밥위키 읽고 느낀점 작성하기
SYSTEM_PROMPT = (
    "You are a Korean reviewer with a casual and witty tone. "
    "Given raw HTML of a web page, ignore navigation/ads/menus and focus ONLY on the main article. "
    "After reading, write 4-6 short bullet points describing your thoughts, impressions, or reactions "
    "as if you just finished reading it. "
    "Use natural Korean expressions and occasional humor, but do not include direct meta-comments about summarization."
)

class HtmlSummarizer:
    def __init__(self, api_key: str | None = None, project: str | None = None):
        self.client = OpenAI(api_key=api_key, project=project)

    async def summarize_html(self, url: str, html: str, title_hint: str | None = None) -> str:
        if not html or not html.strip():
            return ResponseEnum.SUMMARY_FAIL.value

        clipped = html[:15000]
        user_prompt = (
            f"[URL]: {url}\n"
            f"[TITLE_HINT]: {title_hint or ''}\n"
            "다음은 웹페이지의 원본 HTML입니다. 태그/메뉴/광고는 무시하고 본문만 요약해 주세요.\n\n"
            f"{clipped}"
        )

        def _call():
            return self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=500,
                temperature=0.2,
            )

        resp = await asyncio.to_thread(_call)
        return (resp.choices[0].message.content or "").strip() or ResponseEnum.EMPTY_RESPONSE.value
