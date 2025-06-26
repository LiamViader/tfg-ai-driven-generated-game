from typing import Sequence
from subsystems.agents.utils.schemas import AgentLog
def format_window(logs_window: int, refinement_logs: Sequence[AgentLog]) -> str:
    selected_logs = refinement_logs[-logs_window:]
    
    return "; ".join(f"{log.agent_name}: {log.summary}" for log in selected_logs)