import os
import sys
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulated.game_state import SimulatedGameState, SimulatedGameStateSingleton
from core_game.game.singleton import GameStateSingleton

def print_scenarios(state: SimulatedGameState, label: str):
    print(f"\n--- {label} ---")
    count = state.get_scenario_count()
    print(f"Scenario count: {count}")
    print(state.get_summary_list())
    print("--------------------------")

def random_scenario_name():
    return "TestScenario_" + str(uuid.uuid4())[:8]

def run_manual_simulation_test():
    # Reset and get a fresh simulated state
    SimulatedGameStateSingleton.reset_instance()
    state = SimulatedGameStateSingleton.get_instance()

    # --- BASE MODIFICATION (no layers yet) ---
    print(">>> [BASE] Creating scenario before any layers are created (direct modification of domain copy)")
    scenario1 = state.create_scenario(
        name=random_scenario_name(),
        summary_description="A simple place",
        visual_description="Looks calm and empty.",
        narrative_context="Opening area",
        indoor_or_outdoor="indoor",
        type="start",
        zone="zoneA"
    )
    print_scenarios(state, "[BASE] After creating scenario 1")
    print("[BASE] Domain map scenarios:", GameStateSingleton.get_instance().game_map._scenarios)

    # --- LAYER 1 ---
    state.begin_layer()
    print(">>> [LAYER 1] Layer created")

    scenario1 = state.create_scenario(
        name=random_scenario_name(),
        summary_description="A second place",
        visual_description="Also calm and indoors.",
        narrative_context="Continuation",
        indoor_or_outdoor="indoor",
        type="secondary",
        zone="zoneA"
    )
    print_scenarios(state, "[LAYER 1] After creating scenario 1")

    # --- LAYER 2 ---
    state.begin_layer()
    print(">>> [LAYER 2] Layer created")

    scenario2 = state.create_scenario(
        name=random_scenario_name(),
        summary_description="A third place",
        visual_description="Bright and open.",
        narrative_context="Outdoor step",
        indoor_or_outdoor="outdoor",
        type="transition",
        zone="zoneB"
    )
    print_scenarios(state, "[LAYER 2] After creating scenario 2")

    # --- ROLLBACK LAYER 2 ---
    print(">>> [LAYER 2] Rolling back")
    state.rollback()
    print_scenarios(state, "[LAYER 1] After rollback of Layer 2")

    # --- CONTINUE IN LAYER 1 ---
    scenario3 = state.create_scenario(
        name=random_scenario_name(),
        summary_description="Replacement scenario",
        visual_description="Shadowy and strange.",
        narrative_context="New mid area",
        indoor_or_outdoor="indoor",
        type="alternate",
        zone="zoneC"
    )
    print_scenarios(state, "[LAYER 1] After creating scenario 3")
    print("[BASE] Domain map (unchanged):", GameStateSingleton.get_instance().game_map._scenarios)

    # --- COMMIT LAYER 1 ---
    print(">>> [LAYER 1] Committing changes to base/domain")
    state.commit()
    print_scenarios(state, "[BASE] After committing LAYER 1")
    print("[BASE] Domain map (updated):", GameStateSingleton.get_instance().game_map._scenarios)

    # --- NEW LAYER 1 ---
    state.begin_layer()
    print(">>> [LAYER 1] New simulation layer created")

    scenario4 = state.create_scenario(
        name=random_scenario_name(),
        summary_description="Desert zone",
        visual_description="Hot and dry.",
        narrative_context="Outskirts",
        indoor_or_outdoor="outdoor",
        type="exploration",
        zone="zoneD"
    )
    print_scenarios(state, "[LAYER 1] After creating scenario 4")

    # --- NEW LAYER 2 ---
    state.begin_layer()
    print(">>> [LAYER 2] Nested simulation layer created")

    scenario5 = state.create_scenario(
        name=random_scenario_name(),
        summary_description="Mountain area",
        visual_description="Rocky and elevated.",
        narrative_context="Path to peak",
        indoor_or_outdoor="outdoor",
        type="path",
        zone="zoneE"
    )
    print_scenarios(state, "[LAYER 2] After creating scenario 5")

    # --- NEW LAYER 3 ---
    state.begin_layer()
    print(">>> [LAYER 3] Deepest simulation layer created")

    scenario6 = state.create_scenario(
        name=random_scenario_name(),
        summary_description="Final encounter",
        visual_description="Ruins and silence.",
        narrative_context="Climax area",
        indoor_or_outdoor="indoor",
        type="final",
        zone="zoneF"
    )
    print_scenarios(state, "[LAYER 3] After creating scenario 6")

    # --- COMMIT LAYER 3 ---
    print(">>> [LAYER 3] Committing to Layer 2")
    state.commit()
    print_scenarios(state, "[LAYER 2] After commit of Layer 3")

    # --- ROLLBACK LAYER 2 ---
    print(">>> [LAYER 2] Rolling back")
    state.rollback()
    print_scenarios(state, "[LAYER 1] After rollback of Layer 2")

    # --- FINAL ROLLBACK TO BASE ---
    print(">>> [LAYER 1] Rolling back to base/domain")
    state.rollback()
    print_scenarios(state, "[BASE] Final state after rollback chain")

    print("[BASE] Final domain map state:", GameStateSingleton.get_instance().game_map._scenarios)

if __name__ == "__main__":
    run_manual_simulation_test()
