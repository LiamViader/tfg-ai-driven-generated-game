from typing import Sequence

def format_window(logs_window: int, refinement_logs: Sequence[str]) -> str:
    selected_logs = refinement_logs[-logs_window:]

    return "; ".join(selected_logs)