from blacksheep.server.controllers import delete, get, post, put
from blacksheep.server.openapi.common import ContentInfo, ParameterInfo, ResponseInfo
from blacksheep import FromQuery, FromJSON, FromRoute, Request, Response
from controllers.base import BaseSetupController
from docs import docs
from dto import KeywordDto
from models import User
from utils.pager import Pager
from constants.constant import AppConstant
from typing import List

from services.user import UserService


@docs.tags("Setup/User")
class UserController(BaseSetupController):
    
    def __init__(self, cs: UserService):
        self.cs = cs
        
    @docs(
        responses={200: ResponseInfo('', content=[ContentInfo(List[User])])},
        parameters={
            "_page": ParameterInfo(description="Page number"),
            "_limit": ParameterInfo(description="Number of items per page"),
            "sort": ParameterInfo(description="Sort by field and direction (e.g., 'username:asc')")
        }
    )
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