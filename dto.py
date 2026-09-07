from dataclasses import dataclass


@dataclass
class KeywordDto:
    keyword: str = ""
    
@dataclass
class CommonSetupDto:
    code: str
    desc: str
    ref: str