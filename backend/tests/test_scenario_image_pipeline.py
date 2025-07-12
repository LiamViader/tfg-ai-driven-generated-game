import asyncio
import base64
import os
import sys
from dotenv import load_dotenv
# Ensure the project path is available
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from subsystems.image_generation.scenarios.create.orchestrator import get_created_scenario_images_generation_app
from subsystems.image_generation.scenarios.create.schemas import GraphState
from core_game.map.schemas import ScenarioModel
from subsystems.image_generation.scenarios.create.scenario_processor.schemas import ScenarioProcessorState


async def main():
    """
    Main function to configure and run the image generation graph.
    """

    graph = get_created_scenario_images_generation_app()

    load_dotenv()
    current_api_url = current_api_url = os.getenv("SCENARIOS_IMAGE_API_URL")
    if not current_api_url:
        print("Error: The SCENARIOS_IMAGE_API_URL environment variable is not set or could not be found.")
        print("Please ensure you have a .env file with this variable defined.")
        return
    
    # Define the output directory for the images
    output_dir = os.path.join('images', 'scenarios')
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # --- 2. Graph Execution ---
    print("--- 🚀 Starting the main graph execution ---")
    result = await graph.ainvoke(GraphState(
        image_api_url=current_api_url,
        scenarios=[
            # Make sure each scenario has a unique 'id' for the filename
            ScenarioModel(
                id="scenario_001",
                name="HELLO",
                visual_description="A tiny house at the outside of town",
                summary_description="asdasd",
                narrative_context="Sasd",
                indoor_or_outdoor="indoor",
                zone="asddasd",
                type="ass"
            ),
            ScenarioModel(
                id="scenario_002",
                name="GOODBYE",
                visual_description="A dark cave with glowing mushrooms",
                summary_description="qwerty",
                narrative_context="zxcv",
                indoor_or_outdoor="outdoor",
                zone="qwerty",
                type="zxcv"
            )
        ],
        graphic_style="cartoon",
        general_game_context="a game where there are zombies"
    ))
    
    # --- 3. Result Processing ---
    print("\n--- 📊 Processing final results ---")
    
    # Save images from successful scenarios
    final_graph_state = GraphState(**result)
    if final_graph_state.successful_scenarios:
        print(f"  - Saving {len(final_graph_state.successful_scenarios)} successful images...")
        for scenario_state in final_graph_state.successful_scenarios:
            # We convert the dictionary back to our Pydantic model
            try:
                # Decode the image from base64 using attribute notation
                assert scenario_state.image_base64 is not None
                img_bytes = base64.b64decode(scenario_state.image_base64)
                

                file_name = f"{scenario_state.scenario.id}.png"
                output_path = os.path.join(output_dir, file_name)
                

                with open(output_path, "wb") as f:
                    f.write(img_bytes)
                print(f"    - ✅ Image saved to: {output_path}")

            except Exception as e:
                print(f"    - ❌ Error saving image for scenario {scenario_state.scenario.id}: {e}")
    



if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: The OPENAI_API_KEY environment variable is not set.")
    else:
        asyncio.run(main())