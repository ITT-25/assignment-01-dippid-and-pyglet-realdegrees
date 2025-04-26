import math
from typing import TYPE_CHECKING
from pyglet import shapes
from util import gameobject_batch, Vector2D
from .game_object import GameObject

if TYPE_CHECKING:
    from game import GameWindow

class Paddle(GameObject):
    def __init__(self, x, y, player_id: int, window: "GameWindow"):
        super().__init__(shapes.RoundedRectangle(
            x, y, 35, 250, radius=math.pi, color=(255, 255, 255), batch=gameobject_batch), window)
        self.player_id = player_id
        self.window = window
        self.set_velocity(Vector2D(0, 0))
    
    def update(self, delta_time):
        super().update(delta_time)
        # Clamp paddle position to stay within window bounds
        if self.shape.x < 0:
            self.shape.x = 0
        elif self.shape.x + self.shape.width > self.window.width:
            self.shape.x = self.window.width - self.shape.width
        if self.shape.y < 0:
            self.shape.y = 0
        elif self.shape.y + self.shape.height > self.window.height:
            self.shape.y = self.window.height - self.shape.height
