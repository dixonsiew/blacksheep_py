import secrets
from blacksheep.server.authentication.cookie import CookieAuthentication


cookie_auth = CookieAuthentication(
    cookie_name="token",
    secret_keys=[
        secrets.token_urlsafe(32),
        secrets.token_urlsafe(32),
    ],
)