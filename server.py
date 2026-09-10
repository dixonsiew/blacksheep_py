from blacksheep import Application, Request, Response, get, bad_request, json
from blacksheep.exceptions import HTTPException

import asyncpg
from asyncpg import Pool
from typing import Optional
from pydantic import ValidationError
from dotenv import load_dotenv

from docs import docs
from config import Config

from services.common_setup import CommonSetupService
from services.user import UserService

class MyApp(Application):
    async def handle_internal_server_error(self, request: Request, exc: Exception):
        s = exc.status_code if isinstance(exc, HTTPException) else 500 
        return json({
            "statusCode": s,
            "message": exc.message if isinstance(exc, HTTPException) else str(exc)
        }, s)
        

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

load_dotenv()
Config.init()

app = Application()

def register():
    import controllers.setup.city
    import controllers.setup.user

register()

@app.exception_handler(Exception)
async def handle_internal_server_error(self, request, exc: Exception):
    s = exc.status_code if isinstance(exc, HTTPException) else 500 
    return json({
        "statusCode": s,
        "message": exc.message if isinstance(exc, HTTPException) else str(exc)
    }, s)


@app.exception_handler(ValidationError)
async def pydantic_validation_error_handler(self, request, exc: ValidationError) -> Response:
    errs = exc.errors()
    lm = []
    for err in errs:
        s = ".".join(str(loc) for loc in err["loc"])
        ms = err["msg"]
        lm.append(f"[{s}] {ms}")

    return bad_request({
        "statusCode": 400,
        "message": " and ".join(lm)
    })
    
# app.exceptions_handlers[Exception] = handle_internal_server_error
# app.exceptions_handlers[ValidationError] = pydantic_validation_error_handler

@app.on_start
async def configure_database(application: Application) -> None:
    """Initialize database connection pool on app startup."""
    pool = await asyncpg.create_pool(**DB_CONFIG)
    application.services.add_instance(pool, asyncpg.Pool)
    application.services.add_transient(CommonSetupService)
    application.services.add_transient(UserService)

@app.on_stop
async def close_database_connection(application: Application) -> None:
    """Close database connection pool on app shutdown."""
    if pool:
        await pool.close()

app.serve_files("public", root_path="public", fallback_document="index.html")

docs.bind_app(app)


# http://localhost:8000/public/rapidoc/index.html#overview