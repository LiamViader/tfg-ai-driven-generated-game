from enum import Enum

class AgentName(str, Enum):
    """
    Canonical names for all specialized agents in the system.
    Using an Enum prevents typos and provides a single source of truth.
    """
    NARRATIVE = "NarrativeAgent"
    MAP = "MapAgent"
    CHARACTERS = "CharactersAgent" 
    RELATIONSHIP = "RelationshipAgent"