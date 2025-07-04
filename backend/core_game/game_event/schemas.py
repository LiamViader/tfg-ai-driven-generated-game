"""Data models for describing game events and in-game messages."""

from typing import List, Optional, Literal, Union, Dict, Set
from pydantic import BaseModel, Field
from core_game.game_event.activation_conditions.schemas import ActivationConditionModel
from core_game.game_event.constants import EVENT_STATUS_LITERAL

_event_id_counter = 0

def generate_event_id() -> str:
    """Return a sequential id of the form 'event_001'."""
    global _event_id_counter
    _event_id_counter += 1
    return f"event_{_event_id_counter:03d}"

def rollback_event_id() -> None:
    global _event_id_counter
    _event_id_counter -= 1

class GameEventModel(BaseModel):
    """Base class for all game events."""
    id: str = Field(default_factory=generate_event_id, description="Unique identifier of the game event.")
    title: str = Field(
        ...,
        description="A short, descriptive title for the event (7-15 words). This acts as a human-readable headline. e.g., 'The King reveals the secret of the stolen artifact to the player'."
    )
    description: str = Field(
        ...,
        description="The detailed creative brief for this event, guiding the generation of its final content (dialogues, actions). The nature of this brief can be 'open' (e.g., 'Character X asks the player for their opinion on Y') or 'closed' and more prescriptive (e.g., 'The king tells his servant he hates his treatment' in a cutscene). You decide if it must be open or closed based on the narrative and the dependance of other beats and events. Up to 150 words max"
    )
    type: Literal[
        "npc_conversation",
        "player_npc_conversation",
        "narrator_intervention",
        "cutscene",
    ]
    status: EVENT_STATUS_LITERAL = Field("DRAFT", description="The current lifecycle state of the event.")

    activation_conditions: List[ActivationConditionModel] = Field(
        default_factory=list,
        description="The specific condition/s that activates this event. Its structure depends on its 'type'. When any trigger is set, the event moves from 'DRAFT' to 'AVAILABLE'."
    )

    source_beat_id: Optional[str] = Field(..., description="The ID of the Narrative Beat that originated this game event. None if it was not originated by a narrative beat")
    outcome_summary: Optional[str] = Field(
        default=None, 
        description="A summary of the event's final outcome, generated upon its completion. This field is ONLY populated when the event's status moves to 'COMPLETED'. It remains none for all other statuses."
    )

# ---------- Message Schemas ----------


class MessageBase(BaseModel):
    """Base fields shared by all messages."""

    content: str = Field(..., description="Text or description of the message.")


class SpokenMessage(MessageBase):
    """Dialogue line spoken by an actor."""

    type: Literal["spoken"] = Field("spoken", description="Spoken line of dialogue.")


class ActionMessage(MessageBase):
    """Descriptive action performed by an actor."""

    type: Literal["action"] = Field(
        "action", description="Descriptive action performed by the actor."
    )


class ObservationMessage(MessageBase):
    """Narrator observation not directly addressed to the player."""

    type: Literal["observation"] = Field(
        "observation", description="Narrator observation or description."
    )


class ActorMessageMixin(BaseModel):
    """Mixin for messages that include the sender's identifier."""

    actor_id: str = Field(..., description="ID of the actor sending the message.")


class NPCSpokenMessage(SpokenMessage, ActorMessageMixin):
    pass


class NPCActionMessage(ActionMessage, ActorMessageMixin):
    pass


NPCMessage = Union[NPCSpokenMessage, NPCActionMessage]


class PlayerSpokenMessage(SpokenMessage):
    pass


class PlayerActionMessage(ActionMessage):
    pass


PlayerMessage = Union[PlayerSpokenMessage, PlayerActionMessage]


class NarratorSpokenMessage(SpokenMessage):
    """Line the narrator directs straight to the player."""


class NarratorObservationMessage(ObservationMessage):
    """Narrator comment describing the scene without addressing the player."""


# Narrator messages can either address the player directly (spoken) or simply
# describe what happens in the scene (observation).
NarratorMessage = Union[NarratorSpokenMessage, NarratorObservationMessage]


# ---------- Event Schemas ----------
class NPCConversationEventModel(GameEventModel):
    """Conversation between several NPCs."""
    type: Literal["npc_conversation"] = Field(
        default="npc_conversation", description="Type discriminator for this event."
    )
    npc_ids: List[str] = Field(
        ..., description="IDs of the NPCs participating in the conversation."
    )
    messages: List[NPCMessage] = Field(
        default_factory=list,
        description="Ordered list of NPC messages and actions.",
    )


class PlayerNPCConversationEventModel(GameEventModel):
    """Conversation between the player and one or more NPCs."""
    type: Literal["player_npc_conversation"] = Field(
        default="player_npc_conversation",
        description="Type discriminator for this event.",
    )
    npc_ids: List[str] = Field(
        ..., description="IDs of the NPCs participating in the conversation."
    )
    messages: List[NPCMessage] = Field(
        default_factory=list,
        description="Ordered list of NPC messages and actions before player intervention.",
    )
    player_intervention_indices: List[int] = Field(
        default_factory=list,
        description=(
            "Indices in 'messages' after which the player is expected to respond or can intervene."
        ),
    )


class NarratorInterventionEventModel(GameEventModel):
    """Event containing narration addressed to the player or scene observations."""
    type: Literal["narrator_intervention"] = Field(
        default="narrator_intervention", description="Type discriminator for this event."
    )
    messages: List[NarratorMessage] = Field(
        default_factory=list,
        description=(
            "Ordered narration messages. Spoken entries address the player "
            "directly while observations simply describe the scene."
        ),
    )


class CutsceneFrameModel(BaseModel):
    """Single frame within a cutscene."""
    image_path: Optional[str] = Field(
        None, description="Path to the image shown during this frame."
    )
    narrator_messages: List[NarratorMessage] = Field(
        default_factory=list,
        description="Narrator lines for this frame.",
    )
    npc_messages: List[NPCMessage] = Field(
        default_factory=list,
        description="NPC dialogue or actions for this frame.",
    )


class CutsceneEventModel(GameEventModel):
    """Cinematic event composed of multiple frames."""
    type: Literal["cutscene"] = Field(
        default="cutscene", description="Type discriminator for this event."
    )
    frames: List[CutsceneFrameModel] = Field(
        default_factory=list,
        description="Ordered sequence of frames composing the cutscene.",
    )

class GameEventsManagerModel(BaseModel):
    """Stores game events and related info"""
    all_events: Dict[str, GameEventModel] = Field(default_factory=dict, description="Stores all existing events, keyed by id")
    events_by_beat_id: Dict[str, Set[str]] = Field(
        default_factory=dict,
        description="An index that maps a Narrative Beat ID to the set of Game Event IDs that were originated from it. Allows for quick lookups of all events that compose a beat."
    )
    
    beatless_event_ids: Set[str] = Field(
        default_factory=set,
        description="A set of IDs for game events that were not originated from any Narrative Beat (e.g., random events, direct player actions)."
    )

    running_event_stack: List[str] = Field(
        default_factory=list,
        description="Stack of running events, top is the one running currently"
    )