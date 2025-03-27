from aiohttp_session import Session, get_session, new_session
from aiohttp_jinja2 import render_template
from aiohttp import web

from ..keys import SessionKey as skey, RequestKey as rkey, MsgKey as msg
from .. import database as db

routes = web.RouteTableDef()


async def renew_session(req: web.Request) -> tuple[Session,Session]:
    old = await get_session(req)
    new = await new_session(req)
    new[skey.HALTPASS] = skey.HALTPASS(old)
    return old, new


@routes.view('/login')
class Login(web.View):

    async def get(self):
        return render_template('login.html', self.request, {})

    async def post(self):
        data = await self.request.post()
        user = db.user_from_password(rkey.PASSWORD(data))

        if user is None:
            raise web.HTTPUnauthorized(reason=msg.INCORRECT_PASSWORD)

        old, session = await renew_session(self.request)
        session[skey.USER_ID] = user.id

        if (url := old.pop(skey.URL, None)) is None:
            return web.json_response({})

        return web.json_response({ 'url': url })


@routes.post('/logout')
async def logout(req: web.Request):
    await renew_session(req)
    return web.json_response({})


@routes.view('/halt')
class Halt(web.View):

    async def get(self):
        """Halt page"""
        return render_template('halt.html', self.request, {})

    async def post(self):
        """Test password"""
        session = await new_session(self.request)
        data = await self.request.post()

        if rkey.PASSWORD(data) == 'llqepsv':
            session[skey.HALTPASS] = True
            return web.json_response({})

        session[skey.HALTPASS] = False
        raise web.HTTPUnauthorized(reason=msg.INCORRECT_HALTPASS)


@web.middleware
async def halt_middleware(req: web.Request, handler):
    """Website-wide redirect to halt page if not passed"""
    if handler is Halt:
        return await handler(req)

    session = await get_session(req)
    if not skey.HALTPASS(session):
        raise web.HTTPSeeOther('/halt')

    return await handler(req)


middlewares = [
    # halt_middleware, # currently disabled for testing
]