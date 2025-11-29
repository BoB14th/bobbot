# logic.py
import json
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from .collectors import collect_virustotal, collect_urlscan
from app.models import CTITable

SUSPICIOUS = {"phishing","malware","botnet","ransom","ransomware","c2","stealer","trojan"}

def _score(detect_count: int, tags: List[str]) -> int:
    base = int(detect_count) * 15
    boost = 10 if any((t or "").lower() in SUSPICIOUS for t in (tags or [])) else 0
    v = max(0, min(100, base + boost))
    return v

def analyze_and_store(session: Session, ioc: str) -> CTITable:
    vt = collect_virustotal(ioc)
    us = collect_urlscan(ioc)

    vendors = sorted(set((vt.get("vendor_hits") or [])))
    detect_count = int(vt.get("detect_count", 0))  # urlscan은 스코어 없음
    tags = sorted(set((vt.get("tags") or [])))
    country = us.get("country") or ""
    dns_list = sorted(set(us.get("dns") or []))

    ms = _score(detect_count, tags)
    raw = {"virustotal": vt.get("_raw"), "urlscan": us.get("_raw")}

    rec = CTITable(
        search_item=ioc,
        malicious_score=ms,
        detect_count=detect_count,
        detect_vendor=",".join(vendors)[:2048],
        tag=",".join(tags)[:2048],
        contry=country[:64],
        dns=",".join(dns_list)[:2048],
        _raw=json.dumps(raw)[:1_000_000]
    )
    session.add(rec)
    session.commit()
    session.refresh(rec)
    return rec
