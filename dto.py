from dataclasses import dataclass
from pydantic import BaseModel, Field, PositiveInt


class LoginDto(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    
class RefreshTokenDto(BaseModel):
    refresh_token: str = Field(..., min_length=1)
    
class ChangePasswordDto(BaseModel):
    password: str = Field(..., min_length=1, max_length=150)
    confirm_password: str = Field(..., min_length=1, max_length=150)

@dataclass
class KeywordDto:
    keyword: str = ""
    
class CommonSetupDto(BaseModel):
    code: str = Field(..., min_length=1, max_length=30, str_strip=True)
    desc: str = Field(..., min_length=1, max_length=300, str_strip=True)
    ref: str = Field(..., min_length=1, max_length=200, str_strip=True)
    
class UserDto(BaseModel):
    username: str = Field(..., min_length=1, max_length=150)
    password: str = Field(..., min_length=1, max_length=150)
    first_name: str = Field(..., min_length=1, max_length=150)
    last_name: str = Field(..., max_length=150)
    role_id: PositiveInt
    
class ReportQueryDto(BaseModel):
    _page: PositiveInt
    _limit: PositiveInt
    vt: PositiveInt
    datefrom: str = Field(..., min_length=1)
    dateto: str = Field(..., min_length=1)