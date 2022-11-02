from enum import Enum

from player import LivingEntity, Player


class EnemyType(Enum):
    WORM = "worm"
    ORC = "orc"
    ANCIENT = "ancient"


class Enemy(LivingEntity):
    def __init__(self):
        super().__init__()

    def make_move(self, player_pos):
        pass

    def check_if_exploded(self, exploded_tiles):
        pass

    def check_collision(self, player: Player):
        pass

    def react_on_explosions(self, data):
        pass
