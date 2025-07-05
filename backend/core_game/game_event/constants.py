from typing import Tuple, Literal, Union

EVENT_STATUSES: Tuple[str, ...] = (        
    "DRAFT",       # The event is defined but its trigger condition has not been set yet.
    "AVAILABLE",   # Ready to be triggered in the active game world.
    "RUNNING",     # Currently being executed.
    "COMPLETED"    # Finished and part of the historical record.
)

EVENT_STATUS_LITERAL = Literal["DRAFT", "AVAILABLE", "RUNNING", "COMPLETED"]


