from core_game.game_state.singleton import GameStateSingleton
from simulated.singleton import SimulatedGameStateSingleton
from versioning.deltas.checkpoints.changeset import ChangesetCheckpoint
from versioning.deltas.detectors.changeset.root import ChangesetDetector
from versioning.deltas.detectors.changeset.characters.collection import CharactersDetector
from versioning.deltas.detectors.changeset.characters.entity import CharacterDetector
from versioning.deltas.detectors.changeset.map.collection import MapDetector
from versioning.deltas.detectors.changeset.map.entity import ScenarioDetector
from core_game.map.schemas import GameMapModel
from core_game.character.schemas import CharactersModel
from core_game.game_event.schemas import GameEventsManagerModel
from fastapi import HTTPException

def get_full_game_state():
    cp_manager = SimulatedGameStateSingleton.get_checkpoint_manager()

    current_cp_id = cp_manager.create_checkpoint(
        ChangesetCheckpoint,
    )

    changeset = cp_manager.generate_changeset(from_id=current_cp_id)

    return {
        "checkpoint_id": current_cp_id,
        "changes": changeset.get("changes") if changeset else {}
    }


def get_incremental_changes(from_checkpoint_id: str):
    cp_manager = SimulatedGameStateSingleton.get_checkpoint_manager()
    
    try:
        cp_manager.get_checkpoint(from_checkpoint_id)
    except RuntimeError:
        raise HTTPException(
            status_code=404,
            detail=f"Checkpoint '{from_checkpoint_id}' not found"
        )
    
    try:
        changeset = cp_manager.generate_changeset(from_id=from_checkpoint_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate changeset: {str(e)}"
        )
    
    new_checkpoint_id = cp_manager.create_checkpoint(ChangesetCheckpoint)

    cp_manager.delete_checkpoint(from_checkpoint_id)

    return {
        "checkpoint_id": new_checkpoint_id,
        "changes": changeset or {}
    }