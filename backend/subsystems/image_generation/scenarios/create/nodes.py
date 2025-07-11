import asyncio
from typing import List, cast

from .schemas import GraphState
from .scenario_processor.schemas import ScenarioProcessorState
from .scenario_processor.orchestrator import get_scenario_processor_graph_app


async def process_all_scenarios_node(state: GraphState) -> dict:
    """
    This node invokes the 'scenario_processor_graph' subgraph in parallel
    for each of the scenarios provided in the initial state.
    """
    print("--- 🚀 Starting to process all scenarios in parallel ---")

    # Get the subgraph application once
    scenario_processor_app = get_scenario_processor_graph_app()

    tasks = [
        scenario_processor_app.ainvoke(
            ScenarioProcessorState(
                scenario=scenario,
                graphic_style=state.graphic_style,
                general_game_context=state.general_game_context,
                image_api_url=state.image_api_url
            )
        )
        for scenario in state.scenarios
    ]

    # The result data will be a list of dictionaries
    results_data = await asyncio.gather(*tasks)

    print("--- ✅ Finished processing. Classifying results... ---")

    successful_scenarios = []
    failed_scenarios = []

    # We iterate over the result data
    for result_dict in results_data:
        # We convert the dictionary back to our Pydantic model
        scenario_result = ScenarioProcessorState(**result_dict)

        # Now we can safely access the fields
        if scenario_result.error is None and scenario_result.image_base64 is not None:
            successful_scenarios.append(scenario_result)
        else:
            failed_scenarios.append(scenario_result)
    
    print(f"  - Results: {len(successful_scenarios)} success(es), {len(failed_scenarios)} failure(s).")

    return {
        "successful_scenarios": successful_scenarios,
        "failed_scenarios": failed_scenarios
    }