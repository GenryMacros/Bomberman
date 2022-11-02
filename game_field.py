import copy

from pygame.sprite import Group
from pygame import Rect

from events import GameFieldEvent, GameFieldEventType
from lvls import lvls, ObstacleType
from player import PlayerEvent, PlayerEventType, Player, LivingEntity
from tiles import Wall, Tile, BonusType


class Collision:
    def __init__(self, collision_with, is_collision):
        self.collision_with = collision_with
        self.is_collision = is_collision


class GameField:
    def __init__(self, field_size: int, tiles_count: int=64, sprite_scale=1.0):
        self.tiles_count = tiles_count
        self.size = field_size
        self.wall_tiles = Group()
        self.floor_tiles = Group()
        self.breakable_wall_tiles = Group()
        self.bonuses = Group()
        self.bombs = Group()
        self.temp_objects = Group()
        self.aftermath_objects = Group()
        self.coords2tile = {}
        self.coords2bombs = {}
        self.coords2deadTile = {}
        self.events = []
        self.maze_map = None
        self.player_pos = (0, 0)
        self.sprite_scale = sprite_scale
        self.tile_size_x = 32 * sprite_scale
        self.tile_size_y = self.tile_size_x
        self.generate_field()

    def generate_field(self, lvl=1):
        current_lvl_scheme = lvls[lvl]
        for i in range(len(current_lvl_scheme)):
            pos_x = self.tile_size_x * i * 1.94
            for j in range(len(current_lvl_scheme[i])):
                pos_y = self.tile_size_y * j * 1.94
                if ObstacleType(current_lvl_scheme[i][j].split(' ')[0]) == ObstacleType.WALL:
                    wall = Wall(x_pos=pos_x,
                                y_pos=pos_y,
                                is_destructible=False,
                                sprite_scale=self.sprite_scale,
                                field_id=(i, j),
                                game_field=self)
                    self.coords2tile[(i, j)] = wall
                    self.wall_tiles.add(wall)
                elif ObstacleType(current_lvl_scheme[i][j].split(' ')[0]) == ObstacleType.DESTRUCTABLE_WALL:
                    dwall = Wall(x_pos=pos_x,
                                 y_pos=pos_y,
                                 is_destructible=True,
                                 sprite_scale=self.sprite_scale,
                                 field_id=(i, j),
                                 game_field=self)
                    wall_scheme = current_lvl_scheme[i][j].split(' ')
                    if len(wall_scheme) > 1:
                        dwall.bonus = BonusType(wall_scheme[1])
                    self.coords2tile[(i, j)] = dwall
                    self.breakable_wall_tiles.add(dwall)
                elif ObstacleType(current_lvl_scheme[i][j].split(' ')[0]) == ObstacleType.FIELD:
                    field = Tile(x_pos=pos_x,
                                 y_pos=pos_y,
                                 sprite_scale=self.sprite_scale,
                                 field_id=(i, j))
                    self.coords2tile[(i, j)] = field
                    self.floor_tiles.add(field)
                elif ObstacleType(current_lvl_scheme[i][j].split(' ')[0]) == ObstacleType.PLAYER_START_POS:
                    field = Tile(x_pos=pos_x,
                                 y_pos=pos_y,
                                 sprite_scale=self.sprite_scale,
                                 field_id=(i, j))
                    self.coords2tile[(i, j)] = field
                    self.floor_tiles.add(field)
                    self.player_pos = (pos_x, pos_y)

    def draw(self, screen):
        self.floor_tiles.draw(screen)
        self.bonuses.draw(screen)
        self.wall_tiles.draw(screen)
        self.breakable_wall_tiles.draw(screen)
        exploded_tiles = []
        for bomb in self.bombs:
            exploded_tiles = bomb.tick(screen, self)
        for temp in self.temp_objects:
            temp.draw(screen)
        return exploded_tiles

    def move(self, player_event: PlayerEvent, player: Player, enemies):
        x_speed = 0
        y_speed = 0
        if player_event.event_type == PlayerEventType.MOVE_UP:
            y_speed = player_event.data["speed"]
        elif player_event.event_type == PlayerEventType.MOVE_DOWN:
            y_speed = -player_event.data["speed"]
        elif player_event.event_type == PlayerEventType.MOVE_RIGHT:
            x_speed = -player_event.data["speed"]
        elif player_event.event_type == PlayerEventType.MOVE_LEFT:
            x_speed = player_event.data["speed"]
        elif player_event.event_type == PlayerEventType.SPAWN_BOMB:
            self.place_bomb(player_event.data["bomb"], self.player_pos)

        if self.is_collision(x_speed + 7, y_speed + 2, player).is_collision:
            return
        self.move_all_on(x_speed, y_speed, enemies)
        picked_bonus = self.check_if_bonus_picked_up()
        if picked_bonus is not None:
            self.events.append(GameFieldEvent(GameFieldEventType.BONUS_PICKED, {"bonus": picked_bonus.type}))

    def move_all_on(self, on_x, on_y, enemies):
        for wall in self.wall_tiles:
            wall.rect.y += on_y
            wall.rect.x += on_x
        for bwall in self.breakable_wall_tiles:
            bwall.rect.y += on_y
            bwall.rect.x += on_x
        for bomb in self.bombs:
            bomb.rect.y += on_y
            bomb.rect.x += on_x
        for bonus in self.bonuses:
            bonus.rect.y += on_y
            bonus.rect.x += on_x
        for floor in self.floor_tiles:
            floor.rect.y += on_y
            floor.rect.x += on_x
        for temp in self.temp_objects:
            temp.rect.y += on_y
            temp.rect.x += on_x
        for enemy in enemies:
            enemy.rect.y += on_y
            enemy.rect.x += on_x

    def is_collision(self, x_change, y_change, entity_to_check: LivingEntity, size=(16, 16)):
        rect = Rect(entity_to_check.rect.centerx + x_change*-1, entity_to_check.rect.centery + y_change*-1, size[0], size[1])
        true_rect = Rect(self.player_pos[0], self.player_pos[1], 16, 16)

        if isinstance(entity_to_check, Player) and not entity_to_check.is_pushed:
            for bomb in self.bombs:
                bomb_tile = self.coords2tile[bomb.field_id]
                if bomb_tile.rect.colliderect(true_rect):
                    if bomb.is_pushed:
                        entity_to_check.is_pushed = True
                    return Collision(bomb, False)
                if bomb_tile.rect.colliderect(rect):
                    if bomb.is_pushed:
                        entity_to_check.is_pushed = True
                    return Collision(bomb, True)
        else:
            for bomb in self.bombs:
                if bomb.rect.colliderect(rect):
                    return Collision(bomb, True)

        for wall in self.wall_tiles:
            if wall.rect.colliderect(rect):
                return Collision(wall, True)
        if not entity_to_check.is_ghost:
            for bwall in self.breakable_wall_tiles:
                if bwall.rect.colliderect(rect):
                    return Collision(bwall, True)
        return Collision(None, False)

    def get_player_pos(self):
        return self.player_pos

    def place_bomb(self, bomb, placer_pos, shift=(5, 7)):
        cur_nearest_floor = None
        rect = Rect(placer_pos[0], placer_pos[1], 16, 16)
        for floor in self.floor_tiles:
            if floor.rect.colliderect(rect):
                if cur_nearest_floor is None:
                    cur_nearest_floor = floor
                else:
                    x_diff = abs(floor.rect.centerx - rect.centerx)
                    y_diff = abs(floor.rect.centery - rect.centery)
                    cur_x_diff = abs(cur_nearest_floor.rect.centerx - rect.centerx)
                    cur_y_diff = abs(cur_nearest_floor.rect.centery - rect.centery)
                    if x_diff < cur_x_diff and y_diff < cur_y_diff:
                        cur_nearest_floor = floor
        bomb.field_id = cur_nearest_floor.field_id
        self.coords2bombs[bomb.field_id] = bomb
        bomb.rect.x = cur_nearest_floor.rect.x + shift[0]
        bomb.rect.y = cur_nearest_floor.rect.y + shift[1]
        self.bombs.add(bomb)

    def check_if_bonus_picked_up(self):
        rect = Rect(self.player_pos[0], self.player_pos[1], 16, 16)
        picked_up = None
        for bonus in self.bonuses:
            if bonus.rect.colliderect(rect):
                picked_up = bonus
                bonus.kill()
        return picked_up

    def return_last_events(self):
        recent_events = copy.deepcopy(self.events)
        self.events.clear()
        return recent_events

    def get_entity_index(self, entity: LivingEntity):
        cur_nearest_floor = None
        entity_rect = Rect(entity.rect.centerx, entity.rect.centery, 10, 10)
        for floor in self.floor_tiles:
            if floor.rect.colliderect(entity_rect):
                if cur_nearest_floor is None:
                    cur_nearest_floor = floor
                else:
                    x_diff = abs(floor.rect.centerx - entity_rect.centerx)
                    y_diff = abs(floor.rect.centery - entity_rect.centery)
                    cur_x_diff = abs(cur_nearest_floor.rect.centerx - entity_rect.centerx)
                    cur_y_diff = abs(cur_nearest_floor.rect.centery - entity_rect.centery)
                    if x_diff < cur_x_diff and y_diff < cur_y_diff:
                        cur_nearest_floor = floor
        if cur_nearest_floor is None and entity.is_ghost:
            return self.get_ghost_entity_index(entity)
        return cur_nearest_floor.field_id

    def get_ghost_entity_index(self, entity: LivingEntity):
        cur_nearest_wall = None
        rect = Rect(entity.rect.centerx, entity.rect.centery, 32, 32)
        for wall in self.breakable_wall_tiles:
            if wall.rect.colliderect(rect):
                if cur_nearest_wall is None:
                    cur_nearest_wall = wall
                else:
                    x_diff = abs(wall.rect.centerx - rect.centerx)
                    y_diff = abs(wall.rect.centery - rect.centery)
                    cur_x_diff = abs(cur_nearest_wall.rect.centerx - rect.centerx)
                    cur_y_diff = abs(cur_nearest_wall.rect.centery - rect.centery)
                    if x_diff < cur_x_diff and y_diff < cur_y_diff:
                        cur_nearest_wall = wall

        return cur_nearest_wall.field_id
