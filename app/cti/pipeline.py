# app/cti/pipeline.py
import re, json
from sqlalchemy.orm import Session
from app.models import CTITable
from .collectors import collect_virustotal, collect_urlscan
from .utils import score_from, clip

HEX_RE = re.compile(r"^[0-9a-fA-F]+$")

def classify_ioc(ioc: str) -> str:
    if ioc.startswith(("http://","https://")):
        return "url"
    if ioc.count(".")==3 and all(p.isdigit() and 0<=int(p)<=255 for p in ioc.split(".")):
        return "ip"
    if len(ioc) in (32, 40, 64) and HEX_RE.match(ioc):
        return "hash"
    return "domain"

def merge_results(vt, us):
    vendors = sorted(set((vt.get("vendor_hits") or [])))
    detect_count = int(vt.get("detect_count", 0))
    tags = sorted(set((vt.get("tags") or [])))
    country = us.get("country") or ""
    dns_list = sorted(set(us.get("dns") or []))
    raw = {"virustotal": vt.get("_raw")}
    if us:
        raw["urlscan"] = us.get("_raw")
    return vendors, detect_count, tags, country, dns_list, raw

def run_cti_with_session(db: Session, search_item: str) -> CTITable:
    ioc_type = classify_ioc(search_item)

    vt = collect_virustotal(search_item)

    # 해시면 urlscan 생략
    if ioc_type == "hash":
        us = None
        country, dns_list = "", []
    else:
        us = collect_urlscan(search_item)
        country = (us or {}).get("country") or ""
        dns_list = sorted(set((us or {}).get("dns") or []))

    vendors = sorted(set((vt.get("vendor_hits") or [])))
    detect_count = int(vt.get("detect_count", 0))
    tags = sorted(set((vt.get("tags") or [])))

    mscore = score_from(detect_count, tags)
    raw = {"virustotal": vt.get("_raw")}
    if us is not None:
        raw["urlscan"] = us.get("_raw")

    rec = CTITable(
        search_item=clip(search_item, 512),
        malicious_score=mscore,
        detect_count=detect_count,
        detect_vendor=",".join(vendors),   # 스키마를 TEXT로 늘렸다면 clip 불필요
        tag=",".join(tags),
        contry=clip(country, 64),
        dns=",".join(dns_list),
        _raw=json.dumps(raw, ensure_ascii=False),  # MEDIUMTEXT면 자르지 않아도 OK
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec
