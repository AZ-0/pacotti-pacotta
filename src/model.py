from dataclasses import dataclass
from enum import IntEnum

UserID = int
WishID = int
Date = int

class WishKind(IntEnum):
    BOOK = 0
    VIDEO_GAME = 1

wishkinds = { kind.value : kind for kind in WishKind }


@dataclass
class User:
    id:       UserID  # identifier of the user
    name:     str     # name of the user
    birthday: Date    # birthday date of the user
    password: str     # (plaintext!) password of the user


@dataclass
class Wish:
    id:        WishID   # identifier of a wish
    recipient: User     # person who would receive the gift
    wishmaker: User     # person who created the wish
    claim:     User     # person who would give the gift
    kind:      WishKind # kind of wish
    content:   str      # text content of the wish
    hidden:    bool     # whether the wish is hidden from the recipient

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.foreign: bool = self.wishmaker.id != self.recipient.id
        assert self.foreign or not self.hidden  # you cannot hide from your own wishes!