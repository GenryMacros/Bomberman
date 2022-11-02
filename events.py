from dataclasses import dataclass
from enum import Enum


class GameFieldEventType(Enum):
    BONUS_PICKED = "bonus_picked"
    BOMB_EXPLODED = "bomb_exploded"
    NONE = "none"


@dataclass
class GameFieldEvent:
    type: GameFieldEventType
    data: dict