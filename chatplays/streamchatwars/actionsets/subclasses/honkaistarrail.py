from typing import ClassVar, Any, Sequence

from .base_multikey import partial_create_verb_params
from .gamepad import Gamepad_Actionset
from .keyboard import Keyboard_Actionset
from ..actionset import Actionset
from ..._shared.constants import INPUT_TYPE
from ..._shared.types import VerbParamDict, Partial_VerbParamDict


class HSR_GP_Actionset(Gamepad_Actionset):
    '''
    Gamepad-based Actionset that implements the controls for the game
    `Honkai Star Rail`
    '''
    # Class variables:
    name: ClassVar[str] = 'Honkai Star Rail (Gamepad)'
    # ----------------------------------------------------------------------------

    '''
    HSR Controls (XInput):
    
    Action      | Default Layout |
    ------------|----------------|
    Swap Basic  | {X}            |
    Skill       | {Y}            |
    Cast Ability| {A}            |
    Target Right| {RT}           |
    Target Left | {LT}           |
    B Button    | {B}            |
    '''

    key_dict: ClassVar[dict[str, str]] = {
        'swap_basic': 'x',
        'swap_skill': 'y',
        'cast': 'a',
        'target_left': 'lt',
        'target_right': 'rt',
    },

    # ----------------------------------------------------------------------------

    def __init__(
            self,
            doc_url: str = "",
            **kwargs: Any
    ) -> None:
        '''
        Gamepad-based Actionset that implements the controls for the game
        `Honkai Star Rail`
        '''
        super().__init__(doc_url=doc_url, **kwargs)
        self.verb_dict = _build_verb_dict(self.action_prefix)


def _build_verb_dict(action_prefix: str) -> dict[str, list[VerbParamDict]]:
    '''
    Build the dictionary of verbs for this actionset.
    '''
    verb_param: Partial_VerbParamDict = partial_create_verb_params(
        duration=50,
        delay=0,
        min_time=1,
        max_time=100,
        input_type=INPUT_TYPE.PRESS_KEY
    )

    verb_dict: dict[str, list[VerbParamDict]] = {
        'cast': [verb_param(key='cast', duration=50)],
        'swap_basic': [verb_param(key='swap_basic', duration=50)],
        'swap_skill': [verb_param(key='swap_skill', duration=50)],
        'target_right': [verb_param(key='target_right', duration=50)],
    }

    key: str

    for key in list(verb_dict.keys()):
        prefixed_key: str = f'{action_prefix}{key}'
        verb_dict[prefixed_key] = verb_dict[key]

    return verb_dict


class HSR_KB_Actionset(Keyboard_Actionset):
    name: ClassVar[str] = 'Honkai Star Rail (Keyboard)'

    key_dict: ClassVar[dict[str, Sequence[str]]] = {
        'cast': ('space',),
        'swap_basic': ('q',),
        'swap_skill': ('e',),
        'target_left': ('a',),
        'target_right': ('d',),
        'select_ult1': ('1',),
        'select_ult2': ('2', '2'),
        'select_ult3': ('3', '3'),
        'select_ult4': ('4', '4'),
    }

    def __init__(
            self,
            doc_url: str = "",
            **kwargs: Any
    ) -> None:
        '''
        Gamepad-based Actionset that implements the controls for the game
        `Honkai Star Rail`
        '''
        super().__init__(doc_url=doc_url, **kwargs)
        self.verb_dict = _build_verb_dict(self.action_prefix)

    def _build_verb_dict(action_prefix: str) -> dict[str, list[VerbParamDict]]:
        '''
        Build the dictionary of verbs for this actionset.
        '''
        verb_param: Partial_VerbParamDict = partial_create_verb_params(
            duration=50,
            delay=0,
            min_time=1,
            max_time=1000,
            input_type=INPUT_TYPE.PRESS_KEY
        )

        verb_dict: dict[str, list[VerbParamDict]] = {
            'cast': [verb_param(key='cast', duration=250)],
            'swap_basic': [verb_param(key='swap_basic', duration=250)],
            'swap_skill': [verb_param(key='swap_skill', duration=250)],
            'target_right': [verb_param(key='target_right', duration=250)],
            'target_left': [verb_param(key='target_left', duration=250)],
        }

        key: str

        for key in list(verb_dict.keys()):
            prefixed_key: str = f'{action_prefix}{key}'
            verb_dict[prefixed_key] = verb_dict[key]

        return verb_dict


_EXPORT_CLASSES_: list[type[Actionset]] = [
    HSR_GP_Actionset,
    HSR_KB_Actionset
]
