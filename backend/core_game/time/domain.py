from core_game.time.schemas import GameTimeModel
from typing import Optional

class GameTime:
    """Domain class for in-game time."""
    def __init__(self, model: Optional[GameTimeModel]=None):
        
        self._total_minutes_elapsed: int
        self._minute: int
        self._hour: int
        self._day: int

        if model:
            self._populate_from_model(model)
        else:
            self._total_minutes_elapsed=0
            self._minute=0
            self._hour=0
            self._day=0


    
    def _populate_from_model(self, model: GameTimeModel) -> None:
        """Populate the domain state from a :class:`GameTimenModel`."""
        self._total_minutes_elapsed = model.total_minutes_elapsed
        self._day = model.day
        self._hour = model.hour
        self._minute = model.minute

    def advance(self, minutes: int):
        self._total_minutes_elapsed += minutes
        total_minutes = self._day * 1440 + self._hour * 60 + self._minute + minutes
        self._day = total_minutes // 1440
        self._hour = (total_minutes % 1440) // 60
        self._minute = total_minutes % 60