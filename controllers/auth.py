from blacksheep.server.controllers import delete, get, post, put
from blacksheep.server.openapi.common import ContentInfo, ParameterInfo, RequestBodyInfo, ResponseInfo
from blacksheep import FromQuery, FromJSON, FromRoute, Request, Response, auth
from blacksheep.cookies import Cookie, CookieSameSiteMode
from guardpost import Identity
from controllers.base import BaseController
from docs import docs
from dto import LoginDto, RefreshTokenDto, ChangePasswordDto
from models import User
from constants.constant import AppConstant
# from cookie_auth import cookie_auth

import jwt, datetime
from datetime import datetime, timedelta, UTC

from services.user import UserService
from services.token import TokenService


@docs.tags("Auth")
class AuthController(BaseController):
    
    def __init__(self, cs: UserService, ts: TokenService):
        self.cs = cs
        self.ts = ts
      
    @docs(responses={200: ResponseInfo('')})
    @post("/o/logout")
    async def logout(self) -> dict:
        res = self.ok({
            "message": "Logged out successfully"
        })
        res.set_cookie(
            Cookie(
                "token",
                "",
                http_only=True,
                secure=False,
                same_site=CookieSameSiteMode.LAX,
                path="/",
                max_age=-1,
                expires=datetime.now(UTC) + timedelta(hours=-1)
            )
        )
        res.set_cookie(
            Cookie(
                "refreshToken",
                "",
                http_only=True,
                secure=False,
                same_site=CookieSameSiteMode.LAX,
                path="/smrp/o/refresh-token",
                max_age=-1,
                expires=datetime.now(UTC) + timedelta(hours=-1)
            )
        )
        # cookie_auth.unset_cookie(res)
        return res
        
    @docs(
        responses={200: ResponseInfo('')},
        parameters={
            "req": ParameterInfo(description="Login Request", value_type=LoginDto)
        }
    )
    @post("/o/token")
    async def login(self, req: FromJSON[dict]) -> dict:
        m = req.value
        data = LoginDto(**m)
        mx = {
            "statusCode": 401,
            "message": "Invalid Credentials"
        }
        user = await self.cs.find_by_username(data.username)
        valid = False
        if user is not None:
            valid = self.cs.validate_credentials(user, data.password)
            
        else:
            return self.unauthorized(mx)
            
        if not valid:
            return self.unauthorized(mx)
        
        await self.cs.update_last_login(user.id)
        
        payload = {
            "username": user.username,
            "sub": str(user.id),
            "exp": datetime.now(UTC) + timedelta(hours=720)
        }
        token = jwt.encode(payload, AppConstant.JWT_SECRET, algorithm="HS256")
        
        payload_refresh = {
            "username": user.username,
            "sub": str(user.id),
            "exp": datetime.now(UTC) + timedelta(hours=87600)
        }
        refresh_token = jwt.encode(payload_refresh, AppConstant.JWT_SECRET, algorithm="HS256")
        res = self.json({
            "type": "bearer",
            "token": token,
            "refresh_token": refresh_token
        })
        res.set_cookie(
            Cookie(
                "token",
                token,
                http_only=True,
                secure=False,
                same_site=CookieSameSiteMode.LAX,
                path="/",
                max_age=30 * 24 * 60 * 60
            )
        )
        res.set_cookie(
            Cookie(
                "refreshToken",
                refresh_token,
                http_only=True,
                secure=False,
                same_site=CookieSameSiteMode.LAX,
                path="/smrp/o/refresh-token",
                max_age=3650 * 24 * 60 * 60
            )
        )
        
        user_data = {
            "username": user.username,
            "sub": str(user.id),
            "exp": int((datetime.now(UTC) + timedelta(hours=720)).timestamp()),
        }

        # cookie_auth.set_cookie(
        #     user_data,
        #     res,
        #     secure=False
        # )
        
        return res
    
    @docs(
        responses={200: ResponseInfo('')},
        parameters={
            "req": ParameterInfo(description="Refresh Token Request", value_type=RefreshTokenDto)
        }
    )
    @post("/o/refresh-token")
    async def refresh(self, req: Request, mr: FromJSON[dict]) -> dict:
        mx = {
            "statusCode": 401,
            "message": "Invalid Credentials"
        }
        refresh_token = req.cookies.get("refreshToken")
        if refresh_token is None or refresh_token == "":
            m = mr.value
            data = RefreshTokenDto(**m)
            if data.refresh_token == "":
                return self.unauthorized(mx)
            
            refresh_token = data.refresh_token
            
        try:
            payload = jwt.decode(refresh_token, AppConstant.JWT_SECRET, algorithms=["HS256"])
            username = payload.get("username")
            sub = payload.get("sub")
            
            payload = {
                "username": username,
                "sub": sub,
                "exp": datetime.now(UTC) + timedelta(hours=720)
            }
            token = jwt.encode(payload, AppConstant.JWT_SECRET, algorithm="HS256")
            
            payload_refresh = {
                "username": username,
                "sub": sub,
                "exp": datetime.now(UTC) + timedelta(hours=87600)
            }
            refresh_token = jwt.encode(payload_refresh, AppConstant.JWT_SECRET, algorithm="HS256")
            res = self.json({
                "type": "bearer",
                "token": token,
                "refresh_token": refresh_token
            })
            res.set_cookie(
                Cookie(
                    "token",
                    token,
                    http_only=True,
                    secure=False,
                    same_site=CookieSameSiteMode.LAX,
                    path="/",
                    max_age=30 * 24 * 60 * 60
                )
            )
            res.set_cookie(
                Cookie(
                    "refreshToken",
                    refresh_token,
                    http_only=True,
                    secure=False,
                    same_site=CookieSameSiteMode.LAX,
                    path="/smrp/o/refresh-token",
                    max_age=3650 * 24 * 60 * 60
                )
            )
            
            user_data = {
                "username": username,
                "sub": sub,
                "exp": int((datetime.now(UTC) + timedelta(hours=720)).timestamp()),
            }
            
            # cookie_auth.set_cookie(
            #     user_data,
            #     res,
            #     secure=False
            # )
            
            return res
            
        except Exception:
            return self.unauthorized(mx)
      
    @docs(responses={200: ResponseInfo('')})
    @auth()
    @get("/api/current-user")
    async def user_details(self, user: Identity | None) -> dict:
        o = await self.ts.get_user(user)
        if o is None:
            return self.unauthorized()

        return self.ok({
            "id": o.id,
            "username": o.username,
            "first_name": o.first_name,
            "last_name": o.last_name,
            "roles": o.roles
        })
     
    @docs(
        responses={200: ResponseInfo('')},
        parameters={
            "req": ParameterInfo(description="Change Password Request", value_type=ChangePasswordDto)
        }
    )
    @auth()  
    @post("/api/change-password") 
    async def change_password(self, req: FromJSON[dict], user: Identity | None) -> dict:
        m = req.value
        data = ChangePasswordDto(**m)
        if data.password != data.confirm_password:
            return self.bad_request({
                "statusCode": 400,
                "message": "Confirm Password does not match"
            })
            
        o = await self.ts.get_user(user)
        if o is None:
            return self.unauthorized()
        
        o.password = data.password
        await self.cs.update_password(o)
        return self.ok({
            "success": 1
        })