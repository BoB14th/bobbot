# app/vt/vt_service.py
import re, ipaddress, httpx
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session, sessionmaker
from fastapi.exceptions import HTTPException

from app.common.models.response import ResponseResult, IoCResponse
from app.common.enums import ResponseEnum as common
from app.vt.enums import ResponseEnum as response
import app.crud as crud
from app.config import conf, VT_BASE_URL


class VtService:
    _URL_RE   = re.compile(r"^(https?|ftp)://[^\s/$.?#].[^\s]*$", re.IGNORECASE)
    _HASH_RE  = re.compile(r"^[A-Fa-f0-9]{32}$|^[A-Fa-f0-9]{40}$|^[A-Fa-f0-9]{64}$")
    _DOMAIN_RE= re.compile(r"^(?!-)([A-Za-z0-9-]{1,63}\.)+[A-Za-z]{2,63}$")

    def __init__(self, session_factory: sessionmaker, api_key: Optional[str] = None):
        self._session_factory = session_factory
        self._api_key = api_key or conf["vt_api_key"]
        self._headers = {"x-apikey": self._api_key}

    @staticmethod
    def _detect_ioc_type(ioc: str) -> str:
        if VtService._URL_RE.match(ioc):
            return "url"
        try:
            ipaddress.ip_address(ioc)
            return "ip"
        except ValueError:
            pass
        if VtService._HASH_RE.fullmatch(ioc):
            return "hash"
        if VtService._DOMAIN_RE.match(ioc):
            return "domain"
        return "unknown"

    async def analyze_ioc(self, ioc: str) -> ResponseResult[IoCResponse]:
        print("호출되긴 하냐")
        ioc_type = self._detect_ioc_type(ioc)
        print(ioc_type)
        if ioc_type == "unknown":
            raise HTTPException(
                status_code=common.BAD_REQUEST.value,
                detail=response.INVALID_IOC_TYPE.value,
            )

        vt_json = await self._get_ioc_report(ioc, ioc_type)
        
        attrs: Dict[str, Any] = (vt_json.get("data") or {}).get("attributes") or {}
        stats: Dict[str, int] = attrs.get("last_analysis_stats") or attrs.get("stats") or {}
        label: Optional[str] = (attrs.get("popular_threat_classification") or {}).get(
            "suggested_threat_label"
        )

        score = int(stats.get("malicious", 0))
        vendor_count = int(sum(stats.values())) if stats else 0

        ioc_obj = IoCResponse(
            ioc=ioc,
            type=ioc_type,
            malicious_score=score,
            suggested_threat_label=label,
            vendor_count=vendor_count,
        )

        print(ioc_obj)
        db: Session = self._session_factory()
        try:
            crud.save_ioc(db, ioc_obj)
            db.commit()
        finally:
            db.close()

        return ResponseResult[IoCResponse](
            result_code=common.SUCCESS,
            result_msg=response.VT_ANALYSIS_SUCCESS,
            data=ioc_obj,
        )

    async def _get_ioc_report(self, ioc: str, ioc_type: str) -> dict:
        type_map = {
            "ip": "ip_addresses",
            "domain": "domains",
            "url": "urls",
            "hash": "files",
        }
        url = f"{VT_BASE_URL}/{type_map[ioc_type]}/{ioc}"

        timeout = httpx.Timeout(20.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                res = await client.get(url, headers=self._headers)
                res.raise_for_status()
                return res.json()
            except httpx.HTTPStatusError as e:
                # 404 등은 통일해서 NOT_FOUND로 처리
                raise HTTPException(
                    status_code=common.NOT_FOUND.value,
                    detail=response.VT_REPORT_NOT_FOUND.value,
                ) from e
