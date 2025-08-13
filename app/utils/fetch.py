import aiohttp

async def fetch_html(url: str, timeout_sec: int = 10) -> tuple[int, str]:
    timeout = aiohttp.ClientTimeout(total=timeout_sec)
    headers = {
        "User-Agent": "SlackSummaryBot/1.0 (+https://example.com)"
    }
    async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
        async with session.get(url) as r:
            status = r.status
            raw = await r.read()  # ← raw로 받고
            # 우선 UTF-8, 안되면 euc-kr 등 추정 실패는 무시하고 깨진 글자만 버림
            try:
                text = raw.decode("utf-8", errors="ignore")
            except Exception:
                text = (await r.text(errors="ignore"))  # 최후 fallback
            return status, text

