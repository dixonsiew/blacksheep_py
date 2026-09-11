from dataclasses import dataclass
from pydantic import BaseModel, Field


class LoginDto(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    
class RefreshTokenDto(BaseModel):
    refresh_token: str = Field(..., min_length=1)

@dataclass
class KeywordDto:
    keyword: str = ""
    
class CommonSetupDto(BaseModel):
    code: str = Field(..., min_length=1, max_length=30, str_strip=True)
    desc: str = Field(..., min_length=1, max_length=300, str_strip=True)
    ref: str = Field(..., min_length=1, max_length=200, str_strip=True)