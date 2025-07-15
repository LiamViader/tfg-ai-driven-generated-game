from threading import Thread
from api.services.generation_status import (
    update_global_progress,
    set_done,
    set_error,
    reset
)
from subsystems.generation.orchestrator import get_generation_graph_app
from subsystems.generation.schemas.graph_state import GenerationGraphState
from core_game.game_state.singleton import GameStateSingleton
from subsystems.generation.refinement_loop.pipelines import map_then_characters_pipeline
from utils.progress_tracker import ProgressTracker

def start_generation(prompt: str):
    reset()

    def _run():
        try:
            selected_pipeline = map_then_characters_pipeline()

            # root tracker
            root_tracker = ProgressTracker(update_fn=update_global_progress)

            state = GenerationGraphState(
                initial_prompt=prompt,
                refined_prompt_desired_word_length=200,
                refinement_pipeline_config=selected_pipeline,
                generation_progress_tracker=root_tracker
            )

            update_global_progress(0.0, "Generación iniciada...")
            app = get_generation_graph_app()
            result = app.invoke(state, {"recursion_limit": 1000})

            set_done()
        except Exception as e:
            set_error(str(e))

    Thread(target=_run).start()
    return {"status": "started"}