import copy
import time

from enemy import Enemy
from game_field import GameField
from pygame import image, transform

from tiles import Tile, Wall
from utils import AStar


class Worm(Enemy):
    def __init__(self, pos, game_field: GameField, field_id, sprite_scale=1):
        super().__init__()
        self.game_field = game_field
        self.paths_to_sprites = ["Sprites/Enemies/Worm/loop1.png",
                                 "Sprites/Enemies/Worm/loop2.png",
                                 "Sprites/Enemies/Worm/loop3.png",
                                 "Sprites/Enemies/Worm/loop4.png"]
        self.image = image.load(self.paths_to_sprites[0])
        self.image = transform.scale(self.image, (int(self.image.get_width() * sprite_scale),
                                                  int(self.image.get_height() * sprite_scale)))
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.speed = 3
        self.repeat_animation = []
        for path in self.paths_to_sprites:
            anim_p = image.load(path)
            anim_p = transform.scale(anim_p, (int(anim_p.get_width() * sprite_scale),
                                              int(anim_p.get_height() * sprite_scale)))
            self.repeat_animation.append(anim_p)
        self.anim_count = 0
        self.min_patrol_length = 2
        self.max_patrol_length = 20
        self.way_points = []
        self.current_way_point_index = 0
        self.last_route = []
        self.health = 1
        self.update_timer = 10
        self.to_update = self.update_timer
        self.last_patrol_change = time.time()
        self.change_patroll_every = 30
        self.is_probably_locked = False
        self.is_looking_left = False
        self.create_patrol_route(field_id)

    def create_patrol_route(self, field_id):
        self.way_points = []
        avaliable_routes = self.find_new_route(field_id, False)
        max_route = self.find_max_route(avaliable_routes)
        if len(max_route) >= self.min_patrol_length:
            self.form_waypoints_from_route(max_route)
        else:
            with_break_routes = self.find_new_route(field_id, True)
            max_route = self.find_max_route(with_break_routes)
            self.form_waypoints_from_route(max_route)
        if len(max_route) <= self.min_patrol_length:
            self.is_probably_locked = True
        self.last_patrol_change = time.time()
        self.current_way_point_index = 0
        self.to_update = self.update_timer

    def find_new_route(self, field_id, is_with_breakable):
        visited = {}
        routes = [[field_id]]
        stack = [(field_id, routes[0])]
        coords2tile = self.game_field.coords2tile
        while len(stack) > 0:
            current_pos, current_route = stack.pop()
            if visited.get(current_pos, None) is not None:
                continue
            visited[current_pos] = True
            tiles_to_check = [
                (current_pos[0] + 1, current_pos[1]),
                (current_pos[0], current_pos[1] + 1),
                (current_pos[0] - 1, current_pos[1]),
                (current_pos[0], current_pos[1] - 1)
            ]
            turns = []
            for tile_id in tiles_to_check:
                if coords2tile.get(tile_id, None) and not visited.get(tile_id, None):
                    tile = coords2tile[tile_id]
                    if isinstance(tile, Tile):
                        turns.append(tile_id)
                    elif isinstance(tile, Wall) and tile.is_destructible and is_with_breakable:
                        turns.append(tile_id)
            current_route_copy = copy.deepcopy(current_route)
            for i in range(len(turns)):
                if i >= 1:
                    current_route_copy.append(turns[i])
                    stack.append((turns[i], current_route_copy))
                    routes.append(current_route_copy)
                else:
                    current_route.append(turns[i])
                    stack.append((turns[i], current_route))
        return routes

    def find_max_route(self, routes):
        cur_max = routes[0]
        for route in routes:
            if len(cur_max) < len(route) <= self.max_patrol_length:
                cur_max = route
        return cur_max

    def form_waypoints_from_route(self, route):
        if len(route) > self.min_patrol_length:
            for i in range(0, len(route), 3):
                if i > len(route) - 1:
                    self.way_points.append(route[-1])
                    break
                elif i + 3 > len(route) - 1:
                    self.way_points.append(route[-1])
                else:
                    self.way_points.append(route[i])
        else:
            self.way_points = [route[0], route[-1]]

    def draw(self, screen):
        anim_index = self.anim_count // 6
        if anim_index < len(self.repeat_animation) - 1:
            self.anim_count += 1
        else:
            self.anim_count = 0
        screen.blit(transform.flip(self.repeat_animation[anim_index], self.is_looking_left, False), self.rect)

    def make_move(self, player_pos):
        current_index = self.game_field.get_entity_index(self)
        self.update_route(current_index)
        self.change_waypoint_target()
        next_tile = self.game_field.coords2tile[self.last_route[0]]
        if abs(next_tile.rect.centery - self.rect.centery) > 5:
            mod = ((next_tile.rect.centery - self.rect.centery) / abs(next_tile.rect.centery - self.rect.centery))
            if not self.game_field.is_collision(0, self.speed * mod, self, (10, 10)).is_collision:
                self.rect.y += self.speed * mod
        if abs(next_tile.rect.centerx - self.rect.centerx) > 5:
            mod = ((next_tile.rect.centerx - self.rect.centerx) / abs(next_tile.rect.centerx - self.rect.centerx))
            if not self.game_field.is_collision(self.speed * mod, 0, self, (10, 10)).is_collision:
                self.rect.x += self.speed * mod
            if mod < 0:
                self.is_looking_left = False
            else:
                self.is_looking_left = True
        if time.time() - self.last_patrol_change >= self.change_patroll_every:
            self.create_patrol_route(current_index)
            self.last_patrol_change = time.time()

    def change_waypoint_target(self):
        current_target_tile = self.game_field.coords2tile[self.way_points[self.current_way_point_index]]
        if current_target_tile.rect.colliderect(self.rect):
            self.current_way_point_index += 1
            if len(self.last_route) > 1:
                self.last_route.pop(0)
            if self.current_way_point_index == len(self.way_points):
                self.current_way_point_index = 0

    def update_route(self, current_index):
        if self.to_update >= self.update_timer:
            self.last_route = AStar.find_best_route(current_index,
                                                    self.way_points[self.current_way_point_index],
                                                    self.game_field)
            if not self.last_route:
                self.current_way_point_index = 0
                while not self.last_route:
                    self.last_route = AStar.find_best_route(current_index,
                                                            self.way_points[self.current_way_point_index],
                                                            self.game_field)
                    self.current_way_point_index += 1
                    if self.current_way_point_index >= len(self.way_points):
                        self.current_way_point_index = 0
                        self.last_route = [self.game_field.get_entity_index(self)]
                        break
            self.to_update = 0
        else:
            self.to_update += 1

    def check_if_exploded(self, exploded_tiles):
        for tile in exploded_tiles:
            if tile.rect.colliderect(self.rect):
                self.health -= 1
                self.anim_count = 0
                return True
        return False

    def react_on_explosions(self, data):
        if self.is_probably_locked:
            self.create_patrol_route(self.game_field.get_entity_index(self))
