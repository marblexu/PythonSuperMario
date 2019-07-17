__author__ = 'marble_xu'

import pygame as pg
from .. import setup, tools
from .. import constants as c
from . import coin, powerup

class Box(pg.sprite.Sprite):
    def __init__(self, x, y, type, group=None, name=c.MAP_BOX):
        pg.sprite.Sprite.__init__(self)
        
        self.frames = []
        self.frame_index = 0
        self.load_frames()
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.rest_height = y
        self.animation_timer = 0
        self.first_half = True   # First half of animation cycle
        self.state = c.RESTING
        self.y_vel = 0
        self.gravity = 1.2
        self.type = type
        self.group = group
        self.name = name
        
    def load_frames(self):
        sheet = setup.GFX['tile_set']
        frame_rect_list = [(384, 0, 16, 16), (400, 0, 16, 16), 
            (416, 0, 16, 16), (400, 0, 16, 16), (432, 0, 16, 16)]
        for frame_rect in frame_rect_list:
            self.frames.append(tools.get_image(sheet, *frame_rect, 
                            c.BLACK, c.BRICK_SIZE_MULTIPLIER))
    
    def update(self, game_info):
        self.current_time = game_info[c.CURRENT_TIME]
        if self.state == c.RESTING:
            self.resting()
        elif self.state == c.BUMPED:
            self.bumped()

    def resting(self):
        time_list = [375, 125, 125, 125]
        if (self.current_time - self.animation_timer) > time_list[self.frame_index]:
            self.frame_index += 1
            if self.frame_index == 4:
                self.frame_index = 0
            self.animation_timer = self.current_time

        self.image = self.frames[self.frame_index]
    
    def bumped(self):
        self.rect.y += self.y_vel
        self.y_vel += self.gravity
        
        if self.rect.y > self.rest_height + 5:
            self.rect.y = self.rest_height
            self.state = c.OPENED
            if self.type == c.TYPE_MUSHROOM:
                self.group.add(powerup.Mushroom(self.rect.centerx, self.rect.y))
            elif self.type == c.TYPE_FIREFLOWER:
                self.group.add(powerup.FireFlower(self.rect.centerx, self.rect.y))
            elif self.type == c.TYPE_LIFEMUSHROOM:
                self.group.add(powerup.LifeMushroom(self.rect.centerx, self.rect.y))
        self.frame_index = 4
        self.image = self.frames[self.frame_index]
    
    def start_bump(self, score_group):
        self.y_vel = -6
        self.state = c.BUMPED
        
        if self.type == c.TYPE_COIN:
            self.group.add(coin.Coin(self.rect.centerx, self.rect.y, score_group))
