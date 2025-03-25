from aiohttp_jinja2 import render_template
from aiohttp import web

from ... model import User, Wish, wishkinds
from ... auth import authenticated
from ... keys import RequestKey as rkey
from ... import database as db

routes = web.RouteTableDef()

# wishs:
#  - add a wish
#  - see your wishes
#    - modify your wish
#    - delete your wish
#  - see other people's wishes
#    - claim a wish


def parse_wish(data: dict[str]):
    recipient = rkey.WISH_RECIPIENT(data)
    kind      = rkey.WISH_KIND(data)
    hidden    = rkey.WISH_HIDDEN(hidden)
    content   = rkey.WISH_CONTENT(content)

    recipient = db.users.get(recipient)
    kind    = wishkinds.get(kind)
    hidden  = bool(hidden)
    content = str(content)

    assert recipient is not None, "destinataire inconnu"
    assert kind is not None,      "type de souhait inconnu"
    return recipient, kind, hidden, content


@routes.get('/wish')
@authenticated
async def wish_home(req: web.Request, user: User):
    return render_template('wish/index.html', req, { 'user': user })


@routes.get('/wish/view/self')
@authenticated
async def view_self(req: web.Request, user: User):
    wishes = [ wish for wish in await db.wishes_of(user.id) if not wish.hidden ]
    return render_template('wish/view-self.html', req, { 'user': user, 'wishes': wishes })


@routes.get('/wish/view/foreign')
@authenticated
async def view_foreign(req: web.Request, user: User):
    wishes = await db.foreign_wishes_of(user.id)
    return render_template('wish/view-foreign.html', req, { 'user': user, 'wishes': wishes })


@routes.get('/wish/view/other')
@authenticated
async def view_other(req: web.Request, user: User):
    return render_template('wish/view-other-select.html', req, { 'user': user, 'users': db.users })


@routes.get('/wish/view/{id:\d+}')
@authenticated
async def view_other(req: web.Request, user: User):
    uid = int(req.match_info['id'])
    if uid == user.id:
        raise web.HTTPFound('/wish/view/self')

    recipient = db.users.get(uid)
    assert recipient is not None

    wishes = await db.wishes_of(recipient.id)
    return render_template('wish/view-other.html', req, { 'user': user, 'recipient': recipient, 'wishes': wishes })


@routes.get('/wish/new')
@authenticated
async def new(req: web.Request, user: User):
    return render_template('wish/editor.html', req, { 'user': user, 'new': True })


@routes.post('/wish/new')
@authenticated
async def new(req: web.Request, user: User):
    data = await req.post()

    recipient, kind, hidden, content = parse_wish(data)

    id = await db.register_wish(wish := Wish(
        id=None,
        recipient=recipient,
        maker=user,
        claim=None,
        kind=kind,
        content=content,
        hidden=hidden,
    ))

    if wish.foreign:
        raise web.HTTPFound(f'/wish/view/foreign#{id}')
    raise web.HTTPFound(f'/wish/view/self#{id}')


@routes.get('/wish/edit/{id:\d+}')
@authenticated
async def edit(req: web.Request, user: User):
    wishid = int(req.match_info['id'])

    if not await db.own_wish(user.id, wishid):
        raise web.HTTPForbidden(text="Tu n'as pas la permission de modifie ce souhait !")

    wish = await db.wish(wishid)
    return render_template('wish/editor.html', req, { 'user': user, 'new': False, 'wish': wish })


@routes.post('/wish/edit')
@authenticated
async def edit(req: web.Request, user: User):
    data = await req.post()
    recipient, kind, hidden, content = parse_wish(data)
    wishid = int(rkey.WISH_ID(data))

    if not await db.own_wish(user.id, wishid):
        raise web.HTTPForbidden(text="Tu n'as pas la permission de modifier ce souhait !")

    await db.edit_wish(wish := Wish(
        id=wishid,
        recipient=recipient,
        maker=user,
        claim=None,
        kind=kind,
        content=content,
        hidden=hidden,
    ))

    if wish.foreign:
        raise web.HTTPFound(f'/wish/view/foreign#{wish.id}')
    raise web.HTTPFound(f'/wish/view/self#{wish.id}')


@routes.post('/wish/delete')
@authenticated
async def delete(req: web.Request, user: User):
    data = await req.post()
    id = int(rkey.WISH_ID(data))

    if not await db.own_wish(user.id, id):
        raise web.HTTPForbidden(text="Tu n'as pas la permission de supprimer ce souhait !")

    await db.delete_wish(id)
    return web.json_response({ 'msg': "Souhait supprimé !" })


@routes.post('/wish/claim')
@authenticated
async def claim(req: web.Request, user: User):
    data = await req.post()
    id = int(rkey.WISH_ID(data))

    await db.claim_wish(user.id, id)
    return web.json_response({ 'msg': "Souhait revendiqué !" })