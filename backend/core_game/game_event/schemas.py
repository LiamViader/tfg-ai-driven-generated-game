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
    status: EVENT_STATUS_LITERAL = Field(
        "AVAILABLE",
        description="The current lifecycle state of the event. If 'DISABLED', activation conditions will not trigger it.",
    )

    activation_conditions: List[ActivationConditionModel] = Field(
        default_factory=list,
        description="The specific condition/s that activates this event. Its structure depends on its 'type'."
    )

    source_beat_id: Optional[str] = Field(..., description="The ID of the Narrative Beat that originated this game event. None if it was not originated by a narrative beat")
    outcome_summary: Optional[str] = Field(
        default=None, 
        description="A summary of the event's final outcome, generated upon its completion. This field is ONLY populated when the event's status moves to 'COMPLETED'. It remains none for all other statuses."
    )

# ---------- Message Schemas ----------


class CharacterDialogueMessage(BaseModel):
    """A message representing spoken words from any character (NPC or Player)."""
    type: Literal["dialogue"] = Field(default="dialogue", description="Identifies this as a dialogue message.")
    actor_id: str = Field(..., description="The ID of the character speaking.")
    content: str = Field(..., description="The text of the dialogue.")

class CharacterActionMessage(BaseModel):
    """A message representing a physical action performed by any character."""
    type: Literal["action"] = Field(default="action", description="Identifies this as an action message.")
    actor_id: str = Field(..., description="The ID of the character performing the action.")
    content: str = Field(..., description="A description of the action.")

class PlayerThoughtMessage(BaseModel):
    """A message representing the player's internal monologue."""
    type: Literal["thought"] = Field(default="thought", description="Identifies this as a player thought.")
    actor_id: str = Field("player", description="The speaker is always the player.")
    content: str = Field(..., description="The text of the internal thought.")

class PlayerChoiceOptionModel(BaseModel):
    """Defines a single option within a player choice block."""
    type: Literal["Dialogue", "Action"]
    label: str = Field(..., description="The short, descriptive text for the choice.")

class PlayerChoiceMessage(BaseModel):
    """A message representing a set of choices presented to the player."""
    type: Literal["player_choice"] = Field(default="player_choice", description="Identifies this as a player choice block.")
    actor_id: str = Field("player", description="Choices are always presented for the player.")
    title: str = Field(..., description="The question or title for the choice block (e.g., 'What do you do?').")
    options: List[PlayerChoiceOptionModel] = Field(..., description="A list of the available choices.")

class NarratorMessage(BaseModel):
    """A message representing a description or observation from the narrator."""
    type: Literal["narrator"] = Field(default="narrator", description="Identifies this as a narrator message.")
    actor_id: str = Field("narrator", description="The speaker is always the narrator.")
    content: str = Field(..., description="The text of the narration.")

# --- Union Type for Conversations ---

# This Union type represents any possible message that can be part of a conversation log.
ConversationMessage = Union[
    CharacterDialogueMessage,
    CharacterActionMessage,
    PlayerThoughtMessage,
    PlayerChoiceMessage,
    NarratorMessage
]

NPCMessage = Union[
    CharacterActionMessage,
    CharacterActionMessage,
    NarratorMessage
]



# ---------- Event Schemas ----------
class NPCConversationEventModel(GameEventModel):
    """Conversation between several NPCs."""
    type: Literal["npc_conversation"] = Field(
        default="npc_conversation", description="Type discriminator for this event."
    )
    npc_ids: List[str] = Field(
        ..., description="IDs of the NPCs participating in the conversation."
    )
    messages: List[ConversationMessage] = Field(
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
    messages: List[ConversationMessage] = Field(
        default_factory=list,
        description="Ordered list of messages and actions.",
    )


class NarratorInterventionEventModel(GameEventModel):
    """Event containing narration addressed to the player or scene observations."""
    type: Literal["narrator_intervention"] = Field(
        default="narrator_intervention", description="Type discriminator for this event."
    )
    messages: List[ConversationMessage] = Field(
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
    involved_character_ids: List[str] = Field(default_factory=list, description="A list of character IDs who are present or relevant in the cutscene. This provides context for generating visuals. Player id can be here too")
    involved_scenario_ids: List[str] = Field(default_factory=list, description="A list of scenario IDs for scenarios relevant in the cutscene. This provides context for the setting's visuals.")

class RunningEventInfo(BaseModel):
    """Stores information about a single event on the running stack."""
    event_id: str
    activating_condition_id: Optional[str] = None

class GameEventsManagerModel(BaseModel):
    """Stores game events and related info"""
    all_events: Dict[str, GameEventModel] = Field(default_factory=dict, description="Stores all existing events, keyed by id")

    running_event_stack: List[RunningEventInfo] = Field(
        default_factory=list,
        description="Stack of running events, top is the one running currently"
    )