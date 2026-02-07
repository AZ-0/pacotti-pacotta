from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_session import SimpleCookieStorage, session_middleware
from aiohttp_jinja2 import render_template, setup as jinja2_setup
from aiohttp import web
from jinja2 import FileSystemLoader
import logging
import os

from .keys import AppKey as akey
from .auth import current_user
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


routes.static('/static', 'src/static')


async def basic_context(req: web.Request) -> dict[str]:
    return { 'user' : await current_user(req), 'users' : db.users }


def init(argv: list[str] = []):
    """Create application"""
    DEBUG = '--debug' in argv

    if DEBUG:
        logging.basicConfig(level=logging.DEBUG)
        storage = SimpleCookieStorage()
    else:
        logging.basicConfig(level=logging.INFO)
        storage = EncryptedCookieStorage(os.urandom(32))

    app = web.Application(middlewares=[
        session_middleware(storage),
        *errors.middlewares,
        *auth.middlewares,
    ])

    app[akey.DEBUG] = DEBUG
    app.logger.warning('----------------------------')
    app.logger.warning("Running on DEBUG mode: %s", DEBUG)
    app.logger.warning('----------------------------')

    app.add_routes(routes)
    app.add_routes(auth.routes)
    app.add_routes(segments.routes)

    jinja2_setup(app, loader=FileSystemLoader('src/templates/'), context_processors=[basic_context])


    app.on_startup.append(db.startup)
    return app


if __name__ == '__main__':
    from pathlib import Path
    from sys import argv
    os.chdir(Path(__file__).parent.parent.absolute())

    app = init(argv)
    web.run_app(app, port=80)
