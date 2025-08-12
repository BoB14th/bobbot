from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    salt = Column(String)
    hashed_password = Column(String) 

class AccessTime(Base):
    __tablename__ = "accessLogs"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String(45))
    time = Column(DateTime, default=datetime.now)

class IoC(Base):
    __tablename__ = "IoC"

    id = Column(Integer, primary_key=True, index=True)
    ioc_value = Column(String, index=True)
    ioc_type = Column(String)
    malicious_score = Column(Integer)
    suggested_threat_label = Column(String)
    vendor_count = Column(Integer)
    last_analysis_date = Column(DateTime, default=datetime.now)
    
    
