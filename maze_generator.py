from dataclasses import dataclass
from enum import Enum
from typing import List

import numpy as np


class Transition(Enum):
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"


@dataclass
class Cell:
    right_open: bool = False
    left_open: bool = False
    up_open: bool = False
    down_open: bool = False
    is_visited: bool = False


class MazeGenerator:
    def __init__(self, field_size: int, tiles_count: int=64):
        self.tiles_count = tiles_count
        self.size = field_size
        self.maze_map = []
        for i in range(self.tiles_count):
            self.maze_map.append([None] * self.tiles_count)
            for j in range(self.tiles_count):
                self.maze_map[i][j] = Cell()

    def generate_maze(self) -> List[List[Cell]]:
        stack = []
        stack.append(((0, 0), self.maze_map[0][0]))
        backtrack = []
        while len(stack) > 0:
            pos, current_cell = stack.pop()
            backtrack.append((pos, current_cell))
            current_cell.is_visited = True
            possible_transitions = self.get_possible_poses(pos[0], pos[1], current_cell)
            if len(possible_transitions) == 0:
                backtrack.pop()
                if len(backtrack) != 0:
                    stack.append(backtrack.pop())
            else:
                rand_num = np.random.randint(0, high=len(possible_transitions))
                next_transition = possible_transitions[rand_num]
                if next_transition[2] == Transition.RIGHT:
                    current_cell.right_open = True
                    self.maze_map[next_transition[0]][next_transition[1]].left_open = True
                    stack.append((next_transition, self.maze_map[next_transition[0]][next_transition[1]]))
                elif next_transition[2] == Transition.LEFT:
                    current_cell.left_open = True
                    self.maze_map[next_transition[0]][next_transition[1]].right_open = True
                    stack.append((next_transition, self.maze_map[next_transition[0]][next_transition[1]]))
                elif next_transition[2] == Transition.DOWN:
                    current_cell.down_open = True
                    self.maze_map[next_transition[0]][next_transition[1]].up_open = True
                    stack.append((next_transition, self.maze_map[next_transition[0]][next_transition[1]]))
                elif next_transition[2] == Transition.UP:
                    current_cell.up_open = True
                    self.maze_map[next_transition[0]][next_transition[1]].down_open = True
                    stack.append((next_transition, self.maze_map[next_transition[0]][next_transition[1]]))
        return self.maze_map

    def get_possible_poses(self, x, y, cell) -> List[tuple[int, int, Transition]]:
        ret = []
        if x + 1 < self.tiles_count and not self.maze_map[x + 1][y].is_visited:
            ret.append((x + 1, y, Transition.RIGHT))
        if x - 1 >= 0 and not self.maze_map[x - 1][y].is_visited:
            ret.append((x - 1, y, Transition.LEFT))
        if y + 1 < self.tiles_count and not self.maze_map[x][y + 1].is_visited:
            ret.append((x, y + 1, Transition.DOWN))
        if y - 1 >= 0 and not self.maze_map[x][y - 1].is_visited:
            ret.append((x, y - 1, Transition.UP))
        return ret

'''
def generate_field(self):
    maze_generator = MazeGenerator(field_size=self.size,
                                   tiles_count=self.tiles_count)
    self.maze_map = maze_generator.generate_maze()
    self.tile_size_x = self.size / self.tiles_count
    self.tile_size_y = self.tile_size_x
    scale = 1.0
    for i in range(0, len(self.maze_map)):
        cur_x = self.tile_size_x * i * 2
        for j in range(0, len(self.maze_map[i])):
            cur_y = self.tile_size_y * j * 2
            if self.maze_map[i][j].left_open:
                tile = Tile(x_pos=cur_x - self.tile_size_x,
                            y_pos=cur_y,
                            sprite_scale=scale)
                self.floor_tiles.add(tile)
            else:
                wall = Wall(x_pos=cur_x - self.tile_size_x,
                            y_pos=cur_y,
                            is_destructible=False,
                            sprite_scale=scale)
                self.floor_tiles.add(wall)
            if self.maze_map[i][j].right_open:
                tile = Tile(x_pos=cur_x + self.tile_size_x,
                            y_pos=cur_y,
                            sprite_scale=scale)
                self.floor_tiles.add(tile)
            else:
                wall = Wall(x_pos=cur_x + self.tile_size_x,
                            y_pos=cur_y,
                            is_destructible=False,
                            sprite_scale=scale)
                self.floor_tiles.add(wall)

def generate_perimeter(self):
    self.tile_size_x = self.size / self.tiles_count
    self.tile_size_y = self.tile_size_x
    for i in range(self.size):
        current_coord = self.tile_size_x * i
        wall_up = Wall(x_pos=current_coord,
                       y_pos=0,
                       is_destructible=False,
                       sprite_scale=1.0)
        wall_down = Wall(x_pos=current_coord,
                         y_pos=self.tile_size_y * self.tiles_count,
                         is_destructible=False,
                         sprite_scale=1.0)
        wall_left = Wall(x_pos=0,
                         y_pos=current_coord,
                         is_destructible=False,
                         sprite_scale=1.0)
        wall_right = Wall(x_pos=self.tile_size_x * self.tiles_count,
                          y_pos=current_coord,
                          is_destructible=False,
                          sprite_scale=1.0)
        self.wall_tiles.add(wall_up)
        self.wall_tiles.add(wall_down)
        self.wall_tiles.add(wall_left)
        self.wall_tiles.add(wall_right)
'''
