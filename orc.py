import copy
import time
from dataclasses import dataclass
from enum import Enum

from bomb import BombOwner, Bomb
from enemy import Enemy
from game_field import GameField

from pygame import image, transform

from tiles import Tile, Wall
from utils import AStar


@dataclass
class Direction:
    x: int = 0
    y: int = 0

    @classmethod
    def up_direction(cls):
        return Direction(0, -1)

    @classmethod
    def down_direction(cls):
        return Direction(0, 1)

    @classmethod
    def right_direction(cls):
        return Direction(1, 0)

    @classmethod
    def left_direction(cls):
        return Direction(-1, 0)


class OrcStates(Enum):
    LOOKING = "looking"
    CHASING = "chasing"
    BOMB_PUSH = "bomb_push"


@dataclass
class Target:
    target: (int, int)
    priority: int = 0


class Orc(Enemy):
    def __init__(self, pos, game_field: GameField, field_id: (int, int), player, controller, sprite_scale=1):
        super().__init__()
        self.game_field = game_field
        self.paths_to_sprites = ["Sprites/Enemies/Orc/loop1.png",
                                 "Sprites/Enemies/Orc/loop2.png",
                                 "Sprites/Enemies/Orc/loop3.png",
                                 "Sprites/Enemies/Orc/loop4.png"]
        self.image = image.load(self.paths_to_sprites[0])
        self.image = transform.scale(self.image, (int(self.image.get_width() * sprite_scale),
                                                  int(self.image.get_height() * sprite_scale)))
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.speed = 6
        self.repeat_animation = []
        self.player = player
        self.controller = controller
        for path in self.paths_to_sprites:
            anim_p = image.load(path)
            anim_p = transform.scale(anim_p, (int(anim_p.get_width() * sprite_scale),
                                              int(anim_p.get_height() * sprite_scale)))
            self.repeat_animation.append(anim_p)
        self.anim_count = 0
        self.health = 1
        self.field_id = field_id
        self.is_looking_left = False
        self.looking_in_directions = []
        self.current_look = 0
        self.change_look_every = 2
        self.boosted_change_look_every = 0.05
        self.last_look_change = time.time()
        self.is_look_boosted = False
        self.state = OrcStates.LOOKING
        self.current_path = []
        self.tiles_worth_checking = []
        self.is_ghost = True
        self.push_direction = Direction(0, 0)
        self.bomb = None
        self.react_range = 8
        self.start_looking()

    def draw(self, screen):
        anim_index = self.anim_count // 6
        if anim_index < len(self.repeat_animation) - 1:
            self.anim_count += 1
        else:
            self.anim_count = 0
        screen.blit(transform.flip(self.repeat_animation[anim_index], self.is_looking_left, False), self.rect)

    def find_worth_looking_directions(self):
        self.looking_in_directions.clear()
        if self.is_direction_worth(Direction.up_direction()):
            self.looking_in_directions.append(Direction.up_direction())
        if self.is_direction_worth(Direction.down_direction()):
            self.looking_in_directions.append(Direction.down_direction())
        if self.is_direction_worth(Direction.right_direction()):
            self.looking_in_directions.append(Direction.right_direction())
        if self.is_direction_worth(Direction.left_direction()):
            self.looking_in_directions.append(Direction.left_direction())

        if len(self.looking_in_directions) == 0:
            self.looking_in_directions.append(Direction.right_direction())

    def is_direction_worth(self, direction: Direction):
        current_tile_x = self.field_id[0]
        current_tile_y = self.field_id[1]
        current_direction_len = 0
        while True:
            current_tile_x += direction.x
            current_tile_y += direction.y
            current_tile = self.game_field.coords2tile.get((current_tile_x, current_tile_y), None)
            if current_tile is not None and isinstance(current_tile, Tile):
                current_direction_len += 1
            else:
                break
        return current_direction_len >= 1

    def make_move(self, player_pos):
        self.field_id = self.game_field.get_entity_index(self)
        if self.state == OrcStates.LOOKING:
            self.look(player_pos)
        elif self.state == OrcStates.CHASING:
            self.chase()
        elif self.state == OrcStates.BOMB_PUSH:
            self.push_bomb(player_pos)

    def look(self, player_pos):
        change_look_every = self.change_look_every
        if self.is_look_boosted:
            self.look_in_direction(Direction.up_direction(), player_pos)
            self.look_in_direction(Direction.down_direction(), player_pos)
            self.look_in_direction(Direction.left_direction(), player_pos)
            self.look_in_direction(Direction.right_direction(), player_pos)
            self.is_look_boosted = False
            if self.state == OrcStates.CHASING:
                self.make_move(player_pos)
                return
        if time.time() - self.last_look_change > change_look_every:
            self.current_look += 1
            if self.current_look >= len(self.looking_in_directions):
                self.current_look = 0
            self.last_look_change = time.time()
        current_direction = self.looking_in_directions[self.current_look]
        if current_direction == Direction.left_direction():
            self.is_looking_left = True
        else:
            self.is_looking_left = False
        self.look_in_direction(current_direction, player_pos)

    def look_in_direction(self, direction, player_pos):
        looking_on_tile = (self.field_id[0] + direction.x,
                           self.field_id[1] + direction.y)
        while self.game_field.coords2tile.get(looking_on_tile, None) is not None:
            if looking_on_tile == player_pos:
                self.start_chase(looking_on_tile, True)
                return
            if self.game_field.coords2bombs.get(looking_on_tile, None) and not self.is_look_boosted:
                self.start_chase((99, 99), True, is_chase_for_live=True)
                return
            if isinstance(self.game_field.coords2tile[looking_on_tile], Wall):
                break
            looking_on_tile = (looking_on_tile[0] + direction.x,
                               looking_on_tile[1] + direction.y)

    def start_chase(self, target_tile, is_player_target, is_chase_for_live=False):
        self.speed = 6
        if self.state == OrcStates.CHASING and self.current_path and not is_chase_for_live:
            self.tiles_worth_checking.append(Target(target_tile, 1 if is_player_target else 0))
        else:
            self.state = OrcStates.CHASING
            self.current_path = AStar.find_best_route(self.field_id, target_tile,
                                                      self.game_field, ignore_breakable=True,
                                                      ignore_bombs=True if not is_chase_for_live else False,
                                                      find_safest=is_chase_for_live)

    def start_looking(self):
        if self.state == OrcStates.CHASING:
            self.is_look_boosted = True
            self.last_look_boost = time.time()
        self.state = OrcStates.LOOKING
        self.find_worth_looking_directions()
        self.current_look = 0

    def start_bomb_push(self, bomb: Bomb, moved_direction: Direction):
        bomb.is_pushed = True
        self.push_direction = moved_direction
        self.state = OrcStates.BOMB_PUSH
        self.speed = 9
        self.bomb = bomb

    def chase(self):
        next_tile = self.get_next_tile_in_route()
        if next_tile is None:
            self.start_looking()
            return
        if abs(next_tile.rect.centery - self.rect.centery) > 4:
            mod = ((next_tile.rect.centery - self.rect.centery) / abs(next_tile.rect.centery - self.rect.centery))
            collision = self.game_field.is_collision(0, self.speed * mod, self, (10, 10))
            if self.is_bomb_on_road((0, mod)):
                self.start_chase((99, 99), True, is_chase_for_live=True)
            if collision.collision_with is None:
                self.rect.y += self.speed * mod
            elif isinstance(collision.collision_with, Bomb):
                self.rect.y += self.speed * mod
                self.start_bomb_push(collision.collision_with,  Direction(0, mod))
                return
        elif abs(next_tile.rect.centerx - self.rect.centerx) > 1:
            mod = ((next_tile.rect.centerx - self.rect.centerx) / abs(next_tile.rect.centerx - self.rect.centerx))
            collision = self.game_field.is_collision(self.speed * mod, 0, self, (10, 10))
            if self.is_bomb_on_road((mod, 0)):
                self.start_chase((99, 99), True, is_chase_for_live=True)
            if mod < 0:
                self.is_looking_left = False
            else:
                self.is_looking_left = True
            if collision.collision_with is None:
                self.rect.x += self.speed * mod
            elif isinstance(collision.collision_with, Bomb):
                self.rect.x += self.speed * mod
                self.start_bomb_push(collision.collision_with, Direction(mod, 0))
                return

    def push_bomb(self, player_pos):
        if not self.is_player_on_road(player_pos):
            self.start_chase((99, 99), False, is_chase_for_live=True)
            self.make_move(player_pos)
            return
        bomb_collision = self.game_field.is_collision(0, 0, self.bomb, size=(16, 16))
        player_collision = self.game_field.is_collision(0, 0, self.player, size=(16, 16))
        if (not bomb_collision.is_collision or isinstance(bomb_collision.collision_with, Bomb)) and not player_collision.is_collision:
            self.rect.x += self.speed * self.push_direction.x
            self.rect.y += self.speed * self.push_direction.y
            self.bomb.rect.x += self.speed * self.push_direction.x
            self.bomb.rect.y += self.speed * self.push_direction.y
            self.game_field.coords2bombs[self.bomb.field_id] = None
            self.bomb.field_id = self.game_field.get_entity_index(self.bomb)
            self.game_field.coords2bombs[self.bomb.field_id] = self.bomb
            if self.player.is_pushed:
                self.game_field.move_all_on(self.speed * -self.push_direction.x,
                                            self.speed * -self.push_direction.y,
                                            self.controller.enemies)

    def is_player_on_road(self, player_pos):
        cur_tile = self.game_field.coords2tile[self.field_id]
        cur_id = copy.deepcopy(self.field_id)
        while cur_tile is not None:
            cur_tile = self.game_field.coords2tile.get(cur_id, None)
            if cur_tile is None or (isinstance(cur_tile, Wall) and not cur_tile.is_destructible):
                return False
            elif cur_id == player_pos:
                return True
            cur_id = (int(cur_id[0] + self.push_direction.x), int(cur_id[1] + self.push_direction.y))

    def is_bomb_on_road(self, direction):
        cur_tile = self.game_field.coords2tile[self.field_id]
        cur_id = copy.deepcopy(self.field_id)
        while cur_tile is not None:
            cur_id = (cur_id[0] + direction[0], cur_id[1] + direction[1])
            cur_tile = self.game_field.coords2tile.get(cur_id, None)
            bomb_on_tile = self.game_field.coords2bombs.get(cur_id, None)
            if cur_tile is None or (isinstance(cur_tile, Wall) and not cur_tile.is_destructible):
                return False
            elif bomb_on_tile is not None \
                and (abs(cur_id[0] - self.field_id[0]) > 2 or abs(cur_id[1] - self.field_id[1]) > 2):
                return True

    def get_next_tile_in_route(self):
        if len(self.current_path) == 0:
            return None
        current_target_tile = self.game_field.coords2tile[self.current_path[0]]
        if abs(self.rect.x - current_target_tile.rect.x) <= 10 and abs(self.rect.y - current_target_tile.rect.y) <= 10:
            self.current_path.pop(0)
            if len(self.current_path) == 0:
                return None
            return self.game_field.coords2tile[self.current_path[0]]
        return self.game_field.coords2tile[self.current_path[0]]

    def check_if_exploded(self, exploded_tiles):
        for tile in exploded_tiles:
            if tile.field_id == self.field_id:
                self.health -= 1
                self.anim_count = 0
                return True
        return False

    def react_on_explosions(self, data):
        if self.state == OrcStates.LOOKING and data["owner"] == BombOwner.PLAYER:
            exploded_tile = data["tile"]
            if abs(exploded_tile[0] - self.field_id[0]) <= self.react_range and \
               abs(exploded_tile[1] - self.field_id[1]) <= self.react_range:
                self.state = OrcStates.CHASING
                self.start_chase(data["tile"], False)
