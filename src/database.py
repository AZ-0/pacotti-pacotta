from aiohttp.web import Application
from aiosqlite import Cursor, Row, connect
from typing import Iterable, Callable, TypeVar
import os, logging, contextlib

from . model import User, UserID, Wish, WishID, WishKind, ymd_to_date
from . keys import AppKey as akey
from . default_users import DEFAULT_USERS # list[("name", (y, m, d), "pwd")]

DB_PATH = 'db.sqlite'



TABLE_DEF = [
"""
CREATE TABLE IF NOT EXISTS users (
    id   INTEGER NOT NULL,
    name TEXT    NOT NULL UNIQUE,
    bday INTEGER NOT NULL,
    pwd  TEXT    NOT NULL,

    PRIMARY KEY(id)
) STRICT;
""",
"""
CREATE TABLE IF NOT EXISTS wishes (
    id        INTEGER NOT NULL,
    recipient INTEGER NOT NULL,
    maker     INTEGER NOT NULL,
    claimant   INTEGER,
    kind      INTEGER NOT NULL,
    content   TEXT    NOT NULL,
    hidden    INT     NOT NULL,
    date      INTEGER NOT NULL,

    PRIMARY KEY(id),
    FOREIGN KEY(recipient) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(maker)     REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(claimant)  REFERENCES users(id) ON DELETE SET NULL
) STRICT;
""",
*(f"""
INSERT OR REPLACE INTO users (name,bday,pwd) VALUES ({name},{ymd_to_date(y, m, d)},"{pwd}");
""" for name, (y, m, d), pwd in DEFAULT_USERS),
]

T = TypeVar('T')
logger = logging.Logger(__file__)
users: dict[UserID, User] = {}

def user_from_password(password: str) -> User | None:
    for user in users.values():
        if user.password == password:
            return user


def parse_user(row: Row) -> User:
    return User(
        id   = row[0],
        name = row[1],
        birthday = row[2],
        password = row[3],
    )


def parse_wish(row: Row) -> Wish:
    wish = Wish(
        id = row[0],
        recipient = users[row[1]],
        maker     = users[row[2]],
        claimant  = users.get(row[3]),
        kind    = WishKind(row[4]),
        content = row[5],
        hidden  = bool(row[6]),
        date = row[7],
    )
    print(f"Parsed wish {wish.content}. Claimant {wish.claimant}")
    return wish


##### META


async def debug_users():
    await execute_commit('INSERT INTO users (name,bday,pwd) VALUES ("userA",42,"pwdA");')
    await execute_commit('INSERT INTO users (name,bday,pwd) VALUES ("userB",87,"pwdB");')


async def debug_wishes():
    admin, userA, userB = users.values()
    await register_wish(Wish(None,admin,admin,userA,0,"admin←admin",False,48646))
    await register_wish(Wish(None,admin,userA,None,1,"admin←userA",False,45352))
    await register_wish(Wish(None,admin,userB,userB,0,"admin←userB",True,35435))


async def startup(app: Application):
    global DB_PATH

    if app[akey.DEBUG]:
        DB_PATH = 'debug-db.sqlite'
        with contextlib.suppress(FileNotFoundError):
            os.remove(DB_PATH)

    await execute_many(TABLE_DEF)
    app.logger.info(f"Initialized database at {DB_PATH}")

    if app[akey.DEBUG]:
        await debug_users()

    for row in await execute_fetchall("SELECT * FROM users"):
        user = parse_user(row)
        users[user.id] = user
    app.logger.info(f"Loaded {len(users)} users")

    if app[akey.DEBUG]:
        await debug_wishes()


async def execute_fetchall(statement: str, *args) -> Iterable[Row]:
    '''Read all, no commitment.'''
    async with connect(DB_PATH) as db:
        return await db.execute_fetchall(statement, args)


async def execute_fetchone(statement: str, *args) -> Row:
    '''Read one, no commitment.'''
    async with connect(DB_PATH) as db:
        return await (await db.execute(statement, args)).fetchone()


async def execute_many(statements: Iterable[str]) -> None:
    '''Perform statements, then commit.'''
    async with connect(DB_PATH) as db:
        for statement in statements:
            await db.execute(statement)
        await db.commit()


async def execute_commit(statement: str, *args, extractor: Callable[[Cursor], T] = lambda c: c) -> T:
    """When extracting data such as last insert id, it is important to retrieve it right after the execution (before the commitment!).
    Commitment may perform internal operations that would change the desired values.
    Some data may only be gathered when the connection is alive."""
    async with connect(DB_PATH) as db:
        data = extractor(await db.execute(statement, args))
        await db.commit()
        return data


##### READ


async def wish(id: WishID) -> Wish | None:
    data = await execute_fetchone(
        "SELECT * FROM wishes WHERE id = ?",
        id
    )
    if data is None:
        return None
    return parse_wish(data)


async def own_wish(user: UserID, wish: WishID) -> bool:
    """True if (user is maker) or (user is recipient and wish not hidden)"""
    data = await execute_fetchone(
        "SELECT EXISTS(SELECT 1 FROM wishes WHERE id = ? AND (maker = ? OR (recipient = ? AND hidden = FALSE)) LIMIT 1)",
        wish, user, user
    )
    return data


async def maker_of(wish: WishID) -> User:
    data = await execute_fetchone(
        "SELECT maker FROM wishes WHERE id = ?",
        wish
    )
    return users[data['maker']]


async def wishes_of(recipient: UserID) -> list[Wish]:
    """List the wishes an user is recipient of"""
    data = await execute_fetchall(
        "SELECT * FROM wishes WHERE recipient = ?",
        recipient
    )
    return sorted([ parse_wish(row) for row in data ], key=lambda w:w.id)


async def foreign_wishes_of(maker: UserID) -> list[Wish]:
    """List the foreign wishes made by an user"""
    data = await execute_fetchall(
        "SELECT * FROM wishes WHERE maker = ? AND recipient != ?",
        maker, maker
    )
    return sorted([ parse_wish(row) for row in data ], key=lambda w:w.id)


##### CREATE


async def register_wish(wish: Wish) -> WishID:
    """Register a new wish"""
    id = await execute_commit(
        "INSERT INTO wishes (recipient, maker, claimant, kind, content, hidden, date) VALUES (?,?,?,?,?,?,?)",
        wish.recipient.id, wish.maker.id, wish.claimant_id, wish.kind, wish.content, wish.hidden, wish.date,
        extractor = lambda c: c.lastrowid
    )
    return id


##### UPDATE


async def edit_wish(wish: Wish) -> None:
    """Edit a wish"""
    await execute_commit(
        "UPDATE wishes SET recipient = ?, kind = ?, content = ?, hidden = ? WHERE id = ?",
        wish.recipient.id, wish.kind, wish.content, wish.hidden, wish.id,
    )


async def claim_wish(user: UserID, wish: WishID) -> None:
    """Claim a wish"""
    await execute_commit(
        "UPDATE wishes SET claimant = ? WHERE id = ?",
        user, wish
    )


##### DELETE


async def delete_wish(wish: WishID) -> None:
    """Delete a wish"""
    await execute_commit(
        "DELETE FROM wishes WHERE id = ?",
        wish
    )