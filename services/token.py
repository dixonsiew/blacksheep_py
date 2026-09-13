from guardpost import Identity
from services.user import UserService


class TokenService:
    
    def __init__(self, cs: UserService):
        self.cs = cs
        
    def get_userid(self, user: Identity | None):
        sub = user.claims.get("sub")
                                
        if sub is None:
            return None
        
        id = int(sub)
        return id
    
    async def get_user(self, user: Identity | None):
        sub = user.claims.get("sub")
                        
        if sub is None:
            return None
        
        id = int(sub)
        o = await self.cs.find_by_id(id)
        return o