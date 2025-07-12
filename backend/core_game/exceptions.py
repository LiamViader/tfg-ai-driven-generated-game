class GameLogicError(Exception):
    """Clase base para errores específicos de la lógica del juego."""
    pass

class PlayerDeletionError(GameLogicError):
    """Se lanza cuando se intenta realizar una operación inválida sobre el jugador, como borrarlo."""
    pass