from enemy import Enemy
from game_field import GameField
from pygame import image, transform


class Ancient(Enemy):
    def __init__(self, pos, game_field: GameField, field_id: (int, int), player, sprite_scale=1):
        super().__init__()
        self.game_field = game_field
        self.player = player
        self.field_id = field_id
        self.paths_to_sprites = ["Sprites/Enemies/Ancient/loop1.png",
                                 "Sprites/Enemies/Ancient/loop2.png",
                                 "Sprites/Enemies/Ancient/loop3.png",
                                 "Sprites/Enemies/Ancient/loop4.png",
                                 "Sprites/Enemies/Ancient/loop5.png"]
        self.image = image.load(self.paths_to_sprites[0])
        self.image = transform.scale(self.image, (int(self.image.get_width() * sprite_scale),
                                                  int(self.image.get_height() * sprite_scale)))
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.speed = 5
        self.repeat_animation = []
        for path in self.paths_to_sprites:
            anim_p = image.load(path)
            anim_p = transform.scale(anim_p, (int(anim_p.get_width() * sprite_scale),
                                              int(anim_p.get_height() * sprite_scale)))
            self.repeat_animation.append(anim_p)
        self.anim_count = 0
        self.health = 2
        self.is_looking_left = False

    def draw(self, screen):
        anim_index = self.anim_count // 6
        if anim_index < len(self.repeat_animation) - 1:
            self.anim_count += 1
        else:
            self.anim_count = 0
        screen.blit(transform.flip(self.repeat_animation[anim_index], self.is_looking_left, False), self.rect)
