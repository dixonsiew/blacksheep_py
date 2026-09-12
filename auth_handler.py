from blacksheep import Application, Request, auth, get, json
from guardpost import AuthenticationHandler, Identity, User
from constants.constant import AppConstant

import jwt


class SMRPAuthHandler(AuthenticationHandler):
    
    def __init__(self):
        pass
    
    @property
    def scheme(self) -> str:
      return "smrp"
    
    async def authenticate(self, context: Request) -> Identity | None:
        header_value = context.get_first_header(b"Authorization")
        token = ""
        
        if header_value:
            s = header_value.decode()
            token = s.replace("Bearer ", "")
            
        else:
            token = context.cookies.get("token", "")
            
        if token == "":
            context.identity = None
            return None
            
        payload = jwt.decode(token, AppConstant.JWT_SECRET, algorithms=["HS256"])
        username = payload.get("username")
        sub = payload.get("sub")
        context.identity = Identity({
            "username": username,
            "sub": sub
        }, self.scheme)

        return context.identity