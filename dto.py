from dataclasses import dataclass
from pydantic import BaseModel, Field

@dataclass
class KeywordDto:
    keyword: str = ""
    
@dataclass
class CommonSetupDto(BaseModel):
    code: str = Field(..., min_length=1, max_length=30)
    desc: str = Field(..., min_length=1, max_length=300)
    ref: str = Field(..., min_length=1, max_length=200)