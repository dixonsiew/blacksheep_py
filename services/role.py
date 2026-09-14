from models import Role
from typing import List

import asyncpg


class RoleService:
    
    def __init__(self, dbp: asyncpg.Pool):
        self.dbp = dbp
        
    async def find_all(self, sortby: str, sortdir: str) -> List[Role]:
        lx: List[Role] = []
        async with self.dbp.acquire() as conn:
            rows = await conn.fetch(f"""
                select id, name from role order by {sortby} {sortdir}
            """)
            lx = [Role(**dict(row)) for row in rows]
        
        return lx
    
    async def find_by_id(self, id: int) -> Role | None:
        o = None
        async with self.dbp.acquire() as conn:
            row = await conn.fetchrow(f"""
                select id, name from role where id = $1 limit 1
            """, id)
            if row:
                o = Role(**dict(row))
                await self.set_roles(o, conn)

        return o