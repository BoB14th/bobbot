from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.config import conf

DB_PASSWORD = conf['dbpassword']

DB_CONN= f'mysql+pymysql://root:{DB_PASSWORD}@localhost:3306/bobbot'

engine = create_engine(
    DB_CONN,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=0,
    pool_recycle=3600,
    connect_args={"connect_timeout": 10},
)

SessionFactory = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

def get_db():
    db = SessionFactory()
    try:
        yield db
    finally:
        db.close()