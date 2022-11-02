import pygame
from pygame import image, transform


class Beholder:
    def __init__(self, game_window_res, player, enemy_controller):
        self.this_height = 90
        self.image = image.load("Sprites/paper.png")
        self.image = transform.scale(self.image, (int(self.image.get_width() * (game_window_res[0] / self.image.get_width())) + 30,
                                                  int(self.image.get_height() * (self.this_height / self.image.get_height()))))
        self.rect = self.image.get_rect()
        self.font = "Fonts\EightBitDragon.ttf"
        self.window_res = game_window_res
        self.player = player
        self.enemy_controller = enemy_controller
        self.player_attempts = 0
        self.enemies_left = 0
        self.player_firepower = 0
        self.player_speed = 0
        self.this_height = 90

    def draw(self, screen):
        x = self.player.rect.x - self.window_res[0] / 2
        y = self.player.rect.y - self.window_res[0] / 2 + 15
        self.rect.x = x
        self.rect.y = y
        screen.blit(self.image, self.rect)
        health = self.text_format(f"Attempts: {self.player_attempts}", self.font, 20, (0, 0, 0))
        fire_power = self.text_format(f"Power: {self.player_firepower}", self.font, 20, (0, 0, 0))
        speed = self.text_format(f"Speed: {self.player_speed}", self.font, 20, (0, 0, 0))
        enemies_left = self.text_format(f"Enemies: {self.enemies_left}", self.font, 20, (0, 0, 0))
        screen.blit(health, (60, self.this_height / 3))
        screen.blit(fire_power, (180 + 60, self.this_height / 3))
        screen.blit(speed, (180 * 2 + 20, self.this_height / 3))
        screen.blit(enemies_left, (180 * 3 - 20, self.this_height / 3))

    def text_format(self, message, text_font, text_size, text_color):
        new_font = pygame.font.Font(text_font, text_size)
        new_text = new_font.render(message, 0, text_color)
        return new_text
