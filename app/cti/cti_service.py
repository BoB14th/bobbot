import asyncio
from dataclasses import dataclass
from typing import List, Optional, Callable
from sqlalchemy.orm import Session, sessionmaker
from app.cti.pipeline import run_cti_with_session

@dataclass
class CTIResult:
    ioc: str
    ioc_type: str
    malicious_score: int
    detect_count: int
    vendors: List[str]
    tags: List[str]
    country: str
    dns: List[str]
    row_id: Optional[int] = None

class CTIService:
    def __init__(self, session_factory: sessionmaker):
        self._session_factory = session_factory

    async def analyze_and_store(self, ioc: str) -> CTIResult:
        # 동기 DB/HTTP 작업을 스레드로 오프로딩 (이벤트 루프 블로킹 방지)
        rec = await asyncio.to_thread(self._run_sync, ioc)
        return CTIResult(
            ioc=rec.search_item,
            ioc_type=self._guess_type(rec.search_item),
            malicious_score=rec.malicious_score or 0,
            detect_count=rec.detect_count or 0,
            vendors=(rec.detect_vendor or "").split(",") if rec.detect_vendor else [],
            tags=(rec.tag or "").split(",") if rec.tag else [],
            country=rec.contry or "",
            dns=(rec.dns or "").split(",") if rec.dns else [],
            row_id=rec.id,
        )

    def _run_sync(self, ioc: str):
        db: Session = self._session_factory()
        try:
            return run_cti_with_session(db, ioc)
        finally:
            db.close()

    def _guess_type(self, ioc: str) -> str:
        if ioc.startswith(("http://","https://")): return "url"
        if ioc.count(".")==3 and all(p.isdigit() and 0<=int(p)<=255 for p in ioc.split(".")): return "ip"
        if len(ioc) in (32,40,64): return "hash"
        return "domain"
