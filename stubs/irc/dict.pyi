from collections.abc import KeysView

from jaraco.collections import KeyTransformingDict


class IRCDict(KeyTransformingDict):
    @staticmethod
    def transform_key(key): ...

    def keys(self) -> KeysView[str]: ...
