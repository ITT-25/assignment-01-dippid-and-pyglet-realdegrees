import os
import random
from typing import Optional
import pyglet
from src.gameobjects.border import Border
from src.gameobjects.paddle import Paddle
from src.util import Vector2D, gameobject_batch
from .gameobject import GameObject


class Ball(GameObject):
    def __init__(self, x, y, radius, window):
        super().__init__(pyglet.shapes.RoundedRectangle(
            x, y, width=radius * 2, height=radius * 2, radius=radius, color=(255, 255, 255), batch=gameobject_batch), window)
        self.audio = pyglet.media.load(os.path.abspath(
            os.path.dirname(__file__) + '/../../assets/bounce.wav'), streaming=False)
        self.player: Optional[pyglet.media.Player] = None

    def play_bounce_sound(self):
        self.player = self.audio.play()
        self.player.pitch = random.uniform(0.8, 1.2)
        self.player.volume = 0.3

    def on_collision_start(self, other: 'GameObject'):
        if isinstance(other, Paddle):
            # Update NPC offset for the paddle
            other.update_npc_offset()

            # ! Original Bounce Logic Code
            
            # bounce_direction = self.get_center() - other.get_center()
            # self.velocity = Vector2D.lerp(
            #     -self.velocity.normalize(), 
            #     bounce_direction.normalize(), 
            # 0.8).normalize() * self.velocity.length() * random.uniform(1.05, 1.15)
            # self.play_bounce_sound()
            
            #region Bounce Logic
            # ? Source: Copilot prompt based on original code above: "adjust the bounce direction logic in #file:ball.py so that it feels more like the original pong mechanics"
            # ? Generated code is slightly modified
            
            # Classic Pong bounce: angle depends on where the ball hits the paddle
            ball_center = self.get_center()
            paddle_center = other.get_center()
            paddle_height = other.shape.height
            # Offset: -1 (top edge) to 1 (bottom edge)
            offset = (ball_center.y - paddle_center.y) / (paddle_height / 2)
            offset = max(-1, min(1, offset))  # Clamp to [-1, 1]

            # Determine direction: left or right depending on which side the paddle is
            direction = -1 if self.velocity.x > 0 else 1
            speed = self.velocity.length() * random.uniform(1.05, 1.15)
            max_bounce_angle = 60  # degrees
            angle = offset * max_bounce_angle
            import math
            rad = math.radians(angle)
            new_vx = direction * abs(math.cos(rad)) * speed
            new_vy = math.sin(rad) * speed
            self.velocity = Vector2D(new_vx, new_vy)
            self.play_bounce_sound()
            #endregion
        elif isinstance(other, Border):
            # Reflect the ball's velocity based on the border normal
            self.velocity = self.velocity.reflect(other.normal())
            self.play_bounce_sound()

    def reset(self, x, y):
        self.shape.x = x - self.shape.width / 2
        self.shape.y = y - self.shape.height / 2
        self.velocity = Vector2D(0, 0)
        self.visible = True
