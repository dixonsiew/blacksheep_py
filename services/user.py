from models import User, Role
from typing import List

import asyncpg
import bcrypt


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
    
    async def save(self, o: User):
        salt = bcrypt.gensalt(rounds=10)
        pw = o.password.encode('utf-8')
        hashed_password = bcrypt.hashpw(pw, salt)
        psw = hashed_password.decode('utf-8')
        async with self.dbp.acquire() as conn:
            async with conn.transaction():
                id = await conn.fetchval(f"""
                    insert into app_user (id, username, password, first_name, last_name, active) 
                    values(nextval('app_user_id_seq'),$1,$2,$3,$4,$5) returning id as app_user_id       
                """, o.username, psw, o.first_name, o.last_name, True)
                
                for r in o.roles:
                    await conn.execute(f"""
                        insert into app_user_roles (app_user_id, roles_id) values($1, $2)
                    """, id, r.id)
                    
    async def update(self, o: User):
        async with self.dbp.acquire() as conn:
            async with conn.transaction():
                if o.password is not None and o.password != "":
                    salt = bcrypt.gensalt(rounds=10)
                    pw = o.password.encode('utf-8')
                    hashed_password = bcrypt.hashpw(pw, salt)
                    psw = hashed_password.decode('utf-8')
                    await conn.execute(f"""
                        update app_user set password = $1, first_name = $2, last_name = $3 where id = $4
                    """, psw, o.first_name, o.last_name, o.id)
                    
                else:
                    await conn.execute(f"""
                        update app_user set first_name = $1, last_name = $2 where id = $3       
                    """, o.first_name, o.last_name, o.id)
                    
                await conn.execute(f"""
                    delete from app_user_roles where app_user_id = $1
                """, o.id)
                
                for r in o.roles:
                    await conn.execute(f"""
                        insert into app_user_roles (app_user_id, roles_id) values($1, $2)
                    """, o.id, r.id)
    
    async def update_last_login(self, id: int):
        async with self.dbp.acquire() as conn:
            await conn.execute(f"""
                update app_user set last_login = now() where id = $1         
            """, id)
            
    async def update_password(self, o: User):
        salt = bcrypt.gensalt(rounds=10)
        pw = o.password.encode('utf-8')
        hashed_password = bcrypt.hashpw(pw, salt)
        psw = hashed_password.decode('utf-8')
        async with self.dbp.acquire() as conn:
            await conn.execute(f"""
                update app_user set password = $1 where id = $2
            """, psw, o.id)
    
    def validate_credentials(self, user: User, password: str) -> bool:
        password_bytes = password.encode('utf-8')
        user_password_bytes = user.password.encode('utf-8')
        match = bcrypt.checkpw(password_bytes, user_password_bytes)
        return match