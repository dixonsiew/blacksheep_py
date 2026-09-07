from datetime import datetime
from blacksheep import Application, get
from blacksheep.server.openapi.common import ContentInfo, ResponseInfo

from dataclasses import dataclass

import asyncpg
from asyncpg import Pool
from typing import List, Optional

from docs import docs


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "smrpdb_uat",
    "user": "postgres",
    "password": "postgres",
    "min_size": 5,
    "max_size": 20
}

pool: Optional[Pool] = None

@dataclass
class Item:
    id: int
    name: str
    description: str
    price: float
    
@dataclass
class City:
    id: int = None
    code: str = ""
    created_by: int = None
    created_date: str = ""
    deleted: bool = False
    deleted_by: int = None
    deleted_date: str = ""
    desc: str = ""
    modified_by: int = None
    modified_date: str = ""
    ref: str = ""


app = Application()


@app.on_start
async def configure_database(application: Application) -> None:
    """Initialize database connection pool on app startup."""
    pool = await asyncpg.create_pool(**DB_CONFIG)
    application.services.add_instance(pool, asyncpg.Pool)
    print("Database pool created successfully")

@app.on_stop
async def close_database_connection(application: Application) -> None:
    """Close database connection pool on app shutdown."""
    if pool:
        await pool.close()
        print("Database pool closed")

app.serve_files("public", root_path="public", fallback_document="index.html")

docs.bind_app(app)


@docs(responses={200: None}, tags=["Home"])
@get("/")
def home():
    return f"Hello, World! {datetime.now().isoformat()}"

@docs(responses={200: None}, tags=["Home"])
@get("/data")
def data():
    return {"message": "This is some data!"}

@docs(responses={200: ResponseInfo('', content=[ContentInfo(Item)])}, tags=["Items"])
@get("/item")
def get_item() -> Item:
    # In a real application, you would fetch the item from a database or other data source.
    # Here, we return a sample item for demonstration purposes.
    return Item(id=999, name=f"Item {999}", description=f"This is item {999}.", price=9.99)

@docs(responses={200: None}, tags=["Cities"])
@get("/city/list")
async def get_cities(dbp: asyncpg.Pool) -> List[City]:
    """Get all cities."""
    async with dbp.acquire() as conn:
        rows = await conn.fetch("""
            SELECT id, code, created_by, created_date, deleted, deleted_by, deleted_date, "desc", modified_by, modified_date, ref
            FROM city
            ORDER BY id
        """)
        
    lx = [City(**dict(row)) for row in rows]
    return lx


# http://localhost:8000/public/rapidoc/index.html#overview