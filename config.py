import os

class Config:
    FACILITYCODE: str
    POSTGRESDB: str
    MONGODBPREFIX: str
    PORT: str
    
    @classmethod
    def init(cls):
        cls.FACILITYCODE = os.getenv("facilityCode", '')
        cls.POSTGRESDB = os.getenv("postgres.db", 'smrpdb_uat')
        cls.MONGODBPREFIX = os.getenv("mongodb.prefix", 'default')
        cls.PORT = os.getenv("port", '8000')