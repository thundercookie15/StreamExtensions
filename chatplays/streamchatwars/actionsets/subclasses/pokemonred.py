from collections.abc import Sequence
from typing import ClassVar

from streamchatwars._shared.constants import INPUT_TYPE
from streamchatwars._shared.types import VerbParamDict, Partial_VerbParamDict
from streamchatwars.actionsets.actionset import Actionset
from streamchatwars.actionsets.subclasses.base_multikey import partial_create_verb_params
from streamchatwars.actionsets.subclasses.gamepad import Gamepad_Actionset
from streamchatwars.actionsets.subclasses.keyboard import Keyboard_Actionset


class PokemonFireRed_KB_Actionset(Keyboard_Actionset):
    name: ClassVar[str] = 'Pokemon Fire Red (Keyboard)'

    '''
    Pokemon Fire Red Controls (Keyboard):
    
    Action      | Player       |
    ------------| ------------ |
    Up          | {Up Arrow}   |
    Down        | {Down Arrow} |
    Left        | {Left Arrow} |
    Right       | {Right Arrow}|
    A           | Z            |
    B           | X            |
    Start       | Enter        |
    Select      | Backspace    |
    '''

    key_dict: ClassVar[dict[str, Sequence[str]]] = {
        'up': ('up', 'up'),
        'down': ('down', 'down'),
        'left': ('left', 'left'),
        'right': ('right', 'right'),
        'a': ('z', 'z'),
        'b': ('x', 'x'),
        'start': ('enter', 'enter'),
        'select': ('backspace', 'backspace'),
        'save': ('f13', 'f13'),
    }

    def __init__(self, doc_url: str = "", **kwargs):
        super().__init__(doc_url=doc_url, **kwargs)
        self.verb_dict = _build_verb_dict(self.action_prefix)


class PokemonFireRed_GP_Actionset(Gamepad_Actionset):
    name: ClassVar[str] = 'Pokemon Fire Red (Gamepad)'

    '''
    Pokemon Fire Red Controls (XInput):
    
    Action      | Player       |
    ------------| ------------ |
    Up          | Dpad Up      |
    Down        | Dpad Down    |
    Left        | Dpad Left    |
    Right       | Dpad Right   |
    A           | A            |
    B           | B            |
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
        'start': 'start',
        'select': 'back',
        'save': 'x',
    }

    def __init__(self, doc_url: str = "", **kwargs):
        super().__init__(doc_url=doc_url, **kwargs)
        self.verb_dict = _build_verb_dict(self.action_prefix)


def _build_verb_dict(action_prefix: str) -> dict[str, list[VerbParamDict]]:
    verb_param: Partial_VerbParamDict = partial_create_verb_params(
        duration=100,
        delay=0,
        min_time=1,
        max_time=100,
        input_type=INPUT_TYPE.PRESS_KEY
    )

    verb_dict: dict[str, list[VerbParamDict]] = {
        'up': [verb_param(key='up')],
        'down': [verb_param(key='down')],
        'left': [verb_param(key='left')],
        'right': [verb_param(key='right')],
        'a': [verb_param(key='a')],
        'b': [verb_param(key='b')],
        'start': [verb_param(key='start')],
        'select': [verb_param(key='select')],
        'savegame': [verb_param(key='save')],
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


_EXPORT_CLASSES_: list[type[Actionset]] = [
    PokemonFireRed_GP_Actionset,
    PokemonFireRed_KB_Actionset
]
