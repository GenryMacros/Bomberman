from enum import Enum
from typing import List

from pygame.sprite import Sprite
from pygame import image, transform

from events import GameFieldEvent, GameFieldEventType
from tiles import Tile, Wall


class BombOwner(Enum):
    PLAYER = "player"
    ENEMY = "enemy"


class Explosion(Sprite):
    def __init__(self, x_pos: float,
                       y_pos: float,
                       animation_paths: List[str],
                       game_field,
                       field_id,
                       sprite_scale: float=1.0,
                       owner=BombOwner.PLAYER,
                       spawns_event=False):
        super().__init__()
        self.image = image.load("Sprites/Player/Bomb/temp_explosion.png")
        self.image = transform.scale(self.image, (int(self.image.get_width() * sprite_scale),
                                                  int(self.image.get_height() * sprite_scale)))
        self.rect = self.image.get_rect()
        self.rect.x = x_pos
        self.rect.y = y_pos
        self.explosion_state = []
        for anp in animation_paths:
            an_image = image.load(anp)
            an_image = transform.scale(an_image, (int(an_image.get_width() * sprite_scale),
                                                  int(an_image.get_height() * sprite_scale)))
            self.explosion_state.append(an_image)
        self.frames_to_explode = 30
        self.anim_count = 0
        self.game_field = game_field
        self.field_id = field_id
        self.game_field.coords2deadTile[self.field_id] = self
        self.owner = owner
        self.spawns_event = spawns_event

    def draw(self, screen):
        next_anim_index = self.anim_count // int(self.frames_to_explode / len(self.explosion_state))
        if next_anim_index >= len(self.explosion_state):
            self.kill()
            self.game_field.coords2deadTile[self.field_id] = None
            if self.spawns_event:
                self.game_field.events.append(GameFieldEvent(GameFieldEventType.BOMB_EXPLODED, {"owner": self.owner,
                                                                                                "tile": self.field_id}))
            return
        screen.blit(transform.flip(self.explosion_state[next_anim_index], False, False), self.rect)
        self.anim_count += 1


class Bomb(Sprite):
    def __init__(self, x_pos: float,
                       y_pos: float,
                       sprite_scale: float=2.0,
                       bomb_coords_shift=(-5, -7),
                       exp_range: int=2,
                       owner=BombOwner.PLAYER,
                       states_shift=(-30, -30)):
        super().__init__()
        self.image = image.load("Sprites/Player/Bomb/temp_explosion.png")
        self.image = transform.scale(self.image, (int(self.image.get_width() * 1.0),
                                                  int(self.image.get_height() * 1.0)))
        self.rect = self.image.get_rect()
        self.is_ghost = False
        self.bomb_coords_shift = bomb_coords_shift
        self.explosion_range = exp_range
        self.rect.x = x_pos
        self.rect.y = y_pos
        self.bomb_state_paths = [
            'Sprites/Player/Bomb/bomb1.png',
            'Sprites/Player/Bomb/bomb2.png',
            'Sprites/Player/Bomb/bomb3.png',
            'Sprites/Player/Bomb/bomb4.png',
            'Sprites/Player/Bomb/bomb5.png',
            'Sprites/Player/Bomb/bomb6.png',
            'Sprites/Player/Bomb/bomb7.png',
            'Sprites/Player/Bomb/bomb8.png',
            'Sprites/Player/Bomb/bomb9.png',
            'Sprites/Player/Bomb/bomb10.png',
            'Sprites/Player/Bomb/bomb11.png',
            'Sprites/Player/Bomb/bomb12.png'
        ]
        self.bomb_state = []
        self.states_shift = states_shift
        for path in self.bomb_state_paths:
            state_image = image.load(path)
            state_image = transform.scale(state_image, (int(state_image.get_width() * sprite_scale),
                                                        int(state_image.get_height() * sprite_scale)))
            self.bomb_state.append(state_image)
        self.player_explosion_pack = ["Sprites/Player/Bomb/Explosion/1.png",
                                      "Sprites/Player/Bomb/Explosion/2.png",
                                      "Sprites/Player/Bomb/Explosion/3.png",
                                      "Sprites/Player/Bomb/Explosion/4.png",
                                      "Sprites/Player/Bomb/Explosion/5.png",
                                      "Sprites/Player/Bomb/Explosion/6.png",
                                      "Sprites/Player/Bomb/Explosion/7.png",
                                      "Sprites/Player/Bomb/Explosion/8.png",
                                      "Sprites/Player/Bomb/Explosion/9.png",
                                      "Sprites/Player/Bomb/Explosion/10.png",
                                      "Sprites/Player/Bomb/Explosion/11.png",
                                      "Sprites/Player/Bomb/Explosion/12.png"]
        self.frames_to_explode = 60
        self.anim_count = 0
        self.time_left = self.frames_to_explode
        self.field_id = (0, 0)
        self.owner = owner
        self.is_pushed = False

    def tick(self, screen, game_field):
        self.time_left -= 1
        next_anim_index = self.anim_count // int(self.frames_to_explode / len(self.bomb_state))
        if next_anim_index < len(self.bomb_state) - 1:
            self.anim_count += 1
        screen.blit(transform.flip(self.bomb_state[next_anim_index], False, False),
                    (self.rect.x + self.states_shift[0], self.rect.y + self.states_shift[1]))
        if self.time_left == 0:
            self.kill()
            game_field.coords2bombs[self.field_id] = None
            return self.explode(game_field)
        return []

    def explode(self, game_field):
        exploded_tiles = []
        exploded_tiles += self.explode_direction(game_field, 1, 0)
        exploded_tiles += self.explode_direction(game_field, -1, 0)
        exploded_tiles += self.explode_direction(game_field, 0, 1)
        exploded_tiles += self.explode_direction(game_field, 0, -1)
        this_tile_explosion = Explosion(self.rect.x + self.bomb_coords_shift[0],
                                        self.rect.y + self.bomb_coords_shift[1],
                                        animation_paths=self.player_explosion_pack,
                                        game_field=game_field,
                                        field_id=self.field_id,
                                        owner=self.owner,
                                        spawns_event=True,
                                        sprite_scale=2.0)
        game_field.temp_objects.add(this_tile_explosion)
        exploded_tiles.append(game_field.coords2tile[self.field_id])
        return exploded_tiles

    def explode_direction(self, game_field, x_step, y_step):
        exploded_tiles = []
        for i in range(self.explosion_range):
            explode_tile_pos = (self.field_id[0] + x_step * (i + 1), self.field_id[1] + y_step * (i + 1))
            obj_on_coords = game_field.coords2tile.get(explode_tile_pos, None)
            if not obj_on_coords:
                break
            if isinstance(obj_on_coords, Tile):
                exp = Explosion(obj_on_coords.rect.x, obj_on_coords.rect.y,
                                animation_paths=self.player_explosion_pack,
                                game_field=game_field,
                                field_id=explode_tile_pos,
                                owner=self.owner,
                                sprite_scale=2.0)
                game_field.temp_objects.add(exp)
                exploded_tiles.append(obj_on_coords)
            elif isinstance(obj_on_coords, Wall) and obj_on_coords.is_destructible:
                field = Tile(x_pos=obj_on_coords.rect.x,
                             y_pos=obj_on_coords.rect.y,
                             sprite_scale=game_field.sprite_scale,
                             field_id=explode_tile_pos)
                game_field.coords2tile[explode_tile_pos] = field
                game_field.floor_tiles.add(field)
                obj_on_coords.kill()
                break
            else:
                break
        return exploded_tiles
