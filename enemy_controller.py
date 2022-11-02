from pygame import Rect

from enemy import EnemyType
from lvls import lvls
from orc import Orc
from player import Player
from worm import Worm


class EnemyController:
    def __init__(self, game_field, player, lvl=1):
        self.enemies = []
        self.game_field = game_field
        self.player = player
        self.spawn_enemies(lvl)

    def spawn_enemies(self, lvl):
        lvl_scheme = lvls[lvl]
        for i in range(len(lvl_scheme)):
            for j in range(len(lvl_scheme[i])):
                tile_scheme = lvl_scheme[i][j].split(' ')
                tile = self.game_field.coords2tile[(i, j)]
                if len(tile_scheme) > 1 and tile_scheme[0] == 'f':
                    if EnemyType(tile_scheme[1]) == EnemyType.WORM:
                        worm = Worm((tile.rect.x, tile.rect.y),
                                    self.game_field,
                                    (i, j),
                                    sprite_scale=0.7)
                        self.enemies.append(worm)
                    elif EnemyType(tile_scheme[1]) == EnemyType.ORC:
                        orc = Orc((tile.rect.x, tile.rect.y),
                                    self.game_field,
                                    (i, j),
                                    self.player,
                                    self,
                                    sprite_scale=0.9)
                        self.enemies.append(orc)
                    elif EnemyType(tile_scheme[1]) == EnemyType.ANCIENT:
                        pass

    def make_move(self, screen, player_pos):
        for enemy in self.enemies:
            enemy.make_move(player_pos)
            enemy.draw(screen)

    def check_if_someone_exploded(self, exploded_tiles):
        for enemy in self.enemies:
            if enemy.check_if_exploded(exploded_tiles) and enemy.health == 0:
                enemy.kill()
                self.enemies.remove(enemy)

    def damage_player_if_possible(self, player: Player):
        player_rect = Rect(player.rect.centerx, player.rect.centery, 20, 20)
        for enemy in self.enemies:
            if enemy.rect.colliderect(player_rect):
                player.take_damage()
                return

    def react_on_explosions(self, data):
        for enemy in self.enemies:
            enemy.react_on_explosions(data)

    def be_observed(self, observer):
        observer.enemies_left = len(self.enemies)
