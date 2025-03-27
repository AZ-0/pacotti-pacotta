from typing import TypeVar
from enum import StrEnum

T = TypeVar('T')

class Key(StrEnum):
    def __call__(self, data: dict[str], default: T = None) -> T:
        return data.get(self, default)


class SessionKey(Key):
    HALTPASS = 'haltpass'
    URL = 'url'
    USER_ID  = 'uid'


class RequestKey(Key):
    PASSWORD       = 'pwd'
    WISH_CONTENT   = 'content'
    WISH_ID        = 'wishid'
    WISH_HIDDEN    = 'hidden'
    WISH_KIND      = 'kind'
    WISH_RECIPIENT = 'recipient'


class AppKey(Key):
    DEBUG = 'debug'

class MsgKey(Key):
    INCORRECT_HALTPASS = 'incorrect-haltpass'
    INCORRECT_PASSWORD = 'incorrect-password'
