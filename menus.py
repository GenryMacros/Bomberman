import copy
from enum import Enum

import pygame


white  = (255, 255, 255)
black  = (0, 0, 0)
gray   = (50, 50, 50)
red    = (255, 0, 0)
green  = (0, 255, 0)
blue   = (0, 0, 255)
yellow = (255, 255, 0)


class MainMenuCommands(Enum):
    START_GAME = "start_game"
    QUIT = "quit"


class MainMenu:
    def __init__(self, res):
        self.font = "Fonts\EightBitDragon.ttf"
        self.width = res[0]
        self.height = res[1]
        self.menu_buttons_size = 55
        self.main_title = self.text_format("Bomberman", self.font, 70, yellow)
        self.current_button_selected = 0
        self.buttons = {
            0: "START",
            1: "QUIT"
        }
        self.button2Command = {
            0: MainMenuCommands.START_GAME,
            1: MainMenuCommands.QUIT
        }
        self.clock = pygame.time.Clock()
        self.accept_next_command = 0
        self.recent_events = []

    def loop(self, screen):
        self.move_cursor()
        screen.blit(self.main_title, (self.width / 2 - (self.main_title.get_rect()[2] / 2), 80))
        for kei in self.buttons:
            if kei == self.current_button_selected:
                button = self.text_format(self.buttons[kei], self.font, self.menu_buttons_size, red)
            else:
                button = self.text_format(self.buttons[kei], self.font, self.menu_buttons_size, white)
            screen.blit(button, (self.width / 2 - (button.get_rect()[2] / 2), 300 + 130*kei))
        pygame.display.update()

    def move_cursor(self):
        self.accept_next_command += 1
        if self.accept_next_command < 80:
            return
        self.accept_next_command = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.current_button_selected += 1
            if self.current_button_selected >= len(self.buttons.keys()):
                self.current_button_selected = 0
        elif keys[pygame.K_s]:
            self.current_button_selected -= 1
            if self.current_button_selected < 0:
                self.current_button_selected = len(self.buttons.keys()) - 1
        elif keys[pygame.K_RETURN]:
            self.recent_events.append(self.button2Command[self.current_button_selected])

    def text_format(self, message, text_font, text_size, text_color):
        new_font = pygame.font.Font(text_font, text_size)
        new_text = new_font.render(message, 0, text_color)

        return new_text

    def get_recent_events(self):
        events = copy.deepcopy(self.recent_events)
        self.recent_events.clear()
        return events
