from models import User, Role
from typing import List

import asyncpg


class UserService:
    
    def __init__(self, dbp: asyncpg.Pool):
        self.dbp = dbp
        
    async def set_roles(self, o: User, conn):
        rows = await conn.fetch(f"""
            select r.id, r.name from app_user_roles aur inner join role r on aur.roles_id = r.id where aur.app_user_id = $1               
        """, o.id)
        lx = [Role(**dict(row)) for row in rows]
        o.roles = lx
    
    async def find_by_id(self, id: int) -> User | None:
        o = None
        async with self.dbp.acquire() as conn:
            row = await conn.fetchrow(f"""
                select id, username, first_name, last_name, password, last_login from app_user where id = $1 limit 1
            """, id)
            if row:
                o = User(**dict(row))
                await self.set_roles(o, conn)

        return o
    
    async def find_by_username(self, username: str) -> User | None:
        o = None
        async with self.dbp.acquire() as conn:
            row = await conn.fetchrow(f"""
                select id, username, first_name, last_name, password, last_login from app_user where username = $1 limit 1
            """, username)
            if row:
                o = User(**dict(row))
                await self.set_roles(o, conn)
                
        return o
    
    async def find_all(self, offset: int, limit: int, sortby: str, sortdir: str) -> List[User]:
        lx: List[User] = []
        async with self.dbp.acquire() as conn:
            rows = await conn.fetch(f"""
                select t.id, t.username, t.first_name, t.last_name, t.password, t.last_login from app_user t order by {sortby} {sortdir} offset $1 limit $2
            """, offset, limit)
            lx = [User(**dict(row)) for row in rows]
            for o in lx:
                await self.set_roles(o, conn)

        return lx
    
    async def count(self) -> int:
        async with self.dbp.acquire() as conn:
            row = await conn.fetchrow(f"""
                select count(id) from app_user
            """)

        return row[0] if row else 0
    
    async def exists_by_other_username(self, username: str, id: int) -> bool:
        async with self.dbp.acquire() as conn:
            row = await conn.fetchrow(f"""
                select exists (select 1 from app_user t where t.username = $1 and t.id <> $2)
            """, username, id)
            
        return True if row[0] == True else False
    
    async def exists_by_username(self, username: str) -> bool:
        async with self.dbp.acquire() as conn:
            row = await conn.fetchrow(f"""
                select exists (select 1 from app_user t where t.username = $1)
            """, username)
        
        return True if row[0] == True else False
    
    async def find_by_keyword(self, keyword: str, offset: int, limit: int, sortby: str, sortdir: str) -> List[User]:
        lx: List[User] = []
        async with self.dbp.acquire() as conn:
            rows = await conn.fetch(f"""
                select t.id, t.username, t.first_name, t.last_name, t.password, t.last_login 
                from app_user t where (t.username ilike $1 or t.first_name ilike $2 or t.last_name ilike $3) 
                order by {sortby} {sortdir} offset $4 limit $5
            """, keyword, keyword, keyword, offset, limit)
            lx = [User(**dict(row)) for row in rows]
            for o in lx:
                await self.set_roles(o, conn)

        return lx
    
    async def count_by_keyword(self, keyword: str) -> int:
        async with self.dbp.acquire() as conn:
            row = await conn.fetchrow(f"""
                select count(id) from app_user t where (t.username ilike $1 or t.first_name ilike $2 or t.last_name ilike $3)
            """, keyword, keyword, keyword)

        return row[0] if row else 0