from typing import Union
from core_game.game_event.activation_conditions.schemas import *

ActivationConditionsUnion = Union[
    AreaEntryConditionModel,
    EventCompletionConditionModel,
    ImmediateActivationModel,
    CharacterInteractionOptionModel
]

ActivationConditionsNPCConversation = Union[
    AreaEntryConditionModel,
    EventCompletionConditionModel,
    ImmediateActivationModel,
    CharacterInteractionOptionModel
]

ActivationConditionsPlayerConversation = Union[
    AreaEntryConditionModel,
    EventCompletionConditionModel,
    ImmediateActivationModel,
    CharacterInteractionOptionModel
]

ActivationConditionsCutscene = Union[
    AreaEntryConditionModel,
    EventCompletionConditionModel,
    ImmediateActivationModel,
    CharacterInteractionOptionModel
]

ActivationConditionsNarrator = Union[
    AreaEntryConditionModel,
    EventCompletionConditionModel,
    ImmediateActivationModel,
]
