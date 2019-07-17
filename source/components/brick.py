__author__ = 'marble_xu'

import pygame as pg
from .. import setup, tools
from .. import constants as c
from . import coin, stuff, powerup

def create_brick(brick_group, item, level):
    if c.COLOR in item:
        color = item[c.COLOR]
    else:
        color = c.COLOR_TYPE_ORANGE

    x, y, type = item['x'], item['y'], item['type']
    if type == c.TYPE_COIN:
        brick_group.add(Brick(x, y, type, 
                    color, level.coin_group))
    elif (type == c.TYPE_STAR or
        type == c.TYPE_FIREFLOWER or
        type == c.TYPE_LIFEMUSHROOM):
        brick_group.add(Brick(x, y, type,
                    color, level.powerup_group))
    else:
        if c.BRICK_NUM in item:
            create_brick_list(brick_group, item[c.BRICK_NUM], x, y, type,
                        color, item['direction'])
        else:
            brick_group.add(Brick(x, y, type, color))
            
            
def create_brick_list(brick_group, num, x, y, type, color, direction):
    ''' direction:horizontal, create brick from left to right, direction:vertical, create brick from up to bottom '''
    size = 43 # 16 * c.BRICK_SIZE_MULTIPLIER is 43
    tmp_x, tmp_y = x, y
    for i in range(num):
        if direction == c.VERTICAL:
            tmp_y = y + i * size
        else:
            tmp_x = x + i * size
        brick_group.add(Brick(tmp_x, tmp_y, type, color))
        
class Brick(stuff.Stuff):
    def __init__(self, x, y, type, color=c.ORANGE, group=None, name=c.MAP_BRICK):
        orange_rect = [(16, 0, 16, 16), (432, 0, 16, 16)]
        green_rect = [(208, 32, 16, 16), (48, 32, 16, 16)]
        if color == c.COLOR_TYPE_ORANGE:
            frame_rect = orange_rect
        else:
            frame_rect = green_rect
        stuff.Stuff.__init__(self, x, y, setup.GFX['tile_set'],
                        frame_rect, c.BRICK_SIZE_MULTIPLIER)

        self.rest_height = y
        self.state = c.RESTING
        self.y_vel = 0
        self.gravity = 1.2
        self.type = type
        if self.type == c.TYPE_COIN:
            self.coin_num = 10
        else:
            self.coin_num = 0
        self.group = group
        self.name = name
    
    def update(self):
        if self.state == c.BUMPED:
            self.bumped()
    
    def bumped(self):
        self.rect.y += self.y_vel
        self.y_vel += self.gravity
        
        if self.rect.y >= self.rest_height:
            self.rect.y = self.rest_height
            if self.type == c.TYPE_COIN:
                if self.coin_num > 0:
                    self.state = c.RESTING
                else:
                    self.state = c.OPENED
            elif self.type == c.TYPE_STAR:
                self.state = c.OPENED
                self.group.add(powerup.Star(self.rect.centerx, self.rest_height))
            elif self.type == c.TYPE_FIREFLOWER:
                self.state = c.OPENED
                self.group.add(powerup.FireFlower(self.rect.centerx, self.rest_height))
            elif self.type == c.TYPE_LIFEMUSHROOM:
                self.state = c.OPENED
                self.group.add(powerup.LifeMushroom(self.rect.centerx, self.rest_height))
            else:
                self.state = c.RESTING
        
    def start_bump(self, score_group):
        self.y_vel -= 7
        
        if self.type == c.TYPE_COIN:
            if self.coin_num > 0:
                self.group.add(coin.Coin(self.rect.centerx, self.rect.y, score_group))
                self.coin_num -= 1
                if self.coin_num == 0:
                    self.frame_index = 1
                    self.image = self.frames[self.frame_index]
        elif (self.type == c.TYPE_STAR or 
            self.type == c.TYPE_FIREFLOWER or 
            self.type == c.TYPE_LIFEMUSHROOM):
            self.frame_index = 1
            self.image = self.frames[self.frame_index]
        
        self.state = c.BUMPED
    
    def change_to_piece(self, group):
        arg_list = [(self.rect.x, self.rect.y - (self.rect.height/2), -2, -12),
                    (self.rect.right, self.rect.y - (self.rect.height/2), 2, -12),
                    (self.rect.x, self.rect.y, -2, -6),
                    (self.rect.right, self.rect.y, 2, -6)]
        
        for arg in arg_list:
            group.add(BrickPiece(*arg))
        self.kill()
        
class BrickPiece(stuff.Stuff):
    def __init__(self, x, y, x_vel, y_vel):
        stuff.Stuff.__init__(self, x, y, setup.GFX['tile_set'],
            [(68, 20, 8, 8)], c.BRICK_SIZE_MULTIPLIER)
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.gravity = .8
    
    def update(self, *args):
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel
        self.y_vel += self.gravity
        if self.rect.y > c.SCREEN_HEIGHT:
            self.kill()
    
