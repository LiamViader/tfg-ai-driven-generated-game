from core_game.time.schemas import GameTimeModel

class GameTime:
    """Domain class for in-game time."""
    def __init__(self, data: GameTimeModel):
        self.total_minutes_elapsed = data.total_minutes_elapsed
        self.day = data.day
        self.hour = data.hour
        self.minute = data.minute
    
    def advance(self, minutes: int):
        self.total_minutes_elapsed += minutes
        total_minutes = self.day * 1440 + self.hour * 60 + self.minute + minutes
        self.day = total_minutes // 1440
        self.hour = (total_minutes % 1440) // 60
        self.minute = total_minutes % 60