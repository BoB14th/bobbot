# utils.py
def safe_get(d, path, default=None):
    cur = d
    for k in path.split("."):
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return default
    return cur

def clip(s: str, n: int) -> str:
    if s is None:
        return ""
    return s[:n]

SUSPICIOUS_TAGS = {"phishing","malware","botnet","ransom","ransomware","c2","stealer","trojan"}

def score_from(detect_count: int, tags: list) -> int:
    base = int(detect_count) * 15
    tag_boost = 10 if any((t or "").lower() in SUSPICIOUS_TAGS for t in (tags or [])) else 0
    val = max(0, min(100, base + tag_boost))
    return val
