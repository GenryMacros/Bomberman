from enum import Enum


class ObstacleType(Enum):
    WALL = "w"
    DESTRUCTABLE_WALL = "dw"
    FIELD = "f"
    PLAYER_START_POS = "p"

lvls = {1: [
        ["w", "w", "w", "w", "w", "w", "w", "w", "w", "w", "w", "w", "w", "w", "w", "w", "w", "w", "w", "w", "w", "w", "w", "w", "w"],
        ["w", "f", "f orc", "dw", "f", "f", "dw", "f", "f", "dw", "f", "dw", "dw", "f", "f", "f", "f", "f", "f", "f", "f", "f", "dw", "f", "w"],
        ["w", "dw", "w", "dw", "w", "dw", "w", "f", "w", "dw", "w", "f", "f", "f", "w", "f", "w", "dw", "w", "f", "w", "f", "w", "f", "w"],
        ["w", "f", "w", "f", "w", "dw", "w", "f", "w", "dw", "w", "f", "dw", "f", "w", "f", "w", "dw", "w", "f", "w", "f", "w", "f", "w"],
        ["w", "f", "w", "f", "w", "dw", "dw", "f", "w", "dw", "w", "f", "dw", "f", "w", "f", "w", "dw", "w", "f", "w", "f", "w", "f", "w"],
        ["w", "f", "f", "f", "w", "f", "w", "f", "w", "dw", "w", "f", "f", "f", "w", "f", "f", "dw", "w", "f", "w", "f", "w", "f", "w"],
        ["w", "f", "w", "f", "w", "dw", "w", "f", "dw", "dw", "w", "f", "dw", "f", "w", "f", "w", "f", "w", "f", "w", "f", "w", "f", "w"],
        ["w", "f", "w", "f", "dw", "dw", "w", "f", "w", "dw", "w", "f", "dw", "f", "w", "f", "w", "f", "w", "f", "w", "f", "w", "f", "w"],
        ["w", "f", "w", "f", "w", "f", "dw", "f", "w", "f", "w", "f", "dw", "f", "w", "f", "w", "dw", "w", "f", "w", "f", "w", "f", "w"],
        ["w", "f", "f", "f", "w", "dw", "w", "f", "w", "f", "w", "f", "f", "f", "w", "f", "w", "dw", "w", "f", "dw", "f", "w", "f", "w"],
        ["w", "f", "w", "f", "w", "dw", "w", "f", "w", "dw", "w", "f", "dw", "f", "w", "f", "w", "dw", "w", "f", "w", "f", "w", "f", "w"],
        ["w", "p", "dw flames", "f", "w", "dw", "w", "f", "w", "dw", "w", "f", "dw", "f", "f", "f", "f", "dw", "dw", "f", "w", "f", "w", "f", "w"],
        ["w", "w", "w", "w", "w", "w", "w", "w", "w", "w", "w", "w", "w", "w", "w", "w", "w", "w", "w", "w", "w", "w", "w", "w", "w"]
    ]
}
