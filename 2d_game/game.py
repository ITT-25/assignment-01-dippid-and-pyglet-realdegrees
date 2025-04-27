from __future__ import annotations
import sys
import pyglet
from pyglet import window, clock
from config import WINDOW_WIDTH, WINDOW_HEIGHT
from src.util import gameobject_batch, ui_batch
from src.managers.game_manager import GameManager
from src.managers.ui import GameUI

class GameWindow(window.Window):
    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.set_caption("DIPPID Pong")
        self.set_visible(True)
        self.game_manager = GameManager(self)
        self.ui = GameUI(self, self.game_manager.player_1, self.game_manager.player_2)

    def on_update(self, delta_time):
        self.game_manager.update(delta_time)
        self.ui.update(delta_time)

    def on_draw(self):
        self.clear()
        gameobject_batch.draw()
        ui_batch.draw()

    def on_resize(self, width, height):
        # Enforce fixed window size
        if width != WINDOW_WIDTH or height != WINDOW_HEIGHT:
            self.set_size(WINDOW_WIDTH, WINDOW_HEIGHT)
        return super().on_resize(WINDOW_WIDTH, WINDOW_HEIGHT)
    
    def on_close(self):
        super().on_close()
        
        clock.unschedule(self.on_update)
        self.game_manager.exit()
        pyglet.app.exit()
        sys.exit()


win = GameWindow()
clock.schedule(win.on_update)
pyglet.app.run()
