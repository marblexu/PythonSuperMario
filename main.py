import pygame as pg
from source.main import main
from pygame import mixer

if __name__=='__main__':
    mixer.init()
    mixer.music.load("Little-West-Finaly.ogg")
    # mixer.music.play()
    main()
    pg.quit()