import random
import math
from pgzero.builtins import *

WIDTH = 1024
HEIGHT = 768

loadGameEvironment = False
musicOn = True

music.play('music.wav')
music.set_volume(0.05)

class Background:
    def __init__(self, sky_background, ground_background, sky_speed, ground_speed):
        self.sky_background = sky_background
        self.ground_background = ground_background
        self.sky_speed = sky_speed
        self.ground_speed = ground_speed

    def draw_background(self):
        for sky in self.sky_background:
            sky.draw()
        for ground in self.ground_background:
            ground.draw()
    
    def update_background(self):
        for sky in self.sky_background:
            sky.x -= self.sky_speed

            if sky.x <= -images.background.sky.get_width():
                sky.x += images.background.sky.get_width() * 4

        for ground in self.ground_background:
            ground.x -= self.ground_speed

            if ground.x <= -images.background.desert.get_width():
                ground.x += images.background.desert.get_width() * 4

class Platform:
    def __init__(self, platform_size, topleft_coordinate):
        self.platform_size = platform_size
        self.topleft_coordinate = topleft_coordinate
        self.platform_actors = []

        self.platform_actors.append(Actor('platform/terrain_sand_cloud_left', topleft=(self.topleft_coordinate)))

        for i in range(1 ,platform_size - 1):
            self.platform_actors.append(Actor('platform/terrain_sand_cloud_middle', topleft=(self.topleft_coordinate[0] + 32 * i, self.topleft_coordinate[1])))

        self.platform_actors.append(Actor('platform/terrain_sand_cloud_right', topleft=(self.topleft_coordinate[0] + 32 * (self.platform_size - 1), self.topleft_coordinate[1])))


class Terrain:
    def __init__(self, ground, platforms):
        self.ground = ground
        self.platforms = platforms
    
    def draw_terrain(self):
        for ground_piece in self.ground:
            ground_piece.draw()

        for platform in self.platforms:
            for platform_piece in platform.platform_actors:
                platform_piece.draw()

class Menu:
    def __init__(self, play_button, music_button, quit_button, menu_visible, music):
        self.play_button = play_button
        self.music_button = music_button
        self.quit_button = quit_button
        self.menu_visible = menu_visible
        self.music = music

    def on_mouse_down_menu(self, pos):
        if self.play_button.collidepoint(pos) and self.menu_visible:
            self.menu_visible = False

        elif self.music_button.collidepoint(pos) and self.menu_visible and self.music:
            music.set_volume(0)
            self.music = False
            self.music_button.image = 'menu/audiooff'

        elif self.music_button.collidepoint(pos) and self.menu_visible and not self.music:
            music.set_volume(0.2)
            self.music = True
            self.music_button.image = 'menu/audioon'

        elif self.quit_button.collidepoint(pos) and self.menu_visible:
            exit()

    def draw_menu(self):
        if self.menu_visible:
            self.play_button.draw()
            self.music_button.draw()
            self.quit_button.draw()

class Player:
    def __init__(self, standing_animation, walking_animation, hurt_animation, ducking_animation, jumping_animation, start_position):
        self.standing_animation = standing_animation
        self.walking_animation = walking_animation
        self.hurt_animation = hurt_animation
        self.ducking_animation = ducking_animation
        self.jumping_animation = jumping_animation
        self.actor = Actor(self.standing_animation[0], start_position)
        self.vertical_speed = 0
        self.on_ground = True
        self.ducking = False
        self.horizontal_speed = 3
        self.moving = False
        self.anim_index = 0
        self.anim_timer = 0
        self.gravity = 0.5
        self.jump_strength = -9 
        self.super_jump_strength = -12  
        self.max_fall_speed = 15

    def update_player(self):
        self.vertical_speed += self.gravity
        if self.vertical_speed > self.max_fall_speed:
            self.vertical_speed = self.max_fall_speed
            
        self.actor.y += self.vertical_speed
        
        if self.actor.y >= 674: 
            self.actor.y = 674
            self.vertical_speed = 0
            self.on_ground = True
        else:
            self.on_ground = False

        if self.actor.x <= 32:
            self.actor.x = 32

        elif self.actor.x >= 992:
            self.actor.x = 992
         
        for platform in platforms:
            for platform_piece in platform.platform_actors:
                collision_left = platform_piece.left + 20
                collision_right = platform_piece.right - 20
                collision_top = platform_piece.top
                collision_bottom = platform_piece.bottom
                
                if (self.actor.left < collision_right and 
                    self.actor.right > collision_left):
                    
                    if (self.vertical_speed > 0 and 
                        self.actor.bottom >= collision_top and 
                        self.actor.bottom <= collision_top + 15):
                        self.actor.y = collision_top - 30
                        self.vertical_speed = 0
                        self.on_ground = True
                        break

        self.moving = False
        self.ducking = False
        
        if keyboard.down and self.on_ground:
            self.ducking = True
            self.moving = False
        else:
            if keyboard.right:
                self.actor.x += self.horizontal_speed
                self.moving = True

            elif keyboard.left:
                self.actor.x -= self.horizontal_speed
                self.moving = True

        if (keyboard.up or keyboard.space) and self.on_ground:
            if self.ducking:
                self.vertical_speed = self.super_jump_strength
                
            else:
                self.vertical_speed = self.jump_strength
            self.on_ground = False
            self.ducking = False

        for silver_coin in coins.silver_coins:
            if (silver_coin.visible and self.actor.colliderect(silver_coin.coin) and not silver_coin.collected):
                silver_coin.collected = True
                silver_coin.visible = False
                sounds.sfx_coin.play()
        
        if (coins.gold_coin.visible and self.actor.colliderect(coins.gold_coin.coin) and not coins.gold_coin.collected):
            coins.gold_coin.collected = True
            coins.gold_coin.visible = False
            sounds.sfx_coin.play()
            reset_game()

        for enemy in enemies.enemies:
            if self.actor.colliderect(enemy.actor):
                reset_game()

        self.anim_timer += 1
        if self.anim_timer >= 10:
            self.anim_timer = 0
            self.anim_index += 1

            if self.ducking:
                self.anim_index %= len(self.ducking_animation)
                self.actor.image = self.ducking_animation[self.anim_index]
            elif self.moving:
                self.anim_index %= len(self.walking_animation)
                self.actor.image = self.walking_animation[self.anim_index]
            else:
                self.anim_index %= len(self.standing_animation)
                self.actor.image = self.standing_animation[self.anim_index]

    def draw_player(self):
        self.actor.draw()

class Enemy:
    def __init__(self, walking_animation, start_position, min_x, max_x, speed):
        self.walking_animation = walking_animation
        self.actor = Actor(self.walking_animation[0], start_position)
        self.facing_right = False
        self.anim_index = 0
        self.anim_timer = 0
        self.min_x = min_x
        self.max_x = max_x
        self.speed = speed


    def update_enemy(self):
        if self.facing_right:
            self.actor.x += self.speed
            if self.actor.x >= self.max_x:
                self.facing_right = False
        else:
            self.actor.x -= self.speed
            if self.actor.x <= self.min_x:
                self.facing_right = True

        self.anim_timer += 1
        if self.anim_timer >= 14:
            self.anim_timer = 0
            self.anim_index += 1
            self.anim_index %= len(self.walking_animation)
            self.actor.image = self.walking_animation[self.anim_index]

    def draw_enemy(self):
        self.actor.draw()

class Enemies:
    def __init__(self, enemies):
        self.enemies = enemies

    def update_enemies(self):
        for enemy in self.enemies:
            enemy.update_enemy()

    def draw_enemies(self):
        for enemy in self.enemies:
                enemy.draw_enemy()

class Coin:
    def __init__(self, is_silver, topleft_coordinate):
        self.is_silver = is_silver
        self.topleft_coordinate = topleft_coordinate
        self.collected = False

        if self.is_silver:
            self.coin = Actor('coins/coin_silver', topleft=(self.topleft_coordinate))
            self.animation = [
                'coins/coin_silver',
                'coins/coin_silver_side'
            ]
            self.visible = True

        else:
            self.coin = Actor('coins/coin_gold', topleft=(self.topleft_coordinate))
            self.animation = [
                'coins/coin_gold',
                'coins/coin_gold_side'
            ]
            self.visible = False


class Coins:
    def __init__(self, silver_coins, gold_coin):
        self.silver_coins = silver_coins
        self.gold_coin = gold_coin
        self.anim_timer = 0
        self.anim_index = 0
    
    def update_coins(self):
        self.anim_timer += 1
        if self.anim_timer >= 10:
            self.anim_timer = 0
            self.anim_index += 1
            self.anim_index %= 2

            self.gold_coin.coin.image = self.gold_coin.animation[self.anim_index]

            for silver_coin in self.silver_coins:
                silver_coin.coin.image = silver_coin.animation[self.anim_index]

            
    def draw_coins(self):
        all_silver_collected = True

        for silver_coin in self.silver_coins:
            if silver_coin.visible:
                silver_coin.coin.draw()
            if not silver_coin.collected:
                all_silver_collected = False
        
        if all_silver_collected and not self.gold_coin.collected:
            self.gold_coin.visible = True
            self.gold_coin.coin.draw()


## CREATING BACKGROUND ##
bgSky = []
for i in range(4):
    bgSky.append(
        Actor('background/sky', topleft=(images.background.sky.get_width() * i, -images.background.sky.get_height()/2 + 50))
    )

bgGround = []
for i in range(4):
    bgGround.append(
        Actor('background/desert', topleft=(images.background.desert.get_width() * i, images.background.sky.get_height()/2 + 50))
    )

background = Background(
    bgSky,
    bgGround,
    sky_speed = 1.5,
    ground_speed = 0.5
)

## CREATING TERRAIN ##

ground = []
ground.append(Actor('platform/terrain_sand_block_left', topleft=(0,736)))

for i in range(30):
    ground.append(Actor('platform/terrain_sand_block_center', topleft=(32 + 32*i,736)))

ground.append(Actor('platform/terrain_sand_block_right', topleft=(992,736)))

ground.append(Actor('platform/terrain_sand_block_top_left', topleft=(0,704)))

for i in range(30):
    ground.append(Actor('platform/terrain_sand_block_top', topleft=(32 + 32*i,704)))

ground.append(Actor('platform/terrain_sand_block_top_right', topleft=(992,704)))


platforms = []

platform_one = Platform(
    platform_size = 5,
    topleft_coordinate = (180,572)
)

platform_two = Platform(
    platform_size = 4,
    topleft_coordinate = (690,572)
)

platform_three = Platform(
    platform_size = 7,
    topleft_coordinate = (400,472)
)

platform_four = Platform(
    platform_size = 3,
    topleft_coordinate = (690,372)
)

platform_five = Platform(
    platform_size = 2,
    topleft_coordinate = (900,422)
)

platform_six = Platform(
    platform_size = 9,
    topleft_coordinate = (60,372)
)

platform_seven = Platform(
    platform_size = 3,
    topleft_coordinate = (400,272)
)

platform_eight = Platform(
    platform_size = 5,
    topleft_coordinate = (170,222)
)

platform_nine = Platform(
    platform_size = 2,
    topleft_coordinate = (50,122)
)

platform_ten = Platform(
    platform_size = 9,
    topleft_coordinate = (560,172)
)

platform_eleven = Platform(
    platform_size = 2,
    topleft_coordinate = (940,72)
)

platforms = [
    platform_one,
    platform_two,
    platform_three,
    platform_four,
    platform_five,
    platform_six,
    platform_seven,
    platform_eight,
    platform_nine,
    platform_ten,
    platform_eleven
]

terrain = Terrain(
    ground,
    platforms
)

## CREATING MENU ##
menu = Menu(
    play_button = Actor('menu/buttonstart', topleft=(312, 334)),
    music_button = Actor('menu/audioon', topleft=(462, 334)),
    quit_button = Actor('menu/exit', topleft=(612, 334)),
    menu_visible = True,
    music = True
)

## CREATING PLAYER ##
player = Player(
    standing_animation = ['player/character_yellow_idle', 'player/character_yellow_front'],
    walking_animation = ['player/character_yellow_walk_a', 'player/character_yellow_walk_b'],
    hurt_animation = ['player/character_yellow_hit'],
    ducking_animation = ['player/character_yellow_duck'],
    jumping_animation = ['player/character_yellow_jump'],
    start_position = (100, 700)
)

## CREATUBG ENEMY ##

enemy_one = Enemy(
    walking_animation = ['enemy/snail_walk_a', 'enemy/snail_walk_b'],
    start_position = (200,356),
    min_x = 72,
    max_x = 340,
    speed = 1.5
)

enemy_two = Enemy(
    walking_animation = ['enemy/snail_walk_a', 'enemy/snail_walk_b'],
    start_position = (200,208),
    min_x = 184,
    max_x = 312,
    speed = 1.5
)

enemy_three = Enemy(
    walking_animation = ['enemy/snail_walk_a', 'enemy/snail_walk_b'],
    start_position = (500,456),
    min_x = 412,
    max_x = 612,
    speed = 1.5
)

enemy_four = Enemy(
    walking_animation = ['enemy/snail_walk_a', 'enemy/snail_walk_b'],
    start_position = (572,156),
    min_x = 572,
    max_x = 832,
    speed = 1.5
)

enemy_five = Enemy(
    walking_animation = ['enemy/snail_walk_a', 'enemy/snail_walk_b'],
    start_position = (832,156),
    min_x = 572,
    max_x = 832,
    speed = 1.5
)

enemies = Enemies(
    enemies = [
        enemy_one,
        enemy_two,
        enemy_three,
        enemy_four,
        enemy_five
    ]
)

## CREATING COINS ##

coin_one = Coin(
    is_silver = True,
    topleft_coordinate = (180, 536)
)

coin_two = Coin(
    is_silver = True,
    topleft_coordinate = (690, 536)
)

coin_three = Coin(
    is_silver = True,
    topleft_coordinate = (932, 390)
)

coin_four = Coin(
    is_silver = True,
    topleft_coordinate = (50, 90)
)

coin_five = Coin(
    is_silver = True,
    topleft_coordinate = (496, 360)
)

coin_six = Coin(
    is_silver = True,
    topleft_coordinate = (60, 330)
)

coin_seven = Coin(
    is_silver = True,
    topleft_coordinate = (188, 266)
)

coin_eight = Coin(
    is_silver = True,
    topleft_coordinate = (624, 76)
)

coin_nine = Coin(
    is_silver = True,
    topleft_coordinate = (752, 76)
)

silver_coins = [
    coin_one,
    coin_two,
    coin_three,
    coin_four,
    coin_five,
    coin_six,
    coin_seven,
    coin_eight,
    coin_nine
]

gold_coin = Coin(
    is_silver = False,
    topleft_coordinate = (944, 16)
)

coins = Coins(
    silver_coins = silver_coins,
    gold_coin = gold_coin
)

## 

def reset_game():
    global player, coins, menu

    player.actor.pos = (100, 700)
    player.vertical_speed = 0
    player.on_ground = True
    player.ducking = False
    player.moving = False
    player.anim_index = 0
    player.anim_timer = 0

    for silver_coin in coins.silver_coins:
        silver_coin.collected = False
        silver_coin.visible = True
        silver_coin.coin.image = silver_coin.animation[0]

    coins.gold_coin.collected = False
    coins.gold_coin.visible = False
    coins.gold_coin.coin.image = coins.gold_coin.animation[0]
    
    coins.anim_timer = 0
    coins.anim_index = 0
    
    menu.menu_visible = True

def update():
    background.update_background()
    if not menu.menu_visible:
        player.update_player()
        coins.update_coins()
        enemies.update_enemies()

def on_mouse_down(pos):
    menu.on_mouse_down_menu(pos)

def draw():
    background.draw_background()
    terrain.draw_terrain()

    if not menu.menu_visible:
        player.draw_player()
        coins.draw_coins()
        enemies.draw_enemies()
    menu.draw_menu()
