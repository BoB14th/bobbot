# collectors.py
import os, requests
from typing import Dict, Any, List
from app.config import conf

TIMEOUT = 20
VT_API_KEY = conf['vt_api_key']
URLSCAN_API_KEY = conf['urlscan_api_key']
def _safe_get(d: Any, path: str, default=None):
    cur = d
    for k in path.split("."):
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return default
    return cur

def collect_virustotal(ioc: str) -> Dict[str, Any]:
    """
    ioc: 도메인 / URL / 해시 / IP 모두 허용
    - 도메인/IP: /domains/{ioc} 또는 /ip_addresses/{ioc}
    - URL: /search?query=
    - 해시: /files/{hash}
    반환: vendor_hits(list), detect_count(int), tags(list), _raw(json)
    """
    headers = {"x-apikey": VT_API_KEY}
    data = None

    try:
        if ioc.startswith(("http://","https://")):
            # 간단화: URL은 search로 조회
            r = requests.get("https://www.virustotal.com/api/v3/search",
                             headers=headers, params={"query": ioc}, timeout=TIMEOUT)
            r.raise_for_status()
            data = r.json()
        elif ioc.count(".") == 3 and all(p.isdigit() and 0 <= int(p) <= 255 for p in ioc.split(".")):
            # IPv4
            r = requests.get(f"https://www.virustotal.com/api/v3/ip_addresses/{ioc}",
                             headers=headers, timeout=TIMEOUT)
            r.raise_for_status()
            data = r.json()
        elif len(ioc) in (32,40,64):  # md5/sha1/sha256 대략 판별
            r = requests.get(f"https://www.virustotal.com/api/v3/files/{ioc}",
                             headers=headers, timeout=TIMEOUT)
            r.raise_for_status()
            data = r.json()
        else:
            # 도메인 가정
            r = requests.get(f"https://www.virustotal.com/api/v3/domains/{ioc}",
                             headers=headers, timeout=TIMEOUT)
            r.raise_for_status()
            data = r.json()
    except requests.RequestException as e:
        return {"vendor_hits": [], "detect_count": 0, "tags": [], "_raw": {"error": str(e)}}

    stats = _safe_get(data, "data.attributes.last_analysis_stats", {}) or {}
    results = _safe_get(data, "data.attributes.last_analysis_results", {}) or {}
    vendor_hits = [v for v, det in (results or {}).items() if det and det.get("category") == "malicious"]
    detect_count = int(stats.get("malicious", 0))
    tags = _safe_get(data, "data.attributes.tags", []) or []

    return {
        "vendor_hits": vendor_hits,
        "detect_count": detect_count,
        "tags": tags,
        "_raw": data,
    }

def collect_urlscan(ioc: str) -> Dict[str, Any]:
    """
    ioc: URL 또는 도메인(검색은 IP/ASN도 가능하지만 여기서는 URL/도메인 중심)
    - URL이면 그대로 q=ioc
    - 그 외는 도메인으로 보고 q=domain:<ioc>
    반환: country(str), dns(list[str]), _raw(json)
    """
    headers = {"API-Key": URLSCAN_API_KEY, "Content-Type": "application/json"}
    q = ioc if ioc.startswith(("http://","https://")) else f"domain:{ioc}"

    try:
        r = requests.get("https://urlscan.io/api/v1/search/",
                         params={"q": q, "size": 1}, timeout=TIMEOUT, headers=headers)
        r.raise_for_status()
        srch = r.json()
        if not srch.get("results"):
            return {"country": "", "dns": [], "_raw": srch}

        result_api = srch["results"][0].get("result")
        r2 = requests.get(result_api, timeout=TIMEOUT)
        r2.raise_for_status()
        data = r2.json()
    except requests.RequestException as e:
        return {"country": "", "dns": [], "_raw": {"error": str(e)}}

    country = _safe_get(data, "page.country", "") or ""
    reqs: List[dict] = _safe_get(data, "data.requests", []) or []
    hosts = set()
    for req in reqs:
        h = _safe_get(req, "request.requestHeaders.Host")
        if h:
            hosts.add(h)

    return {
        "country": country,
        "dns": sorted(hosts),
        "_raw": data,
    }
