import pygame

from beholder import Beholder
from enemy_controller import EnemyController
from game_field import GameField, GameFieldEventType
from menus import MainMenu, MainMenuCommands
from player import Player, PlayerState


class GameState:
    RUNNING = "running"
    MENU = "menu"
    PAUSE = "pause"
    START_SCREEN = "start_screen"


class Game:
    def __init__(self, game_window_res: (int, int), frames_per_second: int):
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load("Music/default_background.wav")
        pygame.mixer.music.play(-1)
        self.current_lvl = 1
        self.game_window_res = game_window_res
        self.screen = pygame.display.set_mode(game_window_res)
        self.is_running = False
        self.state = GameState.MENU
        self.main_menu = MainMenu(game_window_res)
        self.frames_per_second = frames_per_second
        self.game_field = GameField(game_window_res[0], game_window_res[0] / 16)
        player_pos = self.game_field.get_player_pos()
        self.game_field.move_all_on(game_window_res[0] / 2 - player_pos[0], game_window_res[1] / 2 - player_pos[1], [])
        self.game_field.player_pos = (game_window_res[0] / 2, game_window_res[1] / 2)
        self.player = Player(self.game_field.get_player_pos())
        self.enemy_controller = EnemyController(self.game_field, self.player)
        self.beholder = Beholder(game_window_res, self.player, self.enemy_controller)
        self.clock = pygame.time.Clock()
        self.player_attempts = 2

    def run(self):
        self.is_running = True
        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
            self.screen.fill((0, 0, 0))
            if self.state == GameState.RUNNING:
                self.run_game_cycle()
                self.beholder.draw(self.screen)
                pygame.display.flip()
                if self.player.state == PlayerState.DEAD:
                    self.player_attempts -= 1
                    if self.player_attempts == 0:
                        self.state = GameState.MENU
                    else:
                        self.reset()
            elif self.state == GameState.MENU:
                self.main_menu.loop(self.screen)
                self.parse_main_menu_events()
            elif self.state == GameState.PAUSE:
                pass
            elif self.state == GameState.START_SCREEN:
                pass

    def run_game_cycle(self):
        exploded_tiles = self.game_field.draw(self.screen)
        self.player.check_if_exploded(exploded_tiles)
        self.enemy_controller.check_if_someone_exploded(exploded_tiles)
        self.enemy_controller.damage_player_if_possible(self.player)
        self.player.draw(self.screen)
        self.enemy_controller.make_move(self.screen, self.game_field.get_entity_index(self.player))

        dt = self.clock.tick(self.frames_per_second)
        player_events = self.player.process_input(dt)
        for player_event in player_events:
            self.game_field.move(player_event, self.player, self.enemy_controller.enemies)
        last_events = self.game_field.return_last_events()
        for event in last_events:
            if event.type == GameFieldEventType.BONUS_PICKED:
                self.player.consume_bonus(event.data["bonus"])
            elif event.type == GameFieldEventType.BOMB_EXPLODED:
                self.enemy_controller.react_on_explosions(event.data)
        self.player.be_observed(self.beholder)
        self.enemy_controller.be_observed(self.beholder)
        self.beholder.player_attempts = self.player_attempts

    def parse_main_menu_events(self):
        events = self.main_menu.get_recent_events()
        for event in events:
            if event == MainMenuCommands.START_GAME:
                self.state = GameState.RUNNING
                self.player_attempts = 2
            if event == MainMenuCommands.QUIT:
                self.is_running = False

    def reset(self):
        self.game_field = GameField(self.game_window_res[0], self.game_window_res[0] / 16)
        player_pos = self.game_field.get_player_pos()
        self.game_field.move_all_on(self.game_window_res[0] / 2 - player_pos[0], self.game_window_res[1] / 2 - player_pos[1], [])
        self.game_field.player_pos = (self.game_window_res[0] / 2, self.game_window_res[1] / 2)
        self.player = Player(self.game_field.get_player_pos())
        self.enemy_controller = EnemyController(self.game_field, self.player)
        self.beholder = Beholder(self.game_window_res, self.player, self.enemy_controller)
