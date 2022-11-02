import copy
import time

from orc import OrcStates, Direction, Target
from utils import AStar


class OrcMock:
    def __init__(self, field_id, game_field, player, controller):
        self.field_id = field_id
        self.game_field = game_field
        self.player = player
        self.controller = controller
        self.state = OrcStates.LOOKING
        self.current_path = []
        self.tiles_worth_checking = []

    def make_move(self, player_pos):
        self.field_id = self.game_field.get_entity_index(self)
        if self.state == OrcStates.LOOKING:
            self.look(player_pos)
        elif self.state == OrcStates.CHASING:
            self.chase()
        elif self.state == OrcStates.BOMB_PUSH:
            self.push_bomb(player_pos)

    def look(self, player_pos):
        self.look_in_direction(Direction.up_direction(), player_pos)
        self.look_in_direction(Direction.down_direction(), player_pos)
        self.look_in_direction(Direction.left_direction(), player_pos)
        self.look_in_direction(Direction.right_direction(), player_pos)
        if self.state == OrcStates.CHASING:
            self.make_move(player_pos)
            return

    def look_in_direction(self, direction, player_pos):
        looking_on_tile = (self.field_id[0] + direction.x,
                           self.field_id[1] + direction.y)
        while self.game_field.coords2tile.get(looking_on_tile, None) is not None:
            if looking_on_tile == player_pos:
                self.start_chase(looking_on_tile, True)
                return
            if self.game_field.coords2bombs.get(looking_on_tile, None):
                self.start_chase((99, 99), True, is_chase_for_live=True)
                return
            if self.game_field.coords2tile[looking_on_tile] == "w":
                break
            looking_on_tile = (looking_on_tile[0] + direction.x,
                               looking_on_tile[1] + direction.y)

    def start_chase(self, target_tile, is_player_target, is_chase_for_live=False):
        if self.state == OrcStates.CHASING and self.current_path and not is_chase_for_live:
            self.tiles_worth_checking.append(Target(target_tile, 1 if is_player_target else 0))
        else:
            self.state = OrcStates.CHASING
            self.current_path = AStar.find_best_route(self.field_id, target_tile,
                                                      self.game_field, ignore_breakable=True,
                                                      ignore_bombs=True if not is_chase_for_live else False,
                                                      find_safest=is_chase_for_live)

    def chase(self):
        next_tile = self.get_next_tile_in_route()
        if next_tile is None:
            self.start_looking()
            return
        if self.field_id[1] != next_tile[1]:
            mod = (next_tile[1] - self.field_id[1]) / abs(next_tile[1] - self.field_id[1])
            if self.is_bomb_on_road((0, mod)):
                self.start_chase((99, 99), True, is_chase_for_live=True)
            if self.game_field.is_passable((self.field_id[0] + mod, self.field_id[1])):
                self.field_id = (self.field_id[0], self.field_id[1] + mod)
        elif self.field_id[0] != next_tile[0]:
            mod = (next_tile[0] - self.field_id[0]) / abs(next_tile[0] - self.field_id[0])
            if self.game_field.is_passable((self.field_id[0] + mod, self.field_id[1])):
                self.field_id = (self.field_id[0] + mod, self.field_id[1])

    def start_looking(self):
        self.state = OrcStates.LOOKING

    def get_next_tile_in_route(self):
        if len(self.current_path) == 0:
            return None
        if self.field_id == self.current_path[0]:
            self.current_path.pop(0)
            if len(self.current_path) == 0:
                return None
            return self.game_field.coords2tile[self.current_path[0]]
        return self.game_field.coords2tile[self.current_path[0]]

    def is_bomb_on_road(self, direction):
        cur_tile = self.game_field.coords2tile[self.field_id]
        cur_id = copy.deepcopy(self.field_id)
        while cur_tile is not None:
            cur_id = (cur_id[0] + direction[0], cur_id[1] + direction[1])
            cur_tile = self.game_field.coords2tile.get(cur_id, None)
            bomb_on_tile = self.game_field.coords2bombs.get(cur_id, None)
            if cur_tile is None or cur_tile == 'w':
                return False
            elif bomb_on_tile is not None and (abs(cur_id[0] - self.field_id[0]) > 2 or abs(cur_id[1] - self.field_id[1]) > 2):
                return True

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
                