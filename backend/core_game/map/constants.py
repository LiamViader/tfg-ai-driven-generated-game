from typing import Literal, Dict



Direction = Literal["north", "south", "east", "west"]

OppositeDirections: Dict[Direction, Direction] = {
    "north": "south", "south": "north",
    "east": "west", "west": "east"
}

IndoorOrOutdoor = Literal["indoor", "outdoor"]