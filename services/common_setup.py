from models import CommonSetup
from typing import List

import asyncpg


class CommonSetupService:
    
    def __init__(self, dbp: asyncpg.Pool):
        self.dbp = dbp
    
    async def find_by_id(self, id: int, table: str) -> CommonSetup | None:
        async with self.dbp.acquire() as conn:
            row = await conn.fetchrow(f"""
                select id, code, "desc", ref, created_by, created_date, modified_by, modified_date, deleted, deleted_by, deleted_date 
                from {table} where id = $1 limit 1
            """, id)
            
        if row:
            return CommonSetup(**dict(row))
        else:
            return None
        
    async def find_by_desc(self, desc: str, table: str) -> CommonSetup | None:
        async with self.dbp.acquire() as conn:
            row = await conn.fetchrow(f"""
                select t.id, t.code, t.desc, t.ref, t.created_by, t.created_date, t.modified_by, t.modified_date, t.deleted, t.deleted_by, t.deleted_date 
                from {table} t where lower(t.desc) = lower($1) limit 1
            """, desc)
            
        if row:
            return CommonSetup(**dict(row))
        else:
            return None
        
    async def find_all(self, table: str, offset: int, limit: int, sortby: str, sortdir: str) -> List[CommonSetup]:
        async with self.dbp.acquire() as conn:
            if limit > 0:
                rows = await conn.fetch(f"""
                    select t.id, t.code, t.desc, t.ref, t.created_by, t.created_date, t.modified_by, t.modified_date, t.deleted, t.deleted_by, t.deleted_date from 
                    {table} t where t.deleted is not true order by "{sortby}" {sortdir} offset $1 limit $2
                """, offset, limit)
            else:
                rows = await conn.fetch(f"""
                    select t.id, t.code, t.desc, t.ref, t.created_by, t.created_date, t.modified_by, t.modified_date, t.deleted, t.deleted_by, t.deleted_date 
                    from {table} t where t.desc <> '' and t.deleted is not true order by t.code
                """)
            
        return [CommonSetup(**dict(row)) for row in rows]
    
    async def count(self, table: str) -> int:
        async with self.dbp.acquire() as conn:
            row = await conn.fetchrow(f"""
                select count(id) from {table} t where t.deleted is not true
            """)
            
        return row[0] if row else 0
    
    async def find_by_keyword(self, keyword: str, offset: int, limit: int, sortby: str, sortdir: str, table: str) -> List[CommonSetup]:
        async with self.dbp.acquire() as conn:
            rows = await conn.fetch(f"""
                select t.id, t.code, t.desc, t.ref, t.created_by, t.created_date, t.modified_by, t.modified_date, t.deleted, t.deleted_by, t.deleted_date 
                from {table} t where (t.code ilike $1 or t.desc ilike $2 or t.ref ilike $3) and t.deleted is not true order by "{sortby}" {sortdir} offset $4 limit $5
            """, keyword, keyword, keyword, offset, limit)

            
        return [CommonSetup(**dict(row)) for row in rows]
    
    async def count_by_keyword(self, keyword: str, table: str) -> int:
        async with self.dbp.acquire() as conn:
            row = await conn.fetchrow(f"""
                select count(id) from {table} t where (t.code ilike $1 or t.desc ilike $2 or t.ref ilike $3) and t.deleted is not true
            """, keyword, keyword, keyword)
        
        return row[0] if row else 0
    
    async def save(self, o: CommonSetup, table: str):
        async with self.dbp.acquire() as conn:
            await conn.execute(f"""
                insert into {table} (id, code, "desc", ref, created_by, created_date) values(nextval('{table}_id_seq'),$1,$2,$3,$4,now())
            """, o.code, o.desc, o.ref, o.created_by)
    
    async def update(self, o: CommonSetup, table: str):
        async with self.dbp.acquire() as conn:
            await conn.execute(f"""
                update {table} set code = $1, "desc" = $2, ref = $3, modified_by = $4, modified_date = now() where id = $5
            """, o.code, o.desc, o.ref, o.modified_by, o.id)
            
    async def delete_by_id(self, id: int, user_id: int, table: str):
        async with self.dbp.acquire() as conn:
            await conn.execute(f"""
                update {table} set deleted = true, deleted_by = $1, deleted_date = now() where id = $2
            """, user_id, id)