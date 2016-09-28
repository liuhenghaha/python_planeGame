# coding: utf-8

import pygame


class MyPlane(pygame.sprite.Sprite):
    def __init__(self, bg_size):
        pygame.sprite.Sprite.__init__(self)
        self.image1 = pygame.image.load("image/hero1.png")
        self.image2 = pygame.image.load("image/hero2.png")
        self.rect = self.image1.get_rect()
        self.width, self.height = bg_size[0], bg_size[1]
        self.rect.left, self.rect.top = (self.width - self.rect.width) // 2, (self.height - self.rect.height - 60)
        # 掩膜碰撞检测
        self.mask = pygame.mask.from_surface(self.image1)
        self.speed = 10
        self.active = True
        # 无敌
        self.invincible = False
        # 损毁
        self.destroy_images = []
        self.destroy_images.extend([pygame.image.load("image/hero_blowup_n1.png"),
                                    pygame.image.load("image/hero_blowup_n2.png"),
                                    pygame.image.load("image/hero_blowup_n3.png"),
                                    pygame.image.load("image/hero_blowup_n4.png")])

    def move_up(self):
        if self.rect.top > 0:
            self.rect.top -= self.speed
        else:
            self.rect.top = 0

    def move_down(self):
        if self.rect.bottom < self.height - 60:
            self.rect.top += self.speed
        else:
            self.rect.bottom = self.height - 60

    def move_left(self):
        if self.rect.left > 0:
            self.rect.left -= self.speed
        else:
            self.rect.left = 0

    def move_right(self):
        if self.rect.right < self.width:
            self.rect.right += self.speed
        else:
            self.rect.right = self.width

    def reset(self):
        self.rect.left, self.rect.top = (self.width - self.rect.width) // 2, (self.height - self.rect.height - 60)
        self.active = True
        self.invincible = True
