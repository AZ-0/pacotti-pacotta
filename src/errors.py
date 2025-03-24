from aiohttp import web


def json_error(status: int, msg: str) -> web.Response:
    return web.json_response(
        { 'err': msg },
        status=status,
    )


@web.middleware
async def error_middleware(req: web.Request, handler):
    """Wraps some errors"""
    try:
        return await handler(req)
    except (AssertionError, TypeError) as e:
        return json_error(422, '; '.join(e.args))


middlewares = [ error_middleware ]