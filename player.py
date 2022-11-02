from dataclasses import dataclass
from enum import Enum
from typing import List

import pygame
from pygame.sprite import Sprite
from pygame import image, transform

from bomb import Bomb
from tiles import Bonus, BonusType


class PlayerEventType(Enum):
    MOVE_RIGHT = "right"
    MOVE_LEFT = "left"
    MOVE_UP = "up"
    MOVE_DOWN = "down"
    SPAWN_BOMB = "bomb"
    NONE = "none"


class PlayerState(Enum):
    ALIVE = "alive"
    DYING = "dying"
    DEAD = "dead"


@dataclass
class PlayerEvent:
    event_type: PlayerEventType = None
    data: dict = None


class LivingEntity(Sprite):
    def __init__(self):
        super().__init__()
        self.is_ghost = False


class Player(LivingEntity):
    def __init__(self, pos, sprite_scale=1):
        super().__init__()
        self.power_ups = []
        self.health = 1
        self.speed = 5
        self.bomb_explosion_range = 2
        self.path_to_sprite = "Sprites/Player/loop1.png"
        self.image = image.load(self.path_to_sprite)
        self.image = transform.scale(self.image, (int(self.image.get_width() * sprite_scale),
                                                  int(self.image.get_height() * sprite_scale)))
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.rect.centerx = pos[0] + self.image.get_width() / 4 - 5
        self.rect.centery = pos[1] + self.image.get_height() / 4 - 5
        self.repeat_animation = [
            pygame.image.load('Sprites/Player/loop1.png'),
            pygame.image.load('Sprites/Player/loop2.png'),
            pygame.image.load('Sprites/Player/loop3.png'),
            pygame.image.load('Sprites/Player/loop4.png')
        ]
        self.die_animation = [
            pygame.image.load('Sprites/Player/die1.png'),
            pygame.image.load('Sprites/Player/die2.png'),
            pygame.image.load('Sprites/Player/die3.png'),
            pygame.image.load('Sprites/Player/die4.png'),
            pygame.image.load('Sprites/Player/die5.png'),
            pygame.image.load('Sprites/Player/die6.png'),
            pygame.image.load('Sprites/Player/die7.png'),
            pygame.image.load('Sprites/Player/die8.png'),
            pygame.image.load('Sprites/Player/die9.png'),
            pygame.image.load('Sprites/Player/die10.png')
        ]
        self.anim_count = 0
        self.bomb_cooldown = 30
        self.to_next_bomb = 0
        self.state = PlayerState.ALIVE
        self.is_looking_left = False
        self.is_pushed = False

    def draw(self, screen):
        if self.state == PlayerState.ALIVE:
            if self.anim_count >= 24:
                self.anim_count = 0
            screen.blit(pygame.transform.flip(self.repeat_animation[self.anim_count // 6], self.is_looking_left, False), self.rect)
            self.anim_count += 1
            if self.to_next_bomb < 0:
                self.to_next_bomb += 1
        elif PlayerState.DYING:
            anim_index = self.anim_count // 10
            if anim_index < len(self.die_animation) - 1:
                self.anim_count += 1
            else:
                self.state = PlayerState.DEAD
            screen.blit(pygame.transform.flip(self.die_animation[anim_index], False, False), self.rect)

    def process_input(self, dt) -> List[PlayerEvent]:
        if self.state == PlayerState.DYING or self.state == PlayerState.DEAD or self.is_pushed:
            return []
        keys = pygame.key.get_pressed()
        events = []
        if keys[pygame.K_w]:
            events.append(PlayerEvent(PlayerEventType.MOVE_UP, {"speed": self.speed}))
        if keys[pygame.K_a]:
            events.append(PlayerEvent(PlayerEventType.MOVE_LEFT, {"speed": self.speed}))
            self.is_looking_left = True
        if keys[pygame.K_s]:
            events.append(PlayerEvent(PlayerEventType.MOVE_DOWN, {"speed": self.speed}))
        if keys[pygame.K_d]:
            events.append(PlayerEvent(PlayerEventType.MOVE_RIGHT, {"speed": self.speed}))
            self.is_looking_left = False
        if keys[pygame.K_SPACE]:
            if self.to_next_bomb == 0:
                bomb = Bomb(x_pos=self.rect.centerx, y_pos=self.rect.centery,
                            sprite_scale=0.3, exp_range=self.bomb_explosion_range)
                self.to_next_bomb -= self.bomb_cooldown
                events.append(PlayerEvent(PlayerEventType.SPAWN_BOMB, {"bomb": bomb}))
        return events

    def check_if_exploded(self, exploded_tiles):
        for tile in exploded_tiles:
            if tile.rect.colliderect(self.rect):
                self.take_damage()
                break

    def take_damage(self):
        if self.state != PlayerState.ALIVE:
            return
        self.state = PlayerState.DYING
        self.health -= 1
        self.anim_count = 0

    def consume_bonus(self, bonus: Bonus):
        if bonus == BonusType.FLAMES:
            self.bomb_explosion_range += 1
        elif bonus == BonusType.SPEED:
            self.speed += 1
        elif bonus == BonusType.WALLPASS:
            self.is_ghost = True

    def be_observed(self, observer):
        observer.player_health = self.health
        observer.player_firepower = self.bomb_explosion_range
        observer.player_speed = self.speed
