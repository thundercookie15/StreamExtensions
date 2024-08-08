from collections.abc import Sequence
from typing import ClassVar, Any

from .base_multikey import partial_create_verb_params
from .gamepad import Gamepad_Actionset
from ..actionset import Actionset
from ..._shared.constants import INPUT_TYPE
from ..._shared.types import Partial_VerbParamDict, VerbParamDict


class GTA_GP_Actionset(Gamepad_Actionset):
    '''
    Gamepad-based Actionset that implements the controls for the game
    `Grand Theft Auto V`
    '''
    # Class variables:
    name: ClassVar[str] = 'Grand Theft Auto V (Gamepad)'
    # ----------------------------------------------------------------------------

    '''
    GTA V Controls (XInput):
    
    Action      | Default Layout |
    ------------|----------------|
    Drive       | {Right Trigger}|
    Reverse     | {Left Trigger} |
    Brake       | {Right Bumper} |
    Left        | {Left Stick L} |
    Right       | {Left Stick R} |
    Horn        | {Left Stick}   |
    '''

    key_dict: ClassVar[dict[str, Sequence[str]]] = {
        'drive': 'rt',
        'reverse': 'lt',
        'brake': 'rb',
        'left': 'ls_left',
        'right': 'ls_right',
        'horn': 'ls',
    }

    # ----------------------------------------------------------------------------

    def __init__(
            self,
            doc_url: str = "",
            **kwargs: Any
    ) -> None:
        '''
        Gamepad-based Actionset that implements the controls for the game
        `Grand Theft Auto V`
        '''
        super().__init__(
            doc_url=doc_url, **kwargs
        )
        self.verb_dict = _build_verb_dict(self.action_prefix)


def _build_verb_dict(action_prefix: str) -> dict[str, list[VerbParamDict]]:
    '''
    Helper function to build the dictionary of verbs usable in chat.
    '''
    # partial function to build the verb dict
    verb_param: Partial_VerbParamDict = partial_create_verb_params(
        duration=50,
        delay=0,
        min_time=1,
        max_time=1000,
        input_type=INPUT_TYPE.PRESS_KEY
    )

    verb_dict: dict[str, list[VerbParamDict]] = {
        'drive': [verb_param(key='drive', duration=250)],
        'reverse': [verb_param(key='reverse', duration=250)],
        'brake': [verb_param(key='brake', duration=150)],
        'left': [verb_param(key='left', duration=200)],
        'right': [verb_param(key='right', duration=200)],
        'horn': [verb_param(key='horn', duration=100)],
    }

    key: str

    for key in list(verb_dict.keys()):
        prefixed_key: str = f'{action_prefix}{key}'
        verb_dict[prefixed_key] = verb_dict[key]

    return verb_dict


_EXPORT_CLASSES_: list[type[Actionset]] = [
    GTA_GP_Actionset
]
