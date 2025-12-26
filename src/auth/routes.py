from aiohttp_session import Session, get_session, new_session
from aiohttp_jinja2 import render_template
from aiohttp import web

from ..model import User
from ..keys import SessionKey as skey, RequestKey as rkey, MsgKey as msg
from .. import database as db

routes = web.RouteTableDef()


async def renew_session(req: web.Request) -> tuple[Session,Session]:
    old = await get_session(req)
    new = await new_session(req)
    new[skey.HALTPASS] = skey.HALTPASS(old)
    return old, new


@routes.view('/halt')
class Halt(web.View):

    async def get(self):
        """Halt page"""
        return render_template('auth.html', self.request, {
            "prompt" : "Halte ! Quel est le mot de passe ?",
            "action" : "halt"
        })

    async def post(self):
        """Test password"""
        data = await self.request.post()
        _, session = await renew_session(self.request)

        session[skey.HALTPASS] = haltpass = str(rkey.PASSWORD(data)).lower() == 'llqepsv'

        if not haltpass:
            raise web.HTTPUnauthorized(reason=msg.INCORRECT_HALTPASS)

        return web.HTTPOk()


@web.middleware
async def halt_middleware(req: web.Request, handler):
    """Website-wide redirect to halt page if not passed"""
    if req.path.startswith('/static/') or req.path == '/favicon.ico':
        return await handler(req)

    session = await get_session(req)
    if not skey.HALTPASS(session):
        return await Halt(req)

    return await handler(req)

middlewares = [
    halt_middleware, # currently disabled for testing
]


@routes.view('/login')
class Login(web.View):

    async def get(self):
        return render_template('auth.html', self.request, {
            "prompt" : "Entre ton mot de passe personnel:",
            "action" : "login"
        })

    async def post(self):
        data = await self.request.post()
        user = db.user_from_password(rkey.PASSWORD(data))

        if user is None:
            raise web.HTTPUnauthorized(reason=msg.INCORRECT_PASSWORD)

        _, session = await renew_session(self.request)
        session[skey.USER_ID] = user.id

        return web.HTTPOk()


@routes.get('/logout')
async def logout(req: web.Request):
    await renew_session(req)
    return web.HTTPFound('/')



async def current_user(req: web.Request) -> User:
    uid = skey.USER_ID(await get_session(req))
    return db.users.get(int(uid)) if uid else None


def authenticated(handler):
    """No pasarán"""

    async def auth_middleware(req: web.Request):
        return await (
            handler(req, user)
                if (user := await current_user(req)) else
            Login(req)
        )

    return auth_middleware
