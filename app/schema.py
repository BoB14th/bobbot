from typing import Optional
from pydantic import BaseModel, EmailStr # DTO

from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class Login(BaseModel):
    email: str
    password: str