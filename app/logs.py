from fastapi import Request, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AccessTime
from datetime import datetime

def log_access(
    request: Request,
    db: Session = Depends(get_db)  # db.get_session → get_db로 변경
):
    client_ip = request.client.host
    access_log = AccessTime(ip=client_ip, time=datetime.now())
    db.add(access_log)
    db.commit()
