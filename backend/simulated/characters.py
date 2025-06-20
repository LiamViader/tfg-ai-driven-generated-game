from copy import deepcopy
from typing import Optional, Dict, Set, Tuple

from simulated.game_state import SimulatedGameState
from core_game.character.domain import Characters, BaseCharacter, PlayerCharacter, NPCCharacter
from core_game.character.schemas import PlayerCharacterModel, rollback_character_id, NonPlayerCharacterModel
from core_game.character.schemas import (
    IdentityModel,
    PhysicalAttributesModel,
    PsychologicalAttributesModel,
    NarrativeWeightModel,
    KnowledgeModel,
    DynamicStateModel,
)
from core_game.map.domain import Scenario

class SimulatedCharacters:
    """Lightweight wrapper around :class:`Characters` for isolated modifications."""

    def __init__(self, characters: Characters, simulated_game_state: SimulatedGameState) -> None:
        self._original_state: Characters = characters
        self._copied_state: Optional[Characters] = None
        self._working_state: Characters = self._original_state
        self._simulated_game_state: SimulatedGameState = simulated_game_state
        self._is_modified: bool = False
        self._deleted_characters: Dict[str, BaseCharacter] = {}
        self._added_characters: Set[str] = set()
        self._modified_characters: Set[str] = set()

    @property
    def working_state(self) -> Characters:
        return self._working_state

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _started_modifying(self) -> None:
        if not self._is_modified:
            self._copied_state = Characters(self._original_state.to_model())
            self._working_state = self._copied_state
            self._is_modified = True

    # ------------------------------------------------------------------
    # Proxy methods
    # ------------------------------------------------------------------

    def create_npc(
        self, 
        identity: IdentityModel,
        physical: PhysicalAttributesModel,
        psychological: PsychologicalAttributesModel,
        narrative: NarrativeWeightModel,
        knowledge: KnowledgeModel,
        dynamic_state: DynamicStateModel = DynamicStateModel()
    ) -> NPCCharacter:
        
        self._started_modifying()

        knowledge = knowledge or KnowledgeModel()
        dynamic_state = dynamic_state or DynamicStateModel()

        npc_model = NonPlayerCharacterModel(
            identity=identity,
            physical=physical,
            psychological=psychological,
            knowledge=knowledge,
            present_in_scenario=None,
            dynamic_state=dynamic_state,
            narrative=narrative,
        )
        npc = NPCCharacter(npc_model)

        #aqui anirien comprovacions i en cas de fallada es faria rollback del id i es retornaria error.

        self._working_state.add_npc(npc)

        self._added_characters.add(npc.id)
        return npc

    def create_player(
        self,
        identity: IdentityModel,
        physical: PhysicalAttributesModel,
        psychological: PsychologicalAttributesModel,
        scenario_id: str,
        knowledge: Optional[KnowledgeModel] = KnowledgeModel()
    ) -> Tuple[PlayerCharacter, Scenario]:

        if self.working_state.has_player():
            raise ValueError("Player already exists")

        knowledge = knowledge or KnowledgeModel()

        player_model = PlayerCharacterModel(
            identity=identity,
            physical=physical,
            psychological=psychological,
            knowledge=knowledge,
            present_in_scenario=scenario_id
        )

        player = PlayerCharacter(player_model)

        success, message= self._simulated_game_state.simulated_map.can_place_player(player,scenario_id)
        if not success:
            rollback_character_id()
            raise ValueError(message)
        
        self._started_modifying()
        scenario = self._simulated_game_state.simulated_map.place_player(player,scenario_id)
        player = self.working_state.add_player(player)
        self._added_characters.add(player.id)

        return player, scenario

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

    def characters_count(self) -> int:
        return self.working_state.characters_count()
