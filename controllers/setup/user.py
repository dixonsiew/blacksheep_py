from blacksheep.server.controllers import delete, get, post, put
from blacksheep.server.openapi.common import ContentInfo, ParameterInfo, ResponseInfo
from blacksheep import FromQuery, FromJSON, FromRoute, Request, Response
from blacksheep.server.authorization import auth
from controllers.base import BaseSetupController
from docs import docs
from dto import KeywordDto, UserDto
from models import User
from utils.pager import Pager
from constants.constant import AppConstant
from typing import List

from services.user import UserService
from services.role import RoleService


@docs.tags("Setup/User")
class UserController(BaseSetupController):
    
    def __init__(self, cs: UserService, rs: RoleService):
        self.cs = cs
        self.rs = rs
        
    @docs(
        responses={200: ResponseInfo('', content=[ContentInfo(List[User])])},
        parameters={
            "_page": ParameterInfo(description="Page number"),
            "_limit": ParameterInfo(description="Number of items per page"),
            "sort": ParameterInfo(description="Sort by field and direction (e.g., 'username:asc')")
        }
    )
    @auth()
    @get("/users")
    async def list(self, 
                    _page: FromQuery[int] = FromQuery(1),
                    _limit: FromQuery[int] = FromQuery(20),
                    sort: FromQuery[str] = FromQuery(""),
    ) -> List[User]:
        page = _page.value
        limit = _limit.value
        sorts = sort.value
        
        sortby = "username"
        sortdir = "asc"
        
        if sorts != "":
            lis = sorts.split("$")
            s = lis[0]
            arr = s.split(":")
            sortby = arr[0]
            sortdir = arr[1]
            
        total = await self.cs.count()
        pg = Pager(total, page, limit)
        lx = await self.cs.find_all(offset=pg.lower_bound, limit=pg.page_size, sortby=sortby, sortdir=sortdir)
        ly = [x.to_dict() for x in lx]
        res = self.json(ly)
        res.headers.add(AppConstant.X_TOTAL_COUNT, bytes(str(total), 'utf-8'))
        res.headers.add(AppConstant.X_TOTAL_PAGE, bytes(str(pg.total_pages), 'utf-8'))
        return res
    
    @docs(
        responses={200: ResponseInfo('', content=[ContentInfo(List[User])])},
        parameters={
            "_page": ParameterInfo(description="Page number"),
            "_limit": ParameterInfo(description="Number of items per page"),
            "sort": ParameterInfo(description="Sort by field and direction (e.g., 'username:asc')"),
            "keyword": ParameterInfo(description="Keyword for searching")
        }
    )
    @auth()
    @post("/users")
    async def search_list(self,
                            keyword: FromJSON[KeywordDto],
                            _page: FromQuery[int] = FromQuery(1),
                            _limit: FromQuery[int] = FromQuery(20),
                            sort: FromQuery[str] = FromQuery(""),
    ) -> List[User]:
        page = _page.value
        limit = _limit.value
        sorts = sort.value

        sortby = "username"
        sortdir = "asc"

        data = keyword.value
        key = f'%{data.keyword}%'

        if sorts != "":
            lis = sorts.split("$")
            s = lis[0]
            arr = s.split(":")
            sortby = arr[0]
            sortdir = arr[1]

        total = await self.cs.count_by_keyword(key)
        pg = Pager(total, page, limit)
        lx = await self.cs.find_by_keyword(keyword=key, offset=pg.lower_bound, limit=pg.page_size, sortby=sortby, sortdir=sortdir)
        ly = [x.to_dict() for x in lx]
        res = self.json(ly)
        res.headers.add(AppConstant.X_TOTAL_COUNT, bytes(str(total), 'utf-8'))
        res.headers.add(AppConstant.X_TOTAL_PAGE, bytes(str(pg.total_pages), 'utf-8'))
        return res
    
    @docs(responses={200: ResponseInfo('')})
    @auth()
    @post("/user")
    async def create(self, req: FromJSON[UserDto], request: Request) -> Response:
        user_id = request.user.id
        if user_id is None:
            return self.unauthorized()

        data = req.value
        b = await self.cs.exists_by_username(data.username)
        
        if b:
            return self.bad_request({
                "statusCode": 400,
                "message": "A user with that username already exists"
            })
            
        role = await self.rs.find_by_id(data.role_id)
        
        if role is None:
            return self.not_found({
                "statusCode": 404,
                "message": "A user with that username already exists"
            })
            
        # o = User(password=data.password, username=data.username, first_name=data.first_name, last_name=data.last_name, roles=[role])
        # await self.cs.save(o)
        return self.ok({
            "success": 1
        })