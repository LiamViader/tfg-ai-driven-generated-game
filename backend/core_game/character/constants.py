from typing import Literal

# Centralized type aliases for commonly used Literal values
Gender = Literal["male", "female", "non-binary", "undefined", "other"]
CharacterType = Literal["player", "npc"]
NarrativeRole = Literal[
    "protagonist",
    "secondary",
    "extra",
    "antagonist",
    "ally",
    "informational figure",
]
NarrativeImportance = Literal["important", "secondary", "minor", "inactive"]
