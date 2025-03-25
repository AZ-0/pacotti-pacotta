from typing import TypeVar
from enum import StrEnum

T = TypeVar('T')

class Key(StrEnum):
    def __call__(self, data: dict[str], default: T = None) -> T:
        return data.get(self, default)


class SessionKey(Key):
    PASS     = 'pass'
    USER_ID  = 'uid'


class RequestKey(Key):
    PASSWORD       = 'pwd'
    WISH_CONTENT   = 'wishcontent'
    WISH_ID        = 'wishid'
    WISH_HIDDEN    = 'wishhidden'
    WISH_KIND      = 'wishkind'
    WISH_RECIPIENT = 'wishrecipient'


class AppKey(Key):
    DEBUG = 'debug'