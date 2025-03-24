from model import User, UserID, Wish, WishID

DB_PATH = 'db.sqlite'

users: dict[UserID, User] = {}


def user_from_password(password: str) -> User | None:
    for user in users.values():
        if user.password == password:
            return user


async def is_maker_or_recipient_of(user: UserID, wish: WishID) -> bool:
    """True if the user is the maker or the recipient of the wish, False otherwise"""
    raise NotImplementedError


async def wishes_of(recipient: UserID) -> list[Wish]:
    """List the wishes an user is recipient of"""
    raise NotImplementedError


async def foreign_wishes_of(wishmaker: UserID) -> list[Wish]:
    """List the foreign wishes made by an user"""
    raise NotImplementedError


async def is_maker_of(user: UserID, wish: WishID) -> bool:
    """Whether `user` is the wishmaker of `wish`"""
    raise NotImplementedError


async def register_wish(wish: Wish) -> None:
    """Register a new wish"""
    raise NotImplementedError


async def edit_wish(wish: Wish) -> None:
    """Edit a wish"""
    raise NotImplementedError


async def delete_wish(wish: WishID) -> None:
    """Delete a wish"""
    raise NotImplementedError


async def claim_wish(user: UserID, wish: WishID) -> None:
    """Claim a wish"""
    raise NotImplementedError