# coding: utf-8

from __future__ import division # 该语句必须放在文件开头
import pygame
import sys
import traceback
from random import *
from pygame.locals import *

import myplane
import enemy
import bullet
import supply

# ========= 初始化 ==========
pygame.init()
pygame.mixer.init()  # 混音器初始化
bg_size = width, height = 480, 852  # 设计背景尺寸
screen = pygame.display.set_mode(bg_size)  # 设置背景对话框
pygame.display.set_caption("飞机大战……FishC Demo")
background = pygame.image.load("image/background.png")  # 加载背景图片,并设置为不透明

# ========== 载入游戏音乐 ====================
pygame.mixer.music.load("sound/game_music.wav")
pygame.mixer.music.set_volume(0.2)
bullet_sound = pygame.mixer.Sound("sound/bullet.wav")
bullet_sound.set_volume(0.2)
big_enemy_flying_sound = pygame.mixer.Sound("sound/big_spaceship_flying.wav")
big_enemy_flying_sound.set_volume(0.2)
enemy1_down_sound = pygame.mixer.Sound("sound/enemy1_down.wav")
enemy1_down_sound.set_volume(0.2)
enemy2_down_sound = pygame.mixer.Sound("sound/enemy2_down.wav")
enemy2_down_sound.set_volume(0.2)
enemy3_down_sound = pygame.mixer.Sound("sound/enemy3_down.wav")
enemy3_down_sound.set_volume(0.2)
me_down_sound = pygame.mixer.Sound("sound/game_over.wav")
me_down_sound.set_volume(0.2)
button_down_sound = pygame.mixer.Sound("sound/button.wav")
button_down_sound.set_volume(0.2)
level_up_sound = pygame.mixer.Sound("sound/achievement.wav")
level_up_sound.set_volume(0.2)
bomb_sound = pygame.mixer.Sound("sound/use_bomb.wav")
bomb_sound.set_volume(0.2)
get_bomb_sound = pygame.mixer.Sound("sound/get_bomb.wav")
get_bomb_sound.set_volume(0.2)
get_bullet_sound = pygame.mixer.Sound("sound/get_double_laser.wav")
get_bullet_sound.set_volume(0.2)


# =======敌方飞机生成函数=======
def add_small_enemy(group1, group2, num):
    for i in range(num):
        e1 = enemy.SmallEnemy(bg_size)
        group1.add(e1)
        group2.add(e1)


def add_mid_enemy(group1, group2, num):
    for i in range(num):
        e2 = enemy.MidEnemy(bg_size)
        group1.add(e2)
        group2.add(e2)


def add_big_enemy(group1, group2, num):
    for i in range(num):
        e3 = enemy.BigEnemy(bg_size)
        group1.add(e3)
        group2.add(e3)


def inc_speed(target, inc):
    for each in target:
        each.speed += inc


def main():
    pygame.mixer.music.play(-1)
    running = True

    # 初始化我的飞机
    me = myplane.MyPlane(bg_size)

    # 初始化生命值
    life_image = pygame.image.load("image/life.png")
    life_rect = life_image.get_rect()
    life_num = 3

    # 实例化敌方飞机
    enemies = pygame.sprite.Group()
    small_enemies = pygame.sprite.Group()
    add_small_enemy(small_enemies, enemies, 1)
    mid_enemies = pygame.sprite.Group()
    add_mid_enemy(mid_enemies, enemies, 1)
    big_enemies = pygame.sprite.Group()
    add_big_enemy(big_enemies, enemies, 1)

    # 实例化强化武器
    bullet_supply = supply.BulletSupply(bg_size)
    bomb_supply = supply.BombSupply(bg_size)

    # 帧率
    clock = pygame.time.Clock()

    # 控制飞机图片切换 --模拟喷火
    switch_image = False
    delay = 60

    # 飞机损毁图像索引
    e1_destroy_index = 0
    e2_destroy_index = 0
    e3_destroy_index = 0
    me_destroy_index = 0

    # 生成普通子弹
    bullet1 = []
    bullet1_index = 0
    bullet1_num = 6
    for i in range(bullet1_num):
        bullet1.append(bullet.Bullet1(me.rect.midtop))

    # 生成超级子弹
    bullet2 = []
    bullet2_index = 0
    bullet2_num = 10
    for i in range(bullet2_num // 2):
        bullet2.append(bullet.Bullet2((me.rect.centerx - 33, me.rect.centery)))
        bullet2.append(bullet.Bullet2((me.rect.centerx + 30, me.rect.centery)))

    # 生成血槽
    color_black = (0, 0, 0)
    color_green = (0, 255, 0)
    color_red = (255, 0, 0)
    color_white = (255, 255, 255)

    # 统计得分
    score = 0

    # 显示字体
    score_font = pygame.font.SysFont("arial", 48)

    # 游戏难度
    level = 1

    # 初始化强化武器
    bomb_num = 3
    bomb_image = pygame.image.load("image/bomb.png")
    bomb_rect = bomb_image.get_rect()
    bomb_font = score_font
    is_double_bullet = False  # 超级子弹标志

    # 强化武器发放定时器
    supply_timer = USEREVENT
    pygame.time.set_timer(supply_timer, 10 * 1000)  # 10秒一次

    # 超级子弹限时器
    double_bullet_timer = USEREVENT + 1

    # 无敌定时器
    invincible_time = USEREVENT + 2

    # 暂停
    paused = False
    pause_nor_image = pygame.image.load("image/game_pause_nor.png")
    pause_pressed_image = pygame.image.load("image/game_pause_pressed.png")
    resume_nor_image = pygame.image.load("image/game_resume_nor.png")
    resume_pressed_image = pygame.image.load("image/game_resume_pressed.png")
    paused_rect = pause_nor_image.get_rect()
    paused_rect.left, paused_rect.top = width - paused_rect.width - 10, 10
    paused_image = pause_nor_image

    # game over
    gameover_image = pygame.image.load("image/game_over.png")
    gameover_rect = gameover_image.get_rect()

    # 是否存储最高分
    flag_recorded = False
    
    while running:
        clock.tick(60)
        screen.blit(background, (0, 0))
        score_text = score_font.render("Score : %s" % str(score), True, color_white)
        screen.blit(score_text, (10, 5))
        screen.blit(paused_image, paused_rect)

        if life_num and not paused:
        
            # 游戏难度递增操作
            if level == 1 and score > 5000:
                level = 2
                level_up_sound.play()
                add_small_enemy(small_enemies, enemies, 3)
                add_mid_enemy(mid_enemies, enemies, 2)
                add_big_enemy(big_enemies, enemies, 1)
                inc_speed(small_enemies, 1)
            elif level == 2 and score > 30000:
                level = 3
                level_up_sound.play()
                add_small_enemy(small_enemies, enemies, 3)
                add_mid_enemy(mid_enemies, enemies, 2)
                add_big_enemy(big_enemies, enemies, 1)
                inc_speed(small_enemies, 1)
                inc_speed(mid_enemies, 1)
            elif level == 3 and score > 60000:
                level = 4
                level_up_sound.play()
                add_small_enemy(small_enemies, enemies, 3)
                add_mid_enemy(mid_enemies, enemies, 2)
                add_big_enemy(big_enemies, enemies, 1)
                inc_speed(small_enemies, 1)
                inc_speed(mid_enemies, 1)
                inc_speed(big_enemies, 1)

            # 绘制强化武器数量和剩余生命数量
            bomb_text = bomb_font.render("* %d" % bomb_num, True, color_black)
            bomb_text_rect = bomb_text.get_rect()
            screen.blit(bomb_image, (10, height - 10 - bomb_rect.height))
            screen.blit(bomb_text, (20 + bomb_rect.width, height - 10 - bomb_text_rect.height))
            for i in range(life_num):
                screen.blit(life_image, (width - 10 - (i + 1) * life_rect.width, height - 10 - life_rect.height))
    
            if me.active:
                if switch_image:
                    screen.blit(me.image1, me.rect)
                else:
                    screen.blit(me.image2, me.rect)
            else:
                if not delay % 3:
                    screen.blit(me.destroy_images[me_destroy_index], me.rect)
                    me_destroy_index = (me_destroy_index + 1) % 4
                    if me_destroy_index == 0:
                        me_down_sound.play()
                        life_num -= 1
                        me.reset()
                        pygame.time.set_timer(invincible_time, 3 * 1000)

            if not (delay % 10):
                bullet_sound.play()
                if not is_double_bullet:
                    bullets = bullet1
                    bullets[bullet1_index].reset(me.rect.midtop)
                    bullet1_index = (bullet1_index + 1) % bullet1_num
                else:
                    bullets = bullet2
                    bullets[bullet2_index].reset((me.rect.centerx - 33, me.rect.centery))
                    bullets[bullet2_index + 1].reset((me.rect.centerx + 30, me.rect.centery))
                    bullet2_index = (bullet2_index + 2) % bullet2_num

            for each in small_enemies:
                if each.active:
                    each.move()
                    screen.blit(each.image, each.rect)
                else:
                    if e1_destroy_index == 0:
                        enemy1_down_sound.play()
                    if not (delay % 3):
                        screen.blit(each.destroy_images[e1_destroy_index], each.rect)
                        e1_destroy_index = (e1_destroy_index + 1) % 4
                        if e1_destroy_index == 0:
                            score += 500
                            each.reset()

            for each in mid_enemies:
                if each.active:
                    each.move()
                    if not each.hit:
                        screen.blit(each.image, each.rect)
                    else:
                        screen.blit(each.image_hit, each.rect)
                        each.hit = False
                    # 绘制血槽
                    pygame.draw.line(screen, color_black, (each.rect.left, each.rect.top - 5), (each.rect.right, each.rect.top - 5), 2)
                    energy_remain = each.energy / enemy.MidEnemy.energy
                    if energy_remain > 0.2:
                        energy_color = color_green
                    else:
                        energy_color = color_red
                    pygame.draw.line(screen, energy_color, (each.rect.left, each.rect.top - 5), (each.rect.left + each.rect.width * energy_remain, each.rect.top - 5),2)
                else:
                    if e2_destroy_index == 0:
                        enemy2_down_sound.play()
                    if not (delay % 3):
                        screen.blit(each.destroy_images[e2_destroy_index], each.rect)
                        e2_destroy_index = (e2_destroy_index + 1) % 4
                        if e2_destroy_index == 0:
                            score += 2000
                            each.reset()
                                
            for each in big_enemies:
                if each.active:
                    each.move()
                    if not each.hit:
                        if switch_image:
                            screen.blit(each.image1, each.rect)
                        else:
                            screen.blit(each.image2, each.rect)
                        if each.rect.bottom == -50:
                            big_enemy_flying_sound.play(-1)
                    else:
                        screen.blit(each.image_hit, each.rect)
                        each.hit = False
                    # 绘制血槽
                    pygame.draw.line(screen, color_black, (each.rect.left, each.rect.top - 5), (each.rect.right, each.rect.top - 5), 2)
                    energy_remain = each.energy / enemy.BigEnemy.energy
                    if energy_remain > 0.2:
                        energy_color = color_green
                    else:
                        energy_color = color_red
                    pygame.draw.line(screen,energy_color,(each.rect.left, each.rect.top - 5), (each.rect.left + each.rect.width * energy_remain, each.rect.top - 5),2)
                    if each.rect.bottom == 0:
                        big_enemy_flying_sound.play(-1)
                else:
                    big_enemy_flying_sound.stop()
                    if e3_destroy_index == 0:
                        enemy3_down_sound.play()
                    if not (delay % 3):
                        screen.blit(each.destroy_images[e3_destroy_index], each.rect)
                        e3_destroy_index = (e3_destroy_index + 1) % 6
                        if e3_destroy_index == 0:
                            score += 6000
                            each.reset()

            for b in bullets:
                if b.active:
                    b.move()
                    screen.blit(b.image, b.rect)
                    enemies_hit = pygame.sprite.spritecollide(b, enemies, False, pygame.sprite.collide_mask)
                    if enemies_hit:
                        b.active = False
                        for e in enemies_hit:
                            if e in big_enemies or e in mid_enemies:
                                e.energy -= 1
                                e.hit = True
                                if e.energy == 0:
                                    e.active = False
                            else:
                                e.active = False

            # 绘制强化武器并检测是否获得
            if bomb_supply.active:
                bomb_supply.move()
                screen.blit(bomb_supply.image, bomb_supply.rect)
                if pygame.sprite.collide_mask(bomb_supply, me):
                    get_bomb_sound.play()
                    if bomb_num < 3:
                        bomb_num += 1
                    bomb_supply.active = False

            # 超级子弹包
            if bullet_supply.active:
                bullet_supply.move()
                screen.blit(bullet_supply.image, bullet_supply.rect)
                if pygame.sprite.collide_mask(bullet_supply, me):
                    get_bullet_sound.play()
                    is_double_bullet = True
                    bullet_supply.active = False
                    pygame.time.set_timer(double_bullet_timer, 18 * 1000)

            # 碰撞检测
            enemies_down = pygame.sprite.spritecollide(me, enemies, False, pygame.sprite.collide_mask)
            if enemies_down and not me.invincible:
                me.active = False
                for e in enemies_down:
                    e.active = False

            if not delay % 3:
                switch_image = not switch_image

        elif life_num == 0:
            screen.blit(gameover_image, gameover_rect)
            pygame.mixer.music.stop()
            pygame.mixer.stop()
            pygame.time.set_timer(supply_timer, 0)
            if not flag_recorded:
                flag_recorded = True
                with open ("score_record.txt", "r") as f:
                    record_score = int(f.read())
                if score > record_score:
                    with open("score_record.txt", "w") as f:
                        f.write(str(score))
            record_score_text = score_font.render("%d" % record_score, True, color_white)
            screen.blit(record_score_text, (150, 25))
            gameover_score_text = score_font.render("%d" % score, True, color_red)
            screen.blit(gameover_score_text, (180, 370))
        
        # 检测用户操作  
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                button_down_sound.play()
                if event.button == 1 and paused_rect.collidepoint(event.pos):
                    paused = not paused
                    if paused:
                        paused_image = resume_pressed_image
                        pygame.time.set_timer(supply_timer, 0)
                        pygame.mixer.music.pause()
                        pygame.mixer.pause()
                    else:
                        paused_image = pause_pressed_image
                        pygame.time.set_timer(supply_timer, 30 * 1000)
                        pygame.mixer.music.unpause()
                        pygame.mixer.unpause()
            elif event.type == MOUSEMOTION:
                if paused_rect.collidepoint(event.pos):
                    if paused:
                        paused_image = resume_pressed_image
                    else:
                        paused_image = pause_pressed_image
                else:
                    if paused:
                        paused_image = resume_nor_image
                    else:
                        paused_image = pause_nor_image
            elif event.type == invincible_time:
                me.invincible = False
                pygame.time.set_timer(invincible_time, 0)
            elif event.type == double_bullet_timer:
                is_double_bullet = False
                pygame.time.set_timer(double_bullet_timer, 0)
            elif event.type == supply_timer:
                if choice([True, False]):
                    bomb_supply.reset()
                else:
                    bullet_supply.reset()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    if bomb_num:
                        bomb_num -= 1
                        bomb_sound.play()
                        for each in enemies:
                            if each.rect.bottom > 0:
                                each.active = False

        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_w] or key_pressed[K_UP]:
            me.move_up()
        if key_pressed[K_s] or key_pressed[K_DOWN]:
            me.move_down()
        if key_pressed[K_a] or key_pressed[K_LEFT]:
            me.move_left()
        if key_pressed[K_d] or key_pressed[K_RIGHT]:
            me.move_right()

        if delay == 0:
            delay = 60
        delay -= 1

        pygame.display.flip()
        

if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        pass
    except:
        traceback.print_exc()
        pygame.quit()
        input()
