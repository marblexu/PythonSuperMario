__author__ = 'marble_xu'

from .. import setup, tools
from .. import constants as c
from ..components import info

class LoadScreen(tools.State):
    def __init__(self):
        tools.State.__init__(self)
        self.time_list = [2400, 2600, 2635]
        
    def startup(self, current_time, persist):
        self.start_time = current_time
        self.persist = persist
        self.game_info = self.persist
        self.next = self.set_next_state()
        
        info_state = self.set_info_state()
        self.overhead_info = info.Info(self.game_info, info_state)
    
    def set_next_state(self):
        return c.LEVEL
    
    def set_info_state(self):
        return c.LOAD_SCREEN

    def update(self, surface, keys, current_time):
        if (current_time - self.start_time) < self.time_list[0]:
            surface.fill(c.BLACK)
            self.overhead_info.update(self.game_info)
            self.overhead_info.draw(surface)
        elif (current_time - self.start_time) < self.time_list[1]:
            surface.fill(c.BLACK)
        elif (current_time - self.start_time) < self.time_list[2]:
            surface.fill((106, 150, 252))
        else:
            self.done = True
            
class GameOver(LoadScreen):
    def __init__(self):
        LoadScreen.__init__(self)
        self.time_list = [3000, 3200, 3235]

    def set_next_state(self):
        return c.MAIN_MENU
    
    def set_info_state(self):
        return c.GAME_OVER

class TimeOut(LoadScreen):
    def __init__(self):
        LoadScreen.__init__(self)
        self.time_list = [2400, 2600, 2635]

    def set_next_state(self):
        if self.persist[c.LIVES] == 0:
            return c.GAME_OVER
        else:
            return c.LOAD_SCREEN

    def set_info_state(self):
        return c.TIME_OUT
