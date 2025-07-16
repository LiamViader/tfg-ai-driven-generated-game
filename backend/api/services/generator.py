from threading import Thread
from api.services.generation_status import (
    update_global_progress,
    set_done,
    set_error,
    reset,
    get_status,
)
from subsystems.generation.orchestrator import get_generation_graph_app
from subsystems.generation.schemas.graph_state import GenerationGraphState
from core_game.game_state.singleton import GameStateSingleton
from subsystems.generation.refinement_loop.pipelines import map_then_characters_pipeline, fast_test_pipeline
from utils.progress_tracker import ProgressTracker
from api.schemas.status import GenerationStatusModel

def start_generation(prompt: str) -> GenerationStatusModel:
    reset()

    def _run():
        try:
            selected_pipeline = fast_test_pipeline()

            # root tracker
            root_tracker = ProgressTracker(update_fn=update_global_progress)

            state = GenerationGraphState(
                initial_prompt=prompt,
                refined_prompt_desired_word_length=200,
                refinement_pipeline_config=selected_pipeline,
                generation_progress_tracker=root_tracker
            )

            update_global_progress(0.0, "Generation Initialized...")
            app = get_generation_graph_app()
            result = app.invoke(state, {"recursion_limit": 1000})

            set_done()
        except Exception as e:
            set_error(str(e))

    Thread(target=_run).start()
    status = GenerationStatusModel(
        status="started",
        progress=0.0,
        message="Generation process has been launched",
        detail="You can poll /generate/status to track progress"
    )
    return status

def get_generation_status() -> GenerationStatusModel:
    return get_status()