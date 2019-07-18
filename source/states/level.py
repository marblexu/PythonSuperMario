__author__ = 'marble_xu'

import os
import json
import pygame as pg
from .. import setup, tools
from .. import constants as c
from ..components import info, stuff, player, brick, box, enemy, powerup, coin


class Level(tools.State):
    def __init__(self):
        tools.State.__init__(self)
        self.player = None

    def startup(self, current_time, persist):
        self.game_info = persist
        self.persist = self.game_info
        self.game_info[c.CURRENT_TIME] = current_time
        self.death_timer = 0
        self.castle_timer = 0
        
        self.moving_score_list = []
        self.overhead_info = info.Info(self.game_info, c.LEVEL)
        self.load_map()
        self.setup_background()
        self.setup_maps()
        self.ground_group = self.setup_collide(c.MAP_GROUND)
        self.step_group = self.setup_collide(c.MAP_STEP)
        self.setup_pipe()
        self.setup_slider()
        self.setup_static_coin()
        self.setup_brick_and_box()
        self.setup_player()
        self.setup_enemies()
        self.setup_checkpoints()
        self.setup_flagpole()
        self.setup_sprite_groups()

    def load_map(self):
        map_file = 'level_' + str(self.game_info[c.LEVEL_NUM]) + '.json'
        file_path = os.path.join('source', 'data', 'maps', map_file)
        f = open(file_path)
        self.map_data = json.load(f)
        f.close()
        
    def setup_background(self):
        img_name = self.map_data[c.MAP_IMAGE]
        self.background = setup.GFX[img_name]
        self.bg_rect = self.background.get_rect()
        self.background = pg.transform.scale(self.background, 
                                    (int(self.bg_rect.width*c.BACKGROUND_MULTIPLER),
                                    int(self.bg_rect.height*c.BACKGROUND_MULTIPLER)))
        self.bg_rect = self.background.get_rect()

        self.level = pg.Surface((self.bg_rect.w, self.bg_rect.h)).convert()
        self.viewport = setup.SCREEN.get_rect(bottom=self.bg_rect.bottom)

    def setup_maps(self):
        self.map_list = []
        if c.MAP_MAPS in self.map_data:
            for data in self.map_data[c.MAP_MAPS]:
                self.map_list.append((data['start_x'], data['end_x'], data['player_x'], data['player_y']))
            self.start_x, self.end_x, self.player_x, self.player_y = self.map_list[0]
        else:
            self.start_x = 0
            self.end_x = self.bg_rect.w
            self.player_x = 110
            self.player_y = c.GROUND_HEIGHT
        
    def change_map(self, index, type):
        self.start_x, self.end_x, self.player_x, self.player_y = self.map_list[index]
        self.viewport.x = self.start_x
        if type == c.CHECKPOINT_TYPE_MAP:
            self.player.rect.x = self.viewport.x + self.player_x
            self.player.rect.bottom = self.player_y
            self.player.state = c.STAND
        elif type == c.CHECKPOINT_TYPE_PIPE_UP:
            self.player.rect.x = self.viewport.x + self.player_x
            self.player.rect.bottom = c.GROUND_HEIGHT
            self.player.state = c.UP_OUT_PIPE
            self.player.up_pipe_y = self.player_y
            
    def setup_collide(self, name):
        group = pg.sprite.Group()
        if name in self.map_data:
            for data in self.map_data[name]:
                group.add(stuff.Collider(data['x'], data['y'], 
                        data['width'], data['height'], name))
        return group

    def setup_pipe(self):
        self.pipe_group = pg.sprite.Group()
        if c.MAP_PIPE in self.map_data:
            for data in self.map_data[c.MAP_PIPE]:
                self.pipe_group.add(stuff.Pipe(data['x'], data['y'],
                    data['width'], data['height'], data['type']))

    def setup_slider(self):
        self.slider_group = pg.sprite.Group()
        if c.MAP_SLIDER in self.map_data:
            for data in self.map_data[c.MAP_SLIDER]:
                if c.VELOCITY in data:
                    vel = data[c.VELOCITY]
                else:
                    vel = 1
                self.slider_group.add(stuff.Slider(data['x'], data['y'], data['num'],
                    data['direction'], data['range_start'], data['range_end'], vel))

    def setup_static_coin(self):
        self.static_coin_group = pg.sprite.Group()
        if c.MAP_COIN in self.map_data:
            for data in self.map_data[c.MAP_COIN]:
                self.static_coin_group.add(coin.StaticCoin(data['x'], data['y']))

    def setup_brick_and_box(self):
        self.coin_group = pg.sprite.Group()
        self.powerup_group = pg.sprite.Group()
        self.brick_group = pg.sprite.Group()
        self.brickpiece_group = pg.sprite.Group()

        if c.MAP_BRICK in self.map_data:
            for data in self.map_data[c.MAP_BRICK]:
                brick.create_brick(self.brick_group, data, self)
        
        self.box_group = pg.sprite.Group()
        if c.MAP_BOX in self.map_data:
            for data in self.map_data[c.MAP_BOX]:
                if data['type'] == c.TYPE_COIN:
                    self.box_group.add(box.Box(data['x'], data['y'], data['type'], self.coin_group))
                else:
                    self.box_group.add(box.Box(data['x'], data['y'], data['type'], self.powerup_group))
            
    def setup_player(self):
        if self.player is None:
            self.player = player.Player(self.game_info[c.PLAYER_NAME])
        else:
            self.player.restart()
        self.player.rect.x = self.viewport.x + self.player_x
        self.player.rect.bottom = self.player_y
        if c.DEBUG:
            self.player.rect.x = self.viewport.x + c.DEBUG_START_X
            self.player.rect.bottom = c.DEBUG_START_y
        self.viewport.x = self.player.rect.x - 110

    def setup_enemies(self):
        self.enemy_group_list = []
        index = 0
        for data in self.map_data[c.MAP_ENEMY]:
            group = pg.sprite.Group()
            for item in data[str(index)]:
                group.add(enemy.create_enemy(item, self))
            self.enemy_group_list.append(group)
            index += 1
            
    def setup_checkpoints(self):
        self.checkpoint_group = pg.sprite.Group()
        for data in self.map_data[c.MAP_CHECKPOINT]:
            if c.ENEMY_GROUPID in data:
                enemy_groupid = data[c.ENEMY_GROUPID]
            else:
                enemy_groupid = 0
            if c.MAP_INDEX in data:
                map_index = data[c.MAP_INDEX]
            else:
                map_index = 0
            self.checkpoint_group.add(stuff.Checkpoint(data['x'], data['y'], data['width'], 
                data['height'], data['type'], enemy_groupid, map_index))
    
    def setup_flagpole(self):
        self.flagpole_group = pg.sprite.Group()
        if c.MAP_FLAGPOLE in self.map_data:
            for data in self.map_data[c.MAP_FLAGPOLE]:
                if data['type'] == c.FLAGPOLE_TYPE_FLAG:
                    sprite = stuff.Flag(data['x'], data['y'])
                    self.flag = sprite
                elif data['type'] == c.FLAGPOLE_TYPE_POLE:
                    sprite = stuff.Pole(data['x'], data['y'])
                else:
                    sprite = stuff.PoleTop(data['x'], data['y'])
                self.flagpole_group.add(sprite)
        
        
    def setup_sprite_groups(self):
        self.dying_group = pg.sprite.Group()
        self.enemy_group = pg.sprite.Group()
        self.shell_group = pg.sprite.Group()
        
        self.ground_step_pipe_group = pg.sprite.Group(self.ground_group,
                        self.pipe_group, self.step_group, self.slider_group)
        self.player_group = pg.sprite.Group(self.player)
        
    def update(self, surface, keys, current_time):
        self.game_info[c.CURRENT_TIME] = self.current_time = current_time
        self.handle_states(keys)
        self.draw(surface)
    
    def handle_states(self, keys):
        self.update_all_sprites(keys)
    
    def update_all_sprites(self, keys):
        if self.player.dead:
            self.player.update(keys, self.game_info, self.powerup_group)
            if self.current_time - self.death_timer > 3000:
                self.update_game_info()
                self.done = True
        elif self.player.state == c.IN_CASTLE:
            self.player.update(keys, self.game_info, None)
            self.flagpole_group.update()
            if self.current_time - self.castle_timer > 2000:
                self.update_game_info()
                self.done = True
        elif self.in_frozen_state():
            self.player.update(keys, self.game_info, None)
            self.check_checkpoints()
            self.update_viewport()
            self.overhead_info.update(self.game_info, self.player)
            for score in self.moving_score_list:
                score.update(self.moving_score_list)
        else:
            self.player.update(keys, self.game_info, self.powerup_group)
            self.flagpole_group.update()
            self.check_checkpoints()
            self.slider_group.update()
            self.static_coin_group.update(self.game_info)
            self.enemy_group.update(self.game_info, self)
            self.shell_group.update(self.game_info, self)
            self.brick_group.update()
            self.box_group.update(self.game_info)
            self.powerup_group.update(self.game_info, self)
            self.coin_group.update(self.game_info)
            self.brickpiece_group.update()
            self.dying_group.update(self.game_info, self)
            self.update_player_position()
            self.check_for_player_death()
            self.update_viewport()
            self.overhead_info.update(self.game_info, self.player)
            for score in self.moving_score_list:
                score.update(self.moving_score_list)
    
    def check_checkpoints(self):
        checkpoint = pg.sprite.spritecollideany(self.player, self.checkpoint_group)
        
        if checkpoint:
            if checkpoint.type == c.CHECKPOINT_TYPE_ENEMY:
                group = self.enemy_group_list[checkpoint.enemy_groupid]
                self.enemy_group.add(group)
            elif checkpoint.type == c.CHECKPOINT_TYPE_FLAG:
                self.player.state = c.FLAGPOLE
                if self.player.rect.bottom < self.flag.rect.y:
                    self.player.rect.bottom = self.flag.rect.y
                self.flag.state = c.SLIDE_DOWN
                self.update_flag_score()
            elif checkpoint.type == c.CHECKPOINT_TYPE_CASTLE:
                self.player.state = c.IN_CASTLE
                self.player.x_vel = 0
                self.castle_timer = self.current_time
                self.flagpole_group.add(stuff.CastleFlag(8745, 322))
            elif (checkpoint.type == c.CHECKPOINT_TYPE_MUSHROOM and
                    self.player.y_vel < 0):
                mushroom_box = box.Box(checkpoint.rect.x, checkpoint.rect.bottom - 40,
                                c.TYPE_LIFEMUSHROOM, self.powerup_group)
                mushroom_box.start_bump(self.moving_score_list)
                self.box_group.add(mushroom_box)
                self.player.y_vel = 7
                self.player.rect.y = mushroom_box.rect.bottom
                self.player.state = c.FALL
            elif checkpoint.type == c.CHECKPOINT_TYPE_PIPE:
                self.player.state = c.WALK_AUTO
            elif checkpoint.type == c.CHECKPOINT_TYPE_PIPE_UP:
                self.change_map(checkpoint.map_index, checkpoint.type)
            elif checkpoint.type == c.CHECKPOINT_TYPE_MAP:
                self.change_map(checkpoint.map_index, checkpoint.type)
            elif checkpoint.type == c.CHECKPOINT_TYPE_BOSS:
                self.player.state = c.WALK_AUTO
            checkpoint.kill()

    def update_flag_score(self):
        base_y = c.GROUND_HEIGHT - 80
        
        y_score_list = [(base_y, 100), (base_y-120, 400),
                    (base_y-200, 800), (base_y-320, 2000),
                    (0, 5000)]
        for y, score in y_score_list:
            if self.player.rect.y > y:
                self.update_score(score, self.flag)
                break
        
    def update_player_position(self):
        if self.player.state == c.UP_OUT_PIPE:
            return

        self.player.rect.x += round(self.player.x_vel)
        if self.player.rect.x < self.start_x:
            self.player.rect.x = self.start_x
        elif self.player.rect.right > self.end_x:
            self.player.rect.right = self.end_x
        self.check_player_x_collisions()
        
        if not self.player.dead:
            self.player.rect.y += round(self.player.y_vel)
            self.check_player_y_collisions()
    
    def check_player_x_collisions(self):
        ground_step_pipe = pg.sprite.spritecollideany(self.player, self.ground_step_pipe_group)
        brick = pg.sprite.spritecollideany(self.player, self.brick_group)
        box = pg.sprite.spritecollideany(self.player, self.box_group)
        enemy = pg.sprite.spritecollideany(self.player, self.enemy_group)
        shell = pg.sprite.spritecollideany(self.player, self.shell_group)
        powerup = pg.sprite.spritecollideany(self.player, self.powerup_group)
        coin = pg.sprite.spritecollideany(self.player, self.static_coin_group)

        if box:
            self.adjust_player_for_x_collisions(box)
        elif brick:
            self.adjust_player_for_x_collisions(brick)
        elif ground_step_pipe:
            if (ground_step_pipe.name == c.MAP_PIPE and
                ground_step_pipe.type == c.PIPE_TYPE_HORIZONTAL):
                return
            self.adjust_player_for_x_collisions(ground_step_pipe)
        elif powerup:
            if powerup.type == c.TYPE_MUSHROOM:
                self.update_score(1000, powerup, 0)
                if not self.player.big:
                    self.player.y_vel = -1
                    self.player.state = c.SMALL_TO_BIG
            elif powerup.type == c.TYPE_FIREFLOWER:
                self.update_score(1000, powerup, 0)
                if not self.player.big:
                    self.player.state = c.SMALL_TO_BIG
                elif self.player.big and not self.player.fire:
                    self.player.state = c.BIG_TO_FIRE
            elif powerup.type == c.TYPE_STAR:
                self.update_score(1000, powerup, 0)
                self.player.invincible = True
            elif powerup.type == c.TYPE_LIFEMUSHROOM:
                self.update_score(500, powerup, 0)
                self.game_info[c.LIVES] += 1
            if powerup.type != c.TYPE_FIREBALL:
                powerup.kill()
        elif enemy:
            if self.player.invincible:
                self.update_score(100, enemy, 0)
                self.move_to_dying_group(self.enemy_group, enemy)
                direction = c.RIGHT if self.player.facing_right else c.LEFT
                enemy.start_death_jump(direction)
            elif self.player.hurt_invincible:
                pass
            elif self.player.big:
                self.player.y_vel = -1
                self.player.state = c.BIG_TO_SMALL
            else:
                self.player.start_death_jump(self.game_info)
                self.death_timer = self.current_time
        elif shell:
            if shell.state == c.SHELL_SLIDE:
                if self.player.invincible:
                    self.update_score(200, shell, 0)
                    self.move_to_dying_group(self.shell_group, shell)
                    direction = c.RIGHT if self.player.facing_right else c.LEFT
                    shell.start_death_jump(direction)
                elif self.player.hurt_invincible:
                    pass
                elif self.player.big:
                    self.player.y_vel = -1
                    self.player.state = c.BIG_TO_SMALL
                else:
                    self.player.start_death_jump(self.game_info)
                    self.death_timer = self.current_time
            else:
                self.update_score(400, shell, 0)
                if self.player.rect.x < shell.rect.x:
                    self.player.rect.left = shell.rect.x 
                    shell.direction = c.RIGHT
                    shell.x_vel = 10
                else:
                    self.player.rect.x = shell.rect.left
                    shell.direction = c.LEFT
                    shell.x_vel = -10
                shell.rect.x += shell.x_vel * 4
                shell.state = c.SHELL_SLIDE
        elif coin:
            self.update_score(100, coin, 1)
            coin.kill()

    def adjust_player_for_x_collisions(self, collider):
        if collider.name == c.MAP_SLIDER:
            return

        if self.player.rect.x < collider.rect.x:
            self.player.rect.right = collider.rect.left
        else:
            self.player.rect.left = collider.rect.right
        self.player.x_vel = 0

    def check_player_y_collisions(self):
        ground_step_pipe = pg.sprite.spritecollideany(self.player, self.ground_step_pipe_group)
        enemy = pg.sprite.spritecollideany(self.player, self.enemy_group)
        shell = pg.sprite.spritecollideany(self.player, self.shell_group)

        # decrease runtime delay: when player is on the ground, don't check brick and box
        if self.player.rect.bottom < c.GROUND_HEIGHT:
            brick = pg.sprite.spritecollideany(self.player, self.brick_group)
            box = pg.sprite.spritecollideany(self.player, self.box_group)
            brick, box = self.prevent_collision_conflict(brick, box)
        else:
            brick, box = False, False

        if box:
            self.adjust_player_for_y_collisions(box)
        elif brick:
            self.adjust_player_for_y_collisions(brick)
        elif ground_step_pipe:
            self.adjust_player_for_y_collisions(ground_step_pipe)
        elif enemy:
            if self.player.invincible:
                self.update_score(100, enemy, 0)
                self.move_to_dying_group(self.enemy_group, enemy)
                direction = c.RIGHT if self.player.facing_right else c.LEFT
                enemy.start_death_jump(direction)
            elif (enemy.name == c.PIRANHA or
                enemy.name == c.FIRESTICK or
                enemy.name == c.FIRE_KOOPA or
                enemy.name == c.FIRE):
                pass
            elif self.player.y_vel > 0:
                self.update_score(100, enemy, 0)
                enemy.state = c.JUMPED_ON
                if enemy.name == c.GOOMBA:
                    self.move_to_dying_group(self.enemy_group, enemy)
                elif enemy.name == c.KOOPA or enemy.name == c.FLY_KOOPA:
                    self.enemy_group.remove(enemy)
                    self.shell_group.add(enemy)

                self.player.rect.bottom = enemy.rect.top
                self.player.state = c.JUMP
                self.player.y_vel = -7
        elif shell:
            if self.player.y_vel > 0:
                if shell.state != c.SHELL_SLIDE:
                    shell.state = c.SHELL_SLIDE
                    if self.player.rect.centerx < shell.rect.centerx:
                        shell.direction = c.RIGHT
                        shell.rect.left = self.player.rect.right + 5
                    else:
                        shell.direction = c.LEFT
                        shell.rect.right = self.player.rect.left - 5
        self.check_is_falling(self.player)
        self.check_if_player_on_IN_pipe()
    
    def prevent_collision_conflict(self, sprite1, sprite2):
        if sprite1 and sprite2:
            distance1 = abs(self.player.rect.centerx - sprite1.rect.centerx)
            distance2 = abs(self.player.rect.centerx - sprite2.rect.centerx)
            if distance1 < distance2:
                sprite2 = False
            else:
                sprite1 = False
        return sprite1, sprite2
        
    def adjust_player_for_y_collisions(self, sprite):
        if self.player.rect.top > sprite.rect.top:
            if sprite.name == c.MAP_BRICK:
                self.check_if_enemy_on_brick_box(sprite)
                if sprite.state == c.RESTING:
                    if self.player.big and sprite.type == c.TYPE_NONE:
                        sprite.change_to_piece(self.dying_group)
                    else:
                        if sprite.type == c.TYPE_COIN:
                            self.update_score(200, sprite, 1)
                        sprite.start_bump(self.moving_score_list)
            elif sprite.name == c.MAP_BOX:
                self.check_if_enemy_on_brick_box(sprite)
                if sprite.state == c.RESTING:
                    if sprite.type == c.TYPE_COIN:
                        self.update_score(200, sprite, 1)
                    sprite.start_bump(self.moving_score_list)
            elif (sprite.name == c.MAP_PIPE and
                sprite.type == c.PIPE_TYPE_HORIZONTAL):
                return
            
            self.player.y_vel = 7
            self.player.rect.top = sprite.rect.bottom
            self.player.state = c.FALL
        else:
            self.player.y_vel = 0
            self.player.rect.bottom = sprite.rect.top
            if self.player.state == c.FLAGPOLE:
                self.player.state = c.WALK_AUTO
            elif self.player.state == c.END_OF_LEVEL_FALL:
                self.player.state = c.WALK_AUTO
            else:
                self.player.state = c.WALK
    
    def check_if_enemy_on_brick_box(self, brick):
        brick.rect.y -= 5
        enemy = pg.sprite.spritecollideany(brick, self.enemy_group)
        if enemy:
            self.update_score(100, enemy, 0)
            self.move_to_dying_group(self.enemy_group, enemy)
            if self.player.rect.centerx > brick.rect.centerx:
                direction = c.RIGHT
            else:
                direction = c.LEFT
            enemy.start_death_jump(direction)
        brick.rect.y += 5

    def in_frozen_state(self):
        if (self.player.state == c.SMALL_TO_BIG or
            self.player.state == c.BIG_TO_SMALL or
            self.player.state == c.BIG_TO_FIRE or
            self.player.state == c.DEATH_JUMP or
            self.player.state == c.DOWN_TO_PIPE or
            self.player.state == c.UP_OUT_PIPE):
            return True
        else:
            return False

    def check_is_falling(self, sprite):
        sprite.rect.y += 1
        check_group = pg.sprite.Group(self.ground_step_pipe_group,
                            self.brick_group, self.box_group)
        
        if pg.sprite.spritecollideany(sprite, check_group) is None:
            if (sprite.state == c.WALK_AUTO or
                sprite.state == c.END_OF_LEVEL_FALL):
                sprite.state = c.END_OF_LEVEL_FALL
            elif (sprite.state != c.JUMP and 
                sprite.state != c.FLAGPOLE and
                not self.in_frozen_state()):
                sprite.state = c.FALL
        sprite.rect.y -= 1
    
    def check_for_player_death(self):
        if (self.player.rect.y > c.SCREEN_HEIGHT or
            self.overhead_info.time <= 0):
            self.player.start_death_jump(self.game_info)
            self.death_timer = self.current_time

    def check_if_player_on_IN_pipe(self):
        '''check if player is on the pipe which can go down in to it '''
        self.player.rect.y += 1
        pipe = pg.sprite.spritecollideany(self.player, self.pipe_group)
        if pipe and pipe.type == c.PIPE_TYPE_IN:
            if (self.player.crouching and
                self.player.rect.x < pipe.rect.centerx and
                self.player.rect.right > pipe.rect.centerx):
                self.player.state = c.DOWN_TO_PIPE
        self.player.rect.y -= 1
        
    def update_game_info(self):
        if self.player.dead:
            self.persist[c.LIVES] -= 1

        if self.persist[c.LIVES] == 0:
            self.next = c.GAME_OVER
        elif self.overhead_info.time == 0:
            self.next = c.TIME_OUT
        elif self.player.dead:
            self.next = c.LOAD_SCREEN
        else:
            self.game_info[c.LEVEL_NUM] += 1
            self.next = c.LOAD_SCREEN

    def update_viewport(self):
        third = self.viewport.x + self.viewport.w//3
        player_center = self.player.rect.centerx
        
        if (self.player.x_vel > 0 and 
            player_center >= third and
            self.viewport.right < self.end_x):
            self.viewport.x += round(self.player.x_vel)
        elif self.player.x_vel < 0 and self.viewport.x > self.start_x:
            self.viewport.x += round(self.player.x_vel)
    
    def move_to_dying_group(self, group, sprite):
        group.remove(sprite)
        self.dying_group.add(sprite)
        
    def update_score(self, score, sprite, coin_num=0):
        self.game_info[c.SCORE] += score
        self.game_info[c.COIN_TOTAL] += coin_num
        x = sprite.rect.x
        y = sprite.rect.y - 10
        self.moving_score_list.append(stuff.Score(x, y, score))

    def draw(self, surface):
        self.level.blit(self.background, self.viewport, self.viewport)
        self.powerup_group.draw(self.level)
        self.brick_group.draw(self.level)
        self.box_group.draw(self.level)
        self.coin_group.draw(self.level)
        self.dying_group.draw(self.level)
        self.brickpiece_group.draw(self.level)
        self.flagpole_group.draw(self.level)
        self.shell_group.draw(self.level)
        self.enemy_group.draw(self.level)
        self.player_group.draw(self.level)
        self.static_coin_group.draw(self.level)
        self.slider_group.draw(self.level)
        self.pipe_group.draw(self.level)
        for score in self.moving_score_list:
            score.draw(self.level)
        if c.DEBUG:
            self.ground_step_pipe_group.draw(self.level)
            self.checkpoint_group.draw(self.level)

        surface.blit(self.level, (0,0), self.viewport)
        self.overhead_info.draw(surface)
