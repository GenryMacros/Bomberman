from tiles import Tile, Wall


class AStar:
    @classmethod
    def find_best_route(cls, start, end, game_field,
                        ignore_breakable=False, ignore_bombs=False, find_safest=False):
        if find_safest and cls.is_tile_safe(start, game_field):
            return []
        visited = {}
        came_from = {}
        queue = [start]
        coords2tile = game_field.coords2tile
        is_reachable = False
        last_tile = None
        while len(queue) > 0:
            current_pos = queue.pop(0)
            if visited.get(current_pos, None) is not None:
                continue
            visited[current_pos] = True
            if current_pos == end or (find_safest and cls.is_tile_safe(current_pos, game_field)):
                is_reachable = True
                last_tile = current_pos
                break
            tiles_to_check = [
                (current_pos[0] + 1, current_pos[1]),
                (current_pos[0], current_pos[1] + 1),
                (current_pos[0] - 1, current_pos[1]),
                (current_pos[0], current_pos[1] - 1)
            ]
            for tile_id in tiles_to_check:
                if coords2tile.get(tile_id, None) and not visited.get(tile_id, None):
                    tile = coords2tile[tile_id]
                    bomb = game_field.coords2bombs.get(tile_id, None)
                    death = game_field.coords2deadTile.get(tile_id, None)
                    if ignore_bombs:
                        bomb = None
                    if (isinstance(tile, Tile) or tile == 'f') and bomb is None and death is None:
                        came_from[tile_id] = current_pos
                        queue.append(tile_id)
                    if ignore_breakable and ((isinstance(tile, Wall) and tile.is_destructible) or tile == 'dw') and bomb is None:
                        came_from[tile_id] = current_pos
                        queue.append(tile_id)
        if is_reachable:
            route = []
            current_pos = last_tile
            while current_pos != start:
                route.insert(0, current_pos)
                current_pos = came_from[current_pos]
            return route
        return []

    @classmethod
    def is_tile_safe(cls, tile_id, game_field):
        for bomb in game_field.bombs:
            if ((tile_id[0] > bomb.field_id[0] + 3) or (tile_id[0] < bomb.field_id[0] - 3)) or \
               ((tile_id[1] > bomb.field_id[1] + 3) or (tile_id[1] < bomb.field_id[1] - 3)):
                continue
            else:
                return False
        return True
