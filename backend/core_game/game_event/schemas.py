"""Data models for describing game events and in-game messages."""

from typing import List, Optional, Literal, Union
from pydantic import BaseModel, Field


class GameEventModel(BaseModel):
    """Base class for all game events."""
    id: str = Field(..., description="Unique identifier of the game event.")


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
        "npc_conversation", description="Type discriminator for this event."
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
        "player_npc_conversation",
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
        "narrator_intervention", description="Type discriminator for this event."
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
        "cutscene", description="Type discriminator for this event."
    )
    frames: List[CutsceneFrameModel] = Field(
        default_factory=list,
        description="Ordered sequence of frames composing the cutscene.",
    )
