from aiohttp_session import Session, get_session, new_session
from aiohttp_jinja2 import render_template
from aiohttp import web

from ..keys import SessionKey as skey, RequestKey as rkey
from .. import database as db

routes = web.RouteTableDef()


async def renew_session(req: web.Request) -> Session:
    old = await get_session(req)
    new = await new_session(req)
    new[skey.PASS] = skey.PASS(old)
    return new


@routes.view('/login')
class Login(web.View):

    async def get(self):
        return render_template('login.html', self.request, {})

    async def post(self):
        data = await self.request.post()
        user = db.user_from_password(rkey.PASSWORD(data))

        if user is not None:
            session = await renew_session(self.request)
            session[skey.USER_ID] = user.id
            return web.json_response({ 'msg': f'Bienvenue, {user.name} !' })

        return web.json_response({ 'err': "Mot de passe incorrect." })


@routes.post('/logout')
async def logout(req: web.Request):
    await renew_session(req)
    return web.json_response({ 'msg': "Déconnecté !" })


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
            session[skey.PASS] = True
            raise web.HTTPFound('/')

        session[skey.PASS] = False
        return web.json_response({ 'err': "Souviens-toi de la chanson, et essaie encore !" })


@web.middleware
async def halt_middleware(req: web.Request, handler):
    """Website-wide redirect to halt page if not passed"""
    if handler is Halt:
        return await handler(req)

    session = await get_session(req)
    if not skey.PASS(session):
        raise web.HTTPFound('/halt')

    return await handler(req)


middlewares = [
    # halt_middleware, # currently disabled for testing
]