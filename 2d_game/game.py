import sys
import pyglet
from pyglet import window, clock
from config import WINDOW_WIDTH, WINDOW_HEIGHT
from src.managers.game_manager import GameManager
from src.managers.collision_manager import CollisionManager
from src.managers.ui import GameUI
from src.util import gameobject_batch, ui_batch

# Global reference for GameWindow
GAME_WINDOW = None

class GameWindow(window.Window):

    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.set_caption("DIPPID Pong")
        self.set_visible(True)
        self.game_manager = GameManager(self)
        self.collision_manager = CollisionManager(self, self.game_manager)
        self.ui = GameUI(self)

    def on_update(self, delta_time):
        self.collision_manager.update(delta_time)
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


if __name__ == "__main__":
    win = GameWindow()
    pyglet.clock.schedule_interval(win.on_update, 1/60.0)
    pyglet.app.run()
