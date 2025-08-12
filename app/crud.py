import json
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import os
import hashlib
import base64

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

import app.models as models
import app.schema as schema
from app.common.models.response import IoCResponse
from app.config import conf
from datetime import datetime

def hash_password(password: str) -> tuple:
    # 솔트 생성 (16바이트)
    salt = os.urandom(16)
    # PBKDF2 해싱 (SHA256, 100,000회 반복)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    # Base64 인코딩 (저장 용이하게)
    salt_b64 = base64.b64encode(salt).decode('utf-8')
    hashed_b64 = base64.b64encode(hashed).decode('utf-8')
    return salt_b64, hashed_b64

def save_ioc(db:Session, ioc_obj:IoCResponse):
    existing = db.query(models.IoC).filter(models.IoC.ioc_value == ioc_obj.ioc).first()

    if existing:
        existing.ioc_type = ioc_obj.type
        existing.malicious_score = ioc_obj.malicious_score
        existing.vendor_count = ioc_obj.vendor_count
        existing.created_at = datetime.now()
        db.commit()
        db.refresh(existing)
        return existing

    new_ioc = models.IoC(
        ioc_value=ioc_obj.ioc,
        ioc_type=ioc_obj.type,
        malicious_score=ioc_obj.malicious_score,
        suggested_threat_label=ioc_obj.suggested_threat_label,
        vendor_count=ioc_obj.vendor_count,
        last_analysis_date=datetime.now()
    )
    db.add(new_ioc)
    db.commit()
    db.refresh(new_ioc)
    return new_ioc

# Find user
def exist_user_by_email(db: Session, email: str) -> bool:
    return db.query(models.User).filter(models.User.email == email).first() is not None

def find_user_by_email(db: Session, email:str) -> models.User:
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schema.UserCreate) -> models.User:
    (salt, hashed_password) = hash_password(user.password)
    new_user = models.User(
        name=user.name,
        email=user.email,
        salt=salt,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


