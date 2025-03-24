from aiohttp import web

from . import wish

routes : list[web.AbstractRouteDef] = [
    *wish.routes,
]