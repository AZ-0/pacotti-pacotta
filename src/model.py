from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum

UserID = int
WishID = int
Date = int   # year*366



MONTHS_TIME = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def date_to_ymd(date: Date) -> tuple[int, int, int]:
    year, day = divmod(date, 366)
    MONTHS_TIME[1] = 28 + (not year % 4) # if this isn't good enough I'll add an edge case later
    for i, m in enumerate(MONTHS_TIME):
        if day < m: break
        day -= m
    return year, i+1, day+1


def ymd_to_date(year: int, month: int, day: int) -> Date:
    date = year*366
    MONTHS_TIME[1] = 28 + (not year % 4)
    for i in range(month-1):
        date += MONTHS_TIME[i]
    return date + day-1


def date_to_str(date: Date) -> str:
    year, month, day = date_to_ymd(date)
    return f'{day}/{month}/{year}'



class WishKind(IntEnum):
    # Autre
    OTHER = 0
    # Utile
    USEFUL = 1
    # Lire
    BOOK = 2
    COMIC_STRIP = 3
    # Jouer
    BOARD_GAME = 4
    TOY = 5
    VIDEO_GAME = 6
    # Regarder
    CINEMA = 7
    DVD = 8
    SHOW = 9
    # Écouter
    CD = 10
    VINYL = 11
    # Manger
    FOOD = 12
    RESTAURANT = 13
    # Se Pavaner
    ACCESSORIES = 14
    CLOTHES = 15
    COSMETICS = 16


    def __str__(self):
        return _wishkind_translate[self]


_wishkind_translate = {
    WishKind.OTHER : "Autre",
    WishKind.USEFUL : "Utile",

    WishKind.BOOK : "Livre",
    WishKind.COMIC_STRIP : "BD",

    WishKind.BOARD_GAME : "Jeu de Société",
    WishKind.TOY : "Jouet",
    WishKind.VIDEO_GAME : "Jeu Vidéo",

    WishKind.CINEMA : "Cinéma",
    WishKind.DVD : "DVD",
    WishKind.SHOW : "Spectacle",

    WishKind.CD : "CD",
    WishKind.VINYL : "Vinyle",

    WishKind.FOOD : "Nourriture",
    WishKind.RESTAURANT : "Resto",

    WishKind.ACCESSORIES : "Accessoires",
    WishKind.CLOTHES : "Vêtements",
    WishKind.COSMETICS : "Cosmétiques",
}


WISHKINDS = { kind.value : kind for kind in WishKind }


WISHSORT: list[WishKind | tuple[WishKind, list[WishKind]]] = [
    ("Lire", [WishKind.BOOK, WishKind.COMIC_STRIP]),
    ("Jouer", [WishKind.BOARD_GAME, WishKind.TOY, WishKind.VIDEO_GAME]),
    ("Regarder", [WishKind.CINEMA, WishKind.DVD, WishKind.SHOW]),
    ("Écouter", [WishKind.CD, WishKind.VINYL]),
    ("Manger", [WishKind.FOOD, WishKind.RESTAURANT]),
    ("Se pavaner", [WishKind.ACCESSORIES, WishKind.CLOTHES, WishKind.COSMETICS]),
    WishKind.USEFUL,
    WishKind.OTHER,
]

for category in WISHSORT:
    if isinstance(category, WishKind):
        continue
    category[1].sort(key=str)



@dataclass
class User:
    id:       UserID  # identifier of the user
    name:     str     # name of the user
    birthday: Date    # birthday date of the user
    password: str     # (plaintext!) password of the user

    def __eq__(self, other) -> bool:
        return isinstance(other, User) and other.id == self.id



@dataclass
class Wish:
    id:        WishID   # identifier of a wish
    recipient: User     # person who would receive the gift
    maker:     User     # person who created the wish
    claimant:  User | None # person who would give the gift
    kind:      WishKind # kind of wish
    content:   str      # text content of the wish
    hidden:    bool     # whether the wish is hidden from the recipient
    date:      Date     # creation date of the wish


    def __post_init__(self):
        self.foreign: bool = self.maker.id != self.recipient.id
        assert self.foreign or not self.hidden, "On ne peut se cacher de soi-même !"  # you cannot hide from your own wishes!

        if self.date is None:
            today = datetime.today()
            self.date = ymd_to_date(today.year, today.month, today.day)


    def __eq__(self, other) -> bool:
        return isinstance(other, Wish) and other.id == self.id


    @property
    def claimant_id(self) -> int | None:
        '''Convenience getter for claimant.id, as this may be None'''
        if self.claimant:
            return self.claimant.id
        return None


    def owned_by(self, uid: UserID) -> bool:
        return (uid == self.maker.id) or (uid == self.recipient.id and not self.hidden)


    def date_str(self) -> str:
        return date_to_str(self.date)
