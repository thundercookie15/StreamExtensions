import abc
from collections.abc import Generator
from typing import Any, Iterable, Mapping, Sequence, TypeVar, overload

from more_itertools import peekable

from .client import SimpleIRCClient
from .dict import IRCDict as IRCDict

_T = TypeVar('_T')


class ServerSpec:
    host: str
    port: int
    password: str

    def __init__(self, host: str, port: int = ..., password: str | None = ...) -> None: ...

    @overload
    @classmethod
    def ensure(cls: type[_T], input: _T) -> _T: ...

    @overload
    @classmethod
    def ensure(cls: type[_T], input: tuple[str]) -> _T: ...

    @overload
    @classmethod
    def ensure(cls: type[_T], input: list[str]) -> _T: ...

    @overload
    @classmethod
    def ensure(cls: type[_T], input: tuple[str, int]) -> _T: ...

    @overload
    @classmethod
    def ensure(cls: type[_T], input: list[str | int]) -> _T: ...

    @overload
    @classmethod
    def ensure(cls: type[_T], input: tuple[str, int, str | None]) -> _T: ...

    @overload
    @classmethod
    def ensure(cls: type[_T], input: list[str | int | None]) -> _T: ...


class ReconnectStrategy(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def run(self, bot: SingleServerIRCBot) -> None: ...


class ExponentialBackoff(ReconnectStrategy):
    min_interval: int
    max_interval: int
    attempt_count: Any

    def __init__(self, **attrs: Mapping[str, Any]) -> None: ...

    bot: SingleServerIRCBot

    def run(self, bot: SingleServerIRCBot) -> None: ...

    def check(self) -> None: ...


missing: type[object]


class SingleServerIRCBot(SimpleIRCClient):
    channels: IRCDict
    servers: peekable[Iterable[ServerSpec]]
    recon: ReconnectStrategy

    def __init__(
            self,
            server_list: Sequence[
                ServerSpec
                | tuple[str]
                | list[str]
                | tuple[str, int]
                | list[str | int]
                | tuple[str, int, str | None]
                | list[str | int | None]
                ],
            nickname: str,
            realname: str,
            reconnection_interval: Any = ...,
            recon: ReconnectStrategy = ...,
            **connect_params: Any
    ) -> None: ...

    def die(self, msg: str = ...) -> None: ...

    def disconnect(self, msg: str = ...) -> None: ...

    @staticmethod
    def get_version(): ...

    def jump_server(self, msg: str = ...) -> None: ...

    def on_ctcp(self, connection, event) -> None: ...

    def on_dccchat(self, connection, event) -> None: ...

    def start(self) -> None: ...


class Channel:
    user_modes: str
    mode_users: Any
    modes: Any

    def __init__(self) -> None: ...

    def users(self): ...

    def opers(self): ...

    def voiced(self): ...

    def owners(self): ...

    def halfops(self): ...

    def admins(self): ...

    def has_user(self, nick): ...

    def is_oper(self, nick): ...

    def is_voiced(self, nick): ...

    def is_owner(self, nick): ...

    def is_halfop(self, nick): ...

    def is_admin(self, nick): ...

    def add_user(self, nick) -> None: ...

    @property
    def user_dicts(self) -> Generator[Any, None, None]: ...

    def remove_user(self, nick) -> None: ...

    def change_nick(self, before, after) -> None: ...

    def set_userdetails(self, nick, details) -> None: ...

    def set_mode(self, mode, value: Any | None = ...) -> None: ...

    def clear_mode(self, mode, value: Any | None = ...) -> None: ...

    def has_mode(self, mode): ...

    def is_moderated(self): ...

    def is_secret(self): ...

    def is_protected(self): ...

    def has_topic_lock(self): ...

    def is_invite_only(self): ...

    def has_allow_external_messages(self): ...

    def has_limit(self): ...

    def limit(self): ...

    def has_key(self): ...
