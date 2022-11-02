import copy


class WormMock:
    def __init__(self, field_id, game_field):
        self.field_id = field_id
        self.game_field = game_field
        self.way_points = []
        self.current_way_point_index = 0
        self.last_route = []
        self.min_patrol_length = 2
        self.max_patrol_length = 20
        self.create_patrol_route(field_id)

    def make_move(self, player_pos):
        self.change_waypoint_target()
        next_tile = self.game_field.coords2tile[self.last_route[0]]
        self.game_field.coords2tile[self.field_id] = self.game_field.coords2tile[self.field_id].split(" ")[0]
        if next_tile[0] != self.field_id[0]:
            mod = (next_tile[0] - self.field_id[0]) / abs(next_tile[0] - self.field_id[0])
            if self.game_field.is_passable((self.field_id[0] + mod, self.field_id[1])):
                self.field_id = (self.field_id[0] + mod, self.field_id[1])
        elif next_tile[1] != self.field_id[1]:
            mod = (next_tile[1] - self.field_id[1]) / abs(next_tile[1] - self.field_id[1])
            if self.game_field.is_passable((self.field_id[0] + mod, self.field_id[1])):
                self.field_id = (self.field_id[0], self.field_id[1] + mod)
        self.game_field.coords2tile[self.field_id] = self.game_field.coords2tile[self.field_id].split(" ")[0] + "worm"

    def change_waypoint_target(self):
        current_target_tile = self.way_points[self.current_way_point_index]
        if self.field_id == current_target_tile:
            self.current_way_point_index += 1
            if len(self.last_route) > 1:
                self.last_route.pop(0)
            if self.current_way_point_index == len(self.way_points):
                self.current_way_point_index = 0

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
        self.current_way_point_index = 0

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
                    if tile == "f" or (tile == "dw" and is_with_breakable):
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
