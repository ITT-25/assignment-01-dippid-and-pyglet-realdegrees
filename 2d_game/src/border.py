from enum import Enum
from util import gameobject_batch, Vector2D
import pyglet
from .game_object import GameObject

class BorderDirection(Enum):
    UP = 1
    DOWN = 2

class Border(GameObject):
    def __init__(self, x, y, width, height, window, direction: BorderDirection):
        shape = pyglet.shapes.RoundedRectangle(
            x, y, width=width, height=height, radius=30, color=(255, 255, 255), batch=gameobject_batch
        )
        super().__init__(shape, window)
        self._direction = direction

    def normal(self):
        if self._direction == BorderDirection.UP:
            return Vector2D(0, 1)
        elif self._direction == BorderDirection.DOWN:
            return Vector2D(0, -1)
        return Vector2D(0, 0)