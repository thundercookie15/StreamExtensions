from typing import Any, ClassVar

from streamchatwars._shared.constants import INPUT_TYPE
from streamchatwars._shared.types import Partial_VerbParamDict, VerbParamDict
from streamchatwars.actionsets.actionset import Actionset
from streamchatwars.actionsets.subclasses.base_multikey import partial_create_verb_params
from streamchatwars.actionsets.subclasses.gamepad import Gamepad_Actionset


class DesertBus_GP_Actionset(Gamepad_Actionset):
    '''
    Gamepad-based Actionset that implements the controls for the game
    `Desert Bus`
    '''
    # Class variables:
    name: ClassVar[str] = 'Desert Bus (Gamepad)'
    # ----------------------------------------------------------------------------

    '''
    Desert Bus Controls (XInput):
  
    Action      | Player       |
    ------------| ------------ |
    Accelerate  | RT           |
    Left        | Left Stick L |
    Right       | Left Stick R |
    '''

    key_dict: ClassVar[dict[str, str]] = {
        'drive': 'rt',
        'left': 'ls_left',
        'right': 'ls_right',
    }

    # ----------------------------------------------------------------------------

    def __init__(
            self,
            doc_url: str = "",
            **kwargs: Any
    ) -> None:
        '''
        Gamepad-based Actionset that implements the controls for the game
        `Desert Bus`
        '''
        super().__init__(
            doc_url=doc_url, **kwargs
        )
        self.verb_dict = _build_verb_dict(self.action_prefix)


def _build_verb_dict(action_prefix: str) -> dict[str, list[VerbParamDict]]:
    verb_param: Partial_VerbParamDict = partial_create_verb_params(
        duration=100,
        delay=0,
        min_time=1,
        max_time=250,
        input_type=INPUT_TYPE.PRESS_KEY
    )

    verb_dict: dict[str, list[VerbParamDict]] = {
        'd': [verb_param('drive')],
        'l': [verb_param('left')],
        'r': [verb_param('right')],
    }

    key: str

    for key in list(verb_dict.keys()):
        prefixed_key: str = f'{action_prefix}{key}'
        verb_dict[prefixed_key] = verb_dict[key]

    return verb_dict


_EXPORT_CLASSES_: list[type[Actionset]] = [
    DesertBus_GP_Actionset,
]
