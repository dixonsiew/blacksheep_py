from blacksheep.server.controllers import APIController, delete, get, patch, post
from blacksheep.server.openapi.common import ContentInfo, ResponseInfo
from docs import docs
from datetime import datetime
from models import Item


@docs.tags("Home")
class Homecontroller(APIController):
    
    @classmethod
    def route(cls) -> str:
        return ""
    
    @docs(responses={200: ResponseInfo('', content=[ContentInfo(str)])})
    @get("/")
    async def home(self) -> str:
        return f"Hello, World! {datetime.now().isoformat()}"
    
    @docs(responses={200: ResponseInfo('', content=[ContentInfo(dict)])})
    @get("/data")
    async def data(self) -> dict:
        return {"message": "This is some data!"}
    
    @docs(responses={200: ResponseInfo('', content=[ContentInfo(Item)])})
    @get("/item")
    async def get_item(self) -> Item:
        # In a real application, you would fetch the item from a database or other data source.
        # Here, we return a sample item for demonstration purposes.
        return Item(id=999, name=f"Item {999}", description=f"This is item {999}.", price=9.99)