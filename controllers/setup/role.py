from blacksheep.server.controllers import get
from blacksheep.server.openapi.common import ContentInfo, ResponseInfo
from blacksheep import Response
from blacksheep.server.authorization import auth
from controllers.base import BaseSetupController
from docs import docs
from models import Role
from typing import List

from services.role import RoleService


@docs.tags("Setup/Role")
class RoleController(BaseSetupController):
    
    def __init__(self, cs: RoleService):
        self.cs = cs
        
    @docs(responses={200: ResponseInfo('', content=[ContentInfo(List[Role])])})
    @auth()
    @get("/lookup/groups")
    async def lookup_list(self) -> Response:
        return await self.cs.find_all(sortby="name", sortdir="asc")