from blacksheep.server.controllers import delete, get, post, put
from blacksheep.server.openapi.common import ContentInfo, ParameterInfo, RequestBodyInfo, ResponseInfo
from blacksheep import FromQuery, FromJSON, FromRoute, Request, Response
from blacksheep.server.authorization import auth
from guardpost import Identity
from controllers.base import BaseSetupController
from docs import docs
from dto import KeywordDto, CommonSetupDto
from models import CommonSetup
from utils.pager import Pager
from constants.constant import AppConstant
from typing import List

from services.common_setup import CommonSetupService
from services.token import TokenService


@docs.tags("Setup/City")
class CityController(BaseSetupController):
    
    def __init__(self, cs: CommonSetupService, ts: TokenService):
        self.cs = cs
        self.ts = ts
        self.table = "city"
    
    @docs(responses={200: ResponseInfo('', content=[ContentInfo(List[CommonSetup])])})
    @auth()
    @get("/lookup/cities")
    async def lookup_list(self) -> Response:
        return await self.cs.find_all("city", offset=0, limit=0, sortby="", sortdir="")
    
    @docs(
        responses={200: ResponseInfo('', content=[ContentInfo(List[CommonSetup])])},
        parameters={
            "_page": ParameterInfo(description="Page number"),
            "_limit": ParameterInfo(description="Number of items per page"),
            "sort": ParameterInfo(description="Sort by field and direction (e.g., 'code:asc')")
        }
    )
    @auth()
    @get("/cities")
    async def list(self, 
                   _page: FromQuery[int] = FromQuery(1),
                   _limit: FromQuery[int] = FromQuery(20),
                   sort: FromQuery[str] = FromQuery(""),
    ) -> List[CommonSetup]:
        page = _page.value
        limit = _limit.value
        sorts = sort.value
        
        sortby = "code"
        sortdir = "asc"
        
        if sorts != "":
            lis = sorts.split("$")
            s = lis[0]
            arr = s.split(":")
            sortby = arr[0]
            sortdir = arr[1]
            
        total = await self.cs.count(self.table)
        pg = Pager(total, page, limit)
        lx = await self.cs.find_all(table=self.table, offset=pg.lower_bound, limit=pg.page_size, sortby=sortby, sortdir=sortdir)
        res = self.json(lx)
        res.headers.add(AppConstant.X_TOTAL_COUNT, bytes(str(total), 'utf-8'))
        res.headers.add(AppConstant.X_TOTAL_PAGE, bytes(str(pg.total_pages), 'utf-8'))
        return res
    
    @docs(
        responses={200: ResponseInfo('', content=[ContentInfo(List[CommonSetup])])},
        parameters={
            "_page": ParameterInfo(description="Page number"),
            "_limit": ParameterInfo(description="Number of items per page"),
            "sort": ParameterInfo(description="Sort by field and direction (e.g., 'code:asc')"),
            "keyword": ParameterInfo(description="Keyword for searching")
        }
    )
    @auth()
    @post("/cities")
    async def search_list(self,
                          keyword: FromJSON[KeywordDto],
                          _page: FromQuery[int] = FromQuery(1),
                          _limit: FromQuery[int] = FromQuery(20),
                          sort: FromQuery[str] = FromQuery(""),
    ) -> List[CommonSetup]:
        page = _page.value
        limit = _limit.value
        sorts = sort.value
        
        sortby = "code"
        sortdir = "asc"
        
        data = keyword.value
        key = f'%{data.keyword}%'
        
        if sorts != "":
            lis = sorts.split("$")
            s = lis[0]
            arr = s.split(":")
            sortby = arr[0]
            sortdir = arr[1]
        
        total = await self.cs.count_by_keyword(key, self.table)
        pg = Pager(total, page, limit)
        lx = await self.cs.find_by_keyword(keyword=key, offset=pg.lower_bound, limit=pg.page_size, sortby=sortby, sortdir=sortdir, table=self.table)
        res = self.json(lx)
        res.headers.add(AppConstant.X_TOTAL_COUNT, bytes(str(total), 'utf-8'))
        res.headers.add(AppConstant.X_TOTAL_PAGE, bytes(str(pg.total_pages), 'utf-8'))
        return res
    
    @docs(
        responses={200: ResponseInfo('')},
        parameters={
            "req": ParameterInfo(description="Create City Request", value_type=CommonSetupDto)
        }
    )
    @auth()
    @post("/city")
    async def create(self, req: FromJSON[dict], user: Identity | None) -> Response:
        user_id = self.ts.get_userid(user)
        if user_id is None:
            return self.unauthorized()
        
        m = req.value
        data = CommonSetupDto(**m)
        o = CommonSetup(code=data.code, desc=data.desc, ref=data.ref, created_by=user_id)
        await self.cs.save(o, self.table)
        return self.ok({
            "success": 1
        })
    
    @docs(
        responses={200: ResponseInfo('', content=[ContentInfo(CommonSetup)])},
        parameters={
            "id": ParameterInfo(description="Id")
        }
    )
    @auth()
    @get("/city/{id}")
    async def edit(self, id: FromRoute[int]) -> CommonSetup | None:
        o = await self.cs.find_by_id(id.value, self.table)
        if o:
            return o
        else:
            return self.not_found({
                "statusCode": 404,
                "message": "Record not found"
            })
          
    @docs(
        responses={200: ResponseInfo('')},
        parameters={
            "id": ParameterInfo(description="Id"),
            "req": ParameterInfo(description="Update City Request", value_type=CommonSetupDto)
        }
    )
    @auth()
    @put("/city/{id}")  
    async def update(self, id: FromRoute[int], req: FromJSON[dict], request: Request) -> Response:
        user_id = request.user.id
        if user_id is None:
            return self.unauthorized()
                
        m = req.value
        data = CommonSetupDto(**m)
        o = await self.cs.find_by_id(id.value, self.table)
        if o:
            o.code = data.code
            o.desc = data.desc
            o.ref = data.ref
            o.modified_by = user_id
            await self.cs.update(o, self.table)
            return self.ok({
                "success": 1
            })
        else:
            return self.not_found({
                "statusCode": 404,
                "message": "Record not found"
            })
    
    @docs(
        responses={200: ResponseInfo('')},
        parameters={
            "id": ParameterInfo(description="Id")
        }
    )
    @auth()  
    @delete("/city/{id}")
    async def delete(self, id: FromRoute[int], req: Request) -> Response:
        user_id = req.user.id
        if user_id is None:
            return self.unauthorized()
        
        await self.cs.delete_by_id(id.value, user_id, self.table)
        return self.ok({
            "success": 1
        })