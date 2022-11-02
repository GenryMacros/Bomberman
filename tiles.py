import numpy as np

from enum import Enum

from pygame.sprite import Sprite
from pygame import image, transform


class BonusType(Enum):
    FLAMES = "flames"
    WALLPASS = "wallpass"
    SPEED = "speed"
    NONE = "none"


class Bonus(Sprite):
    def __init__(self, x_pos: float, y_pos: float, sprite_scale: float, bonus_type: BonusType):
        super().__init__()
        self.type = bonus_type
        self.image = image.load(self.get_bonus_img_path())
        self.image = transform.scale(self.image, (int(self.image.get_width() * sprite_scale),
                                                  int(self.image.get_height() * sprite_scale)))
        self.rect = self.image.get_rect()
        self.rect.x = x_pos
        self.rect.y = y_pos

    def get_bonus_img_path(self):
        if self.type == BonusType.FLAMES:
            return "Sprites/Power_Ups/flames_buff.png"
        elif self.type == BonusType.SPEED:
            return "Sprites/Power_Ups/speed_buff.png"
        elif self.type == BonusType.WALLPASS:
            return "Sprites/Power_Ups/cheat_buff.png"


class Tile(Sprite):
    def __init__(self, x_pos: float, y_pos: float, sprite_scale: float, field_id: (int, int)):
        super().__init__()
        self.field_id = field_id
        self.image = image.load(self.choose_sprite())
        self.image = transform.scale(self.image, (int(self.image.get_width() * sprite_scale),
                                                  int(self.image.get_height() * sprite_scale)))
        self.rect = self.image.get_rect()
        self.rect.x = x_pos
        self.rect.y = y_pos
        self.rect.centerx = x_pos + self.image.get_width() / 2
        self.rect.centery = y_pos + self.image.get_height() / 2

    def choose_sprite(self) -> str:
        rand_num = np.random.randint(1, high=5)
        return f"Sprites/Surface/floor{rand_num}.png"


class Wall(Sprite):
    def __init__(self, x_pos: float, y_pos: float, is_destructible: bool, sprite_scale: float, field_id: (int, int), game_field):
        super().__init__()
        self.is_destructible = is_destructible
        self.field_id = field_id
        self.image = image.load(self.choose_sprite())
        self.image = transform.scale(self.image, (int(self.image.get_width() * sprite_scale),
                                                  int(self.image.get_height() * sprite_scale)))
        self.rect = self.image.get_rect()
        self.rect.x = x_pos
        self.rect.y = y_pos
        self.game_field = game_field
        self.bonus = BonusType.NONE

    def set_bonus(self, bonus: Bonus):
        self.bonus = bonus

    def kill(self):
        super().kill()
        if self.bonus == BonusType.NONE:
            return
        elif self.bonus == BonusType.SPEED:
            self.game_field.bonuses.add(Bonus(self.rect.x, self.rect.y, 1.6, BonusType.SPEED))
        elif self.bonus == BonusType.FLAMES:
            self.game_field.bonuses.add(Bonus(self.rect.x, self.rect.y, 1.6, BonusType.FLAMES))
        elif self.bonus == BonusType.WALLPASS:
            self.game_field.bonuses.add(Bonus(self.rect.x, self.rect.y, 1.6, BonusType.WALLPASS))

    def choose_sprite(self) -> str:
        if self.is_destructible:
            return "Sprites/Surface/cracking_wall.png"
        else:
            rand_num = np.random.randint(1, high=9)
            return f"Sprites/Surface/wall{rand_num}.png"
