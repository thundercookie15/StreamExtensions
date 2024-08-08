from collections.abc import Sequence
from typing import ClassVar

from streamchatwars._shared.constants import INPUT_TYPE
from streamchatwars._shared.types import VerbParamDict, Partial_VerbParamDict
from streamchatwars.actionsets.actionset import Actionset
from streamchatwars.actionsets.subclasses.base_multikey import partial_create_verb_params
from streamchatwars.actionsets.subclasses.gamepad import Gamepad_Actionset


class SNES_GP_Actionset(Gamepad_Actionset):
    name: ClassVar[str] = 'SNES (Gamepad)'

    '''    
    Action      | Player       |
    ------------| ------------ |
    Up          | Dpad Up      |
    Down        | Dpad Down    |
    Left        | Dpad Left    |
    Right       | Dpad Right   |
    A           | A            |
    B           | B            |
    X           | X            |
    Y           | Y            |
    Rb          | Rb           |
    Lb          | Lb           |
    Start       | Start        |
    Select      | Back         |
    '''

    key_dict: ClassVar[dict[str, str]] = {
        'up': 'dpad_up',
        'down': 'dpad_down',
        'left': 'dpad_left',
        'right': 'dpad_right',
        'a': 'a',
        'b': 'b',
        'x': 'x',
        'y': 'y',
        'rb': 'rb',
        'lb': 'lb',
        'start': 'start',
        'select': 'back',
    }

    def __init__(self, doc_url: str = "", **kwargs):
        super().__init__(doc_url=doc_url, **kwargs)
        self.verb_dict = _build_verb_dict_1(self.action_prefix)


def _build_verb_dict_1(action_prefix: str) -> dict[str, list[VerbParamDict]]:
    verb_param: Partial_VerbParamDict = partial_create_verb_params(
        duration=100,
        delay=0,
        min_time=1,
        max_time=500,
        input_type=INPUT_TYPE.PRESS_KEY
    )

    verb_dict: dict[str, list[VerbParamDict]] = {
        'up': [verb_param(key='up')],
        'down': [verb_param(key='down')],
        'left': [verb_param(key='left')],
        'right': [verb_param(key='right')],
        'a': [verb_param(key='b')],
        'b': [verb_param(key='a')],
        'x': [verb_param(key='y')],
        'y': [verb_param(key='x')],
        'rb': [verb_param(key='rb')],
        'lb': [verb_param(key='lb')],
        'start': [verb_param(key='start')],
        'select': [verb_param(key='select')],
    }

    vd_aliases: dict[str, str] = {
        'u': 'up',
        'd': 'down',
        'l': 'left',
        'r': 'right'
    }

    for alias, original in vd_aliases.items():
        verb_dict[alias] = verb_dict[original]

    key: str
    for key in list(verb_dict.keys()):
        prefixed_key: str = f"{action_prefix}{key}"
        verb_dict[prefixed_key] = verb_dict[key]

    return verb_dict


class SNES_Hotkeys_GP_Actionset(Gamepad_Actionset):
    name: ClassVar[str] = 'SNES Hotkeys (Gamepad)'

    key_dict: ClassVar[dict[str, str]] = {
        'savegame': 'rt',
        'loadgame': 'lt',
    }

    def __init__(self, doc_url: str = "", **kwargs):
        super().__init__(doc_url=doc_url, **kwargs)
        self.verb_dict = _build_verb_dict_2(self.action_prefix)


def _build_verb_dict_2(action_prefix: str) -> dict[str, list[VerbParamDict]]:
    verb_param: Partial_VerbParamDict = partial_create_verb_params(
        duration=100,
        delay=0,
        min_time=1,
        max_time=100,
        input_type=INPUT_TYPE.PRESS_KEY
    )

    verb_dict: dict[str, list[VerbParamDict]] = {
        'savegame': [verb_param(key='savegame')],
        'loadgame': [verb_param(key='loadgame')],
    }

    key: str
    for key in list(verb_dict.keys()):
        prefixed_key: str = f"{action_prefix}{key}"
        verb_dict[prefixed_key] = verb_dict[key]

    return verb_dict


_EXPORT_CLASSES_: list[type[Actionset]] = [
    SNES_GP_Actionset,
    SNES_Hotkeys_GP_Actionset,
]