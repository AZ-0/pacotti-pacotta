from dataclasses import dataclass
from markupsafe import escape
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

    def __eq__(self, other) -> bool:
        return isinstance(other, User) and other.id == self.id

    def html_tag(self, *classes, **kwclasses) -> str:
        kwclasses = ' '.join(f'{cls}={val}' for cls,val in kwclasses.items())
        classes = ' '.join(classes)

        return ' '.join([
            '<x-user',
            f'uid={self.id}',
            f'bday={self.birthday}',
            f'name="{escape(self.name)}"',
            kwclasses,
            classes,
        ]) + '></x-user>'


@dataclass
class Wish:
    id:        WishID   # identifier of a wish
    recipient: User     # person who would receive the gift
    maker:     User     # person who created the wish
    claim:     User     # person who would give the gift
    kind:      WishKind # kind of wish
    content:   str      # text content of the wish
    hidden:    bool     # whether the wish is hidden from the recipient

    def __post_init__(self):
        self.foreign: bool = self.maker.id != self.recipient.id
        assert self.foreign or not self.hidden  # you cannot hide from your own wishes!

    def __eq__(self, other) -> bool:
        return isinstance(other, User) and other.id == self.id

    def html_tag(self) -> str:
        parts = [
            '<x-wish',
            f'wishid={self.id}',
            f'kind={self.kind}',
            f'content="{escape(self.content)}"',
        ]
        if self.hidden:
            parts.append('x-hidden')
        return ' '.join(parts) + ''.join([
            '>',
            self.recipient.html_tag('disabled'),
            self.maker.html_tag('disabled'),
            self.claim.html_tag('disabled') if self.claim else '',
            '</x-wish>'
        ])
