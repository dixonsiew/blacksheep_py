import os

class Config:
    PORT: str
    
    @classmethod
    def init(cls):
        cls.PORT = os.getenv("PORT", '8000')