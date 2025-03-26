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

    def js(self) -> str:
        """Converts to javascript; for use in jinja2 templating"""
        return f'new User({self.id}, {repr(self.name)}, {self.birthday})'

    def html_tag(self, disabled=False) -> str:
        return ''.join([
            '<x-user',
            f' uid={self.id}',
            f' bday={self.birthday}',
            f' name="{escape(self.name)}"',
            ' disabled' if disabled else '',
            '></x-user>'
        ])


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

    def js(self) -> str:
        """Converts to javascript; for use in jinja2 templating"""
        claim  = 'null' if self.claim is None else self.claim.js()
        hidden = str(self.hidden).lower()
        return f'new Wish({self.id}, {self.recipient.js()}, {self.maker.js()}, {claim}, {self.kind}, {repr(self.content)}, {hidden})'

    def html_tag(self) -> str:
        return ''.join([
            '<x-wish',
            f' wishid={self.id}',
            f' kind={self.kind}',
            f' content="{escape(self.content)}"',
            ' x-hidden' if self.hidden else '',
            '>',
            self.recipient.html_tag(disabled=True),
            self.maker.html_tag(disabled=True),
            self.claim.html_tag(disabled=True) if self.claim else '',
            '</x-wish>'
        ])