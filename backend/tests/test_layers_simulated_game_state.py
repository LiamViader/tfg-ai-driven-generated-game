import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulated.game_state import SimulatedGameState, SimulatedGameStateSingleton
from core_game.game.singleton import GameStateSingleton
import uuid

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

    print("Create scenario before creating a layer")

    scenario1 = state.create_scenario(
        name=random_scenario_name(),
        summary_description="A simple place",
        visual_description="Looks calm and empty.",
        narrative_context="Opening area",
        indoor_or_outdoor="indoor",
        type="start",
        zone="zoneA"
    )
    print_scenarios(state, "Scenarios after creating scenario 1")
    print(GameStateSingleton.get_instance().game_map._scenarios)
    
    # --- Layer 1 () ---
    state.begin_layer()
    print(">>> [LAYER 1] Layer 1 created")

    scenario1 = state.create_scenario(
        name=random_scenario_name(),
        summary_description="A simple place",
        visual_description="Looks calm and empty.",
        narrative_context="Opening area",
        indoor_or_outdoor="indoor",
        type="start",
        zone="zoneA"
    )
    print_scenarios(state, "[LAYER 1] After creating scenario 1")

    # --- Layer 2 ---
    state.begin_layer()
    print(">>> [LAYER 2] Started")

    scenario2 = state.create_scenario(
        name=random_scenario_name(),
        summary_description="A second scenario",
        visual_description="Brighter and larger.",
        narrative_context="Mid area",
        indoor_or_outdoor="indoor",
        type="mid",
        zone="zoneB"
    )
    print_scenarios(state, "[LAYER 2] After creating scenario 2")

    # --- Rollback Layer 2 ---
    print(">>> [LAYER 2] Rollback")
    state.rollback()
    print_scenarios(state, "[LAYER 1] After rollback of LAYER 2")

    # --- Continue in Layer 1 (still active) ---
    scenario3 = state.create_scenario(
        name=random_scenario_name(),
        summary_description="A replacement for 2",
        visual_description="Shadowy and strange.",
        narrative_context="New mid area",
        indoor_or_outdoor="indoor",
        type="alternate",
        zone="zoneC"
    )
    print_scenarios(state, "[LAYER 1] After creating scenario 3")
    print(GameStateSingleton.get_instance().game_map._scenarios)

    # --- Commit Layer 1 ---
    print(">>> [LAYER 1] Commit to domain")
    state.commit()
    print_scenarios(state, "[BASE] After committing LAYER 1 (now in domain)")

    print(GameStateSingleton.get_instance().game_map._scenarios)

    # --- Begin New Simulation Layer  ---
    state.begin_layer()
    print(">>> [NEW LAYER 1] Begin")

    scenario4 = state.create_scenario(
        name=random_scenario_name(),
        summary_description="A fourth scenario",
        visual_description="Deserted and dry.",
        narrative_context="Desert zone",
        indoor_or_outdoor="outdoor",
        type="optional",
        zone="zoneD"
    )
    print_scenarios(state, "[NEW LAYER 1] After creating scenario 4")

    # --- Layer 2 ---
    state.begin_layer()
    print(">>> [NEW LAYER 2] Started")

    scenario5 = state.create_scenario(
        name=random_scenario_name(),
        summary_description="Another scenario",
        visual_description="Mountainous terrain.",
        narrative_context="Mountain path",
        indoor_or_outdoor="outdoor",
        type="path",
        zone="zoneE"
    )
    print_scenarios(state, "[NEW LAYER 2] After creating scenario 5")

    # --- Layer 3 ---
    state.begin_layer()
    print(">>> [NEW LAYER 3] Started")

    scenario6 = state.create_scenario(
        name=random_scenario_name(),
        summary_description="Final scenario in chain",
        visual_description="Abandoned city ruins.",
        narrative_context="Climax",
        indoor_or_outdoor="indoor",
        type="end",
        zone="zoneF"
    )
    print_scenarios(state, "[NEW LAYER 3] After creating scenario 6")

    # --- Commit Layer 3 ---
    print(">>> [NEW LAYER 3] Commit to Layer 2")
    state.commit()
    print_scenarios(state, "[AFTER COMMIT 3->2]")

    # --- Rollback Layer 2 ---
    print(">>> [NEW LAYER 2] Rollback")
    state.rollback()
    print_scenarios(state, "[AFTER ROLLBACK TO LAYER 1]")

    # --- Rollback Final Layer (Back to Base) ---
    print(">>> [NEW LAYER 1] Rollback (to domain/base)")
    state.rollback()
    print_scenarios(state, "[BASE] Final state after full rollback")

    print(GameStateSingleton.get_instance().game_map._scenarios)
if __name__ == "__main__":
    run_manual_simulation_test()
