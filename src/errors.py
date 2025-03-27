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
    except AssertionError as e:
        return json_error(422, '; '.join(e.args))
    except web.HTTPError as e:
        return json_error(e.status_code, e.reason)



middlewares = [ error_middleware ]