import pygame as pg
from . import setup, tools
from . import constants as c
from .states import main_menu, load_screen, level

def main():
	run_it = tools.Control(c.SCREEN_SIZE)
	state_dict = {c.MAIN_MENU: main_menu.Menu(),
				  c.LOAD_SCREEN: load_screen.LoadScreen(),
				  c.LEVEL: level.Level(),
				  c.GAME_OVER: load_screen.GameOver()}
	run_it.setup_states(state_dict, c.MAIN_MENU)
	run_it.main()
