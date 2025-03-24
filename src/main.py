from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_session import session_middleware
from aiohttp_jinja2 import render_template
from aiohttp import web
import os

from . import database as db
from . import segments
from . import errors
from . import auth

routes = web.RouteTableDef()


@routes.get('/')
async def index(req: web.Request):
    """Home page"""
    return render_template('index.html', req, {})


@routes.get('/dump')
async def dump(req: web.Request):
    """Dump database"""
    return web.FileResponse(db.DB_PATH)


def init(argv: list[str] = []):
    """Create application"""
    storage = EncryptedCookieStorage(os.urandom(32))

    app = web.Application(middlewares=[
        session_middleware(storage),
        *errors.middlewares,
        *auth.middlewares,
    ])

    app.add_routes(routes)
    app.add_routes(auth.routes)
    app.add_routes(segments.routes)
    return app


if __name__ == '__main__':
    app = init()
    web.run_app(app)
