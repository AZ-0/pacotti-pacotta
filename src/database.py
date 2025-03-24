from aiosqlite import connect

from model import User, UserID, Wish, WishID, WishKind

DB_PATH = 'db.sqlite'

TABLE_DEF = """
CREATE TABLE IF NOT EXISTS users (
    id   INTEGER NOT NULL,
    name TEXT    NOT NULL,
    bday INTEGER NOT NULL,

    PRIMARY KEY(id),
) STRICT;

CREATE TABLE IF NOT EXISTS wishes (
    id        INTEGER NOT NULL,
    recipient INTEGER NOT NULL,
    maker     INTEGER NOT NULL,
    claim     INTEGER,
    kind      INTEGER NOT NULL,
    content   TEXT    NOT NULL,
    hidden    BOOLEAN NOT NULL,

    PRIMARY KEY(id),
    FOREIGN KEY(recipient) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(maker)     REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(claim)     REFERENCES users(id) ON DELETE SET NULL,
) STRICT;
"""


async def init():
    async with connect(DB_PATH) as db:
        await db.execute(TABLE_DEF)
        await db.commit()


users: dict[UserID, User] = {}


def user_from_password(password: str) -> User | None:
    for user in users.values():
        if user.password == password:
            return user


def parse_wish(row) -> Wish:
    return Wish(
        id = row['id'],
        recipient = users.get(row['recipient']),
        wishmaker = users.get(row['maker']),
        claim     = users.get(row['claim']),
        kind    = WishKind(row['kind']),
        content = row['content'],
        hidden  = bool(row['hidden'])
    )


async def execute_fetchall(statement, *args):
    async with connect(DB_PATH) as db:
        data = await db.execute_fetchall(statement, args)
        await db.commit()
        return data


async def is_maker_or_recipient_of(user: UserID, wish: WishID) -> bool:
    """True if the user is the maker or the recipient of the wish, False otherwise"""
    data = await execute_fetchall(
        "EXISTS(SELECT 1 FROM wishes WHERE id = ? AND (maker = ? OR recipient = ?))",
        wish, user, user
    )
    return data[0]


async def wishes_of(recipient: UserID) -> list[Wish]:
    """List the wishes an user is recipient of"""
    data = await execute_fetchall(
        "SELECT * FROM wishes WHERE recipient = ?",
        recipient
    )

    return [ parse_wish(row) for row in data ]



async def foreign_wishes_of(wishmaker: UserID) -> list[Wish]:
    """List the foreign wishes made by an user"""
    data = await execute_fetchall(
        "SELECT * FROM wishes WHERE maker = ? AND recipient != ?",
        wishmaker, wishmaker
    )

    return [ parse_wish(row) for row in data ]


async def register_wish(wish: Wish) -> None:
    """Register a new wish"""
    await execute_fetchall(
        "INSERT INTO wishes (recipient, maker, kind, content, hidden) VALUES (?,?,?,?,?)",
        wish.recipient, wish.wishmaker, wish.kind, wish.content, wish.hidden
    )


async def edit_wish(wish: Wish) -> None:
    """Edit a wish"""
    await execute_fetchall(
        "UPDATE wishes SET recipient = ?, kind = ?, content = ?, hidden = ? WHERE id = ?",
        wish.recipient, wish.kind, wish.content, wish.hidden, wish.id
    )


async def delete_wish(wish: WishID) -> None:
    """Delete a wish"""
    await execute_fetchall(
        "DELETE FROM wishes WHERE id = ?",
        wish
    )


async def claim_wish(user: UserID, wish: WishID) -> None:
    """Claim a wish"""
    await execute_fetchall(
        "UPDATE wishes SET claim = ? WHERE id = ?",
        user, wish
    )