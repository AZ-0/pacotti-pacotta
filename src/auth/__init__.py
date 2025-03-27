from aiohttp_session import get_session
from aiohttp import web

from .. keys import SessionKey as skey
from .. import database as db

from .routes import routes, middlewares


def authenticated(handler):
    """Forces user to be authenticated to access this endpoint"""

    async def auth_middleware(req: web.Request):
        session = await get_session(req)

        uid = skey.USER_ID(session)
        if uid is None or (user := db.users.get(int(uid))) is None:
            if req.method == 'GET':
                session[skey.URL] = req.path_qs
            raise web.HTTPSeeOther('/login')

        return await handler(req, user)

    return auth_middleware