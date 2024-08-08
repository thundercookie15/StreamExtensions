from typing import Any

from jaraco.text import FoldedCase


class IRCFoldedCase(FoldedCase):
    translation: Any

    def lower(self): ...


def lower(str): ...
