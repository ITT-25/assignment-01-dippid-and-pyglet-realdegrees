from src.script import Script
from src.util import Vector2D

class Border(Script):
    def __init__(self, gameobject, direction):
        super().__init__()
        self.gameobject = gameobject
        self._direction = direction
    def normal(self):
        if self._direction == 1:
            return Vector2D(0, 1)
        elif self._direction == 2:
            return Vector2D(0, -1)
        return Vector2D(0, 0)
