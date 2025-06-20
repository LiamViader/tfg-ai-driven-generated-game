from copy import deepcopy
from typing import Optional, Dict, Set

from core_game.character.domain import Characters, BaseCharacter
from core_game.character.schemas import (
    IdentityModel,
    PhysicalAttributesModel,
    PsychologicalAttributesModel,
    NarrativeWeightModel,
    KnowledgeModel,
    DynamicStateModel,
)


class SimulatedCharacters:
    """Lightweight wrapper around :class:`Characters` for isolated modifications."""

    def __init__(self, characters: Characters) -> None:
        self._original_state: Characters = characters
        self._copied_state: Optional[Characters] = None
        self._working_state: Characters = self._original_state
        self.is_modified: bool = False
        self._deleted: Dict[str, BaseCharacter] = {}
        self._added: Set[str] = set()

    @property
    def working_state(self) -> Characters:
        return self._working_state

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _started_modifying(self) -> None:
        if not self.is_modified:
            self._copied_state = Characters(self._original_state.to_model())
            self._working_state = self._copied_state
            self.is_modified = True

    # ------------------------------------------------------------------
    # Proxy methods
    # ------------------------------------------------------------------

    def create_npc(self, *args, **kwargs) -> str:
        self._started_modifying()
        npc = self.working_state.create_npc(*args, **kwargs)
        self._added.add(npc.id)
        return npc.id

    def create_player(self, *args, **kwargs) -> str:
        self._started_modifying()
        player = self.working_state.create_player(*args, **kwargs)
        self._added.add(player.id)
        return player.id

    def delete_character(self, character_id: str) -> bool:
        self._started_modifying()
        char = self.working_state.find_character(character_id)
        if not char:
            return False
        if self.working_state.delete_character(character_id):
            if character_id not in self._added:
                self._deleted[character_id] = char
            return True
        return False

    def place_character(self, *args, **kwargs) -> bool:
        self._started_modifying()
        return self.working_state.place_character(*args, **kwargs)

    def remove_character_from_scenario(self, *args, **kwargs) -> bool:
        self._started_modifying()
        return self.working_state.remove_character_from_scenario(*args, **kwargs)

    def modify_identity(self, *args, **kwargs) -> bool:
        self._started_modifying()
        return self.working_state.modify_identity(*args, **kwargs)

    def modify_physical(self, *args, **kwargs) -> bool:
        self._started_modifying()
        return self.working_state.modify_physical(*args, **kwargs)

    def modify_psychological(self, *args, **kwargs) -> bool:
        self._started_modifying()
        return self.working_state.modify_psychological(*args, **kwargs)

    def modify_knowledge(self, *args, **kwargs) -> bool:
        self._started_modifying()
        return self.working_state.modify_knowledge(*args, **kwargs)

    def modify_dynamic_state(self, *args, **kwargs) -> bool:
        self._started_modifying()
        return self.working_state.modify_dynamic_state(*args, **kwargs)

    def modify_narrative(self, *args, **kwargs) -> bool:
        self._started_modifying()
        return self.working_state.modify_narrative(*args, **kwargs)

    # query helpers
    def get_character(self, cid: str) -> Optional[BaseCharacter]:
        return self.working_state.find_character(cid)

    def get_count(self) -> int:
        return len(self.working_state._registry)
