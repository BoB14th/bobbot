from fastapi import Request, Depends
from sqlalchemy.orm import Session
from app.database import db
from app.models import AccessTime
from datetime import datetime

def log_access(request: Request, db: Session = Depends(db.get_session)):
    client_ip = request.client.host
    access_log = AccessTime(ip=client_ip, time=datetime.now())
    db.add(access_log)
    db.commit()