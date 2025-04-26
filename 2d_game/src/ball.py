import os
import random
from typing import Optional
import pyglet
from src.border import Border
from src.paddle import Paddle
from util import Vector2D, gameobject_batch
from .game_object import GameObject


class Ball(GameObject):
    def __init__(self, x, y, radius, window):
        super().__init__(pyglet.shapes.RoundedRectangle(
            x, y, width=radius * 2, height=radius * 2, radius=radius, color=(255, 255, 255), batch=gameobject_batch), window)
        self.audio = pyglet.media.load(os.path.abspath(
            os.path.dirname(__file__) + '/../assets/bounce.wav'), streaming=False)
        self.player: Optional[pyglet.media.Player] = None

    def play_bounce_sound(self):
        self.player = self.audio.play()
        self.player.pitch = random.uniform(0.8, 1.2)
        self.player.volume = 0.3

    def on_collision_start(self, other: 'GameObject'):
        if isinstance(other, Paddle):
            # Calculate the new velocity from the center of the paddle to the center of the ball
            bounce_direction = self.get_center() - other.get_center()
            self.velocity = Vector2D.lerp(
                -self.velocity.normalize(), 
                bounce_direction.normalize(), 
            0.8).normalize() * self.velocity.length() * random.uniform(1.05, 1.15)
            self.play_bounce_sound()
        elif isinstance(other, Border):
            # Reflect the ball's velocity based on the border normal
            self.velocity = self.velocity.reflect(other.normal())
            self.play_bounce_sound()

    def reset(self, x, y):
        self.shape.x = x - self.shape.width / 2
        self.shape.y = y - self.shape.height / 2
        self.velocity = Vector2D(0, 0)
        self.visible = True
