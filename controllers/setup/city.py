from blacksheep.server.controllers import APIController, delete, get, patch, post, put
from blacksheep.server.openapi.common import ContentInfo, ParameterInfo, ResponseInfo
from blacksheep import FromQuery, FromJSON, FromRoute, Response, json, not_found, ok
from docs import docs
from dto import KeywordDto, CommonSetupDto
from models import CommonSetup
from utils.pager import Pager
from constants.constant import AppConstant
from typing import List

from services.common_setup import CommonSetupService


@docs.tags("Setup/City")
class CityController(APIController):
    
    def __init__(self, cs: CommonSetupService):
        self.cs = cs
        self.table = "city"
    
    @classmethod
    def route(cls) -> str:
        return "api"
    
    
    @docs(responses={200: ResponseInfo('', content=[ContentInfo(List[CommonSetup])])})
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
        res = json(lx)
        res.headers.add(AppConstant.X_TOTAL_COUNT, bytes(str(total), 'utf-8'))
        res.headers.add(AppConstant.X_TOTAL_PAGES, bytes(str(pg.total_pages), 'utf-8'))
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
        res = json(lx)
        res.headers.add(AppConstant.X_TOTAL_COUNT, bytes(str(total), 'utf-8'))
        res.headers.add(AppConstant.X_TOTAL_PAGES, bytes(str(pg.total_pages), 'utf-8'))
        return res
    
    @docs(
        responses={200: ResponseInfo('')},
        parameters={
            "req": ParameterInfo(description="Create City Request")
        }
    )
    @post("/city")
    async def create(self, req: FromJSON[CommonSetupDto]) -> Response:
        data = req.value
        o = CommonSetup(code=data.code, desc=data.desc, ref=data.ref, created_by=1)
        await self.cs.save(o, self.table)
        return ok({
            "success": 1
        })
    
    @docs(
        responses={200: ResponseInfo('', content=[ContentInfo(CommonSetup)])},
        parameters={
            "id": ParameterInfo(description="Id")
        }
    )
    @get("/city/{id}")
    async def edit(self, id: FromRoute[int]) -> CommonSetup | None:
        o = await self.cs.find_by_id(id.value, self.table)
        if o:
            return o
        else:
            return not_found({
                "statusCode": 404,
                "message": "Record not found"
            })
          
    @docs(
        responses={200: ResponseInfo('')},
        parameters={
            "id": ParameterInfo(description="Id"),
            "req": ParameterInfo(description="Update City Request")
        }
    )
    @put("/city/{id}")  
    async def update(self, id: FromRoute[int], req: FromJSON[CommonSetupDto]) -> Response:
        data = req.value
        o = await self.cs.find_by_id(id.value, self.table)
        if o:
            o.code = data.code
            o.desc = data.desc
            o.ref = data.ref
            o.modified_by = 1
            await self.cs.update(o, self.table)
            return ok({
                "success": 1
            })
        else:
            return not_found({
                "statusCode": 404,
                "message": "Record not found"
            })
    
    @docs(
        responses={200: ResponseInfo('')},
        parameters={
            "id": ParameterInfo(description="Id")
        }
    )     
    @delete("/city/{id}")
    async def delete(self, id: FromRoute[int]) -> Response:
        await self.cs.delete_by_id(id.value, 1, self.table)
        return ok({
            "success": 1
        })