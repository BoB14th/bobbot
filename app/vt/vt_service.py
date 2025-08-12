import httpx, re, ipaddress
from app.common.models.response import ResponseResult
from app.common.models.response import ResponseResult, IoCResponse
from app.common.enums import ResponseEnum as common
from app.vt.enums import ResponseEnum as response
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
import app.crud as crud
from app.config import conf,VT_BASE_URL

def detect_ioc_type(ioc: str) -> str:
    url_regex = re.compile(r'^(https?|ftp)://[^\s/$.?#].[^\s]*$', re.IGNORECASE)
    if url_regex.match(ioc):
        return "url"
    
    try:
        ipaddress.ip_address(ioc)
        return "ip"
    except ValueError:
        pass

    if re.fullmatch(r"[a-fA-F0-9]{32}|[a-fA-F0-9]{40}|[a-fA-F0-9]{64}", ioc):
        return "hash"

    domain_regex = re.compile(
        r"^(?!\-)([A-Za-z0-9\-]{1,63}\.)+[A-Za-z]{2,63}$"
    )
    if domain_regex.match(ioc):
        return "domain"

    return "unknown"

async def analyze_ioc(ioc: str, db: Session) -> IoCResponse:
    ioc_type = detect_ioc_type(ioc)
    if ioc_type == "unknown":
        raise HTTPException(status_code=common.BAD_REQUEST.value, detail=response.INVALID_IOC_TYPE.value)
    
    vt_response = await get_ioc_report(ioc, ioc_type)
    
    stats = vt_response["data"]["attributes"]["last_analysis_stats"]
    suggested_threat_label = vt_response.get("data", {}) \
    .get("attributes", {}) \
    .get("popular_threat_classification", {}) \
    .get("suggested_threat_label")


    score = stats.get("malicious", 0)

    vendor_count = sum(stats.values())

    ioc_obj = IoCResponse(
        ioc=ioc,
        type=ioc_type,
        malicious_score=score,
        suggested_threat_label=suggested_threat_label,
        vendor_count=vendor_count
    )

    crud.save_ioc(db, ioc_obj)

    return ResponseResult[IoCResponse](
        result_code=common.SUCCESS,
        result_msg=response.VT_ANALYSIS_SUCCESS,
        data=ioc_obj
    )

VT_API_KEY = conf['vt_api_key']
HEADERS = {"x-apikey": VT_API_KEY}

async def get_ioc_report(ioc: str, ioc_type: str) -> dict:
    type_map = {
        "ip": "ip_addresses",
        "domain": "domains",
        "url": "urls",
        "hash": "files"
    }
    url = f"{VT_BASE_URL}/{type_map[ioc_type]}/{ioc}"

    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(url, headers=HEADERS)
            res.raise_for_status()
            return res.json()
        except httpx.HTTPStatusError:
            raise HTTPException(status_code=common.NOT_FOUND.value, detail=response.VT_REPORT_NOT_FOUND.value)
