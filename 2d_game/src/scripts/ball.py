from typing import TYPE_CHECKING
from src.script import Script
from src.util import Vector2D
import os
import pyglet
import random
import math
from config import INITIAL_BALL_SPEED, SPEED_RATE
from src.scripts.border import Border
from src.scripts.paddle import Paddle

if TYPE_CHECKING:
    from src.gameobject import GameObject


class Ball(Script):
    def __init__(self, gameobject):
        super().__init__()
        self.gameobject = gameobject
        self.audio = pyglet.media.load(
            os.path.abspath(os.path.dirname(__file__) + "/../../assets/bounce.wav"),
            streaming=False,
        )
        self.player = None

    def play_bounce_sound(self):
        self.player = self.audio.play()
        self.player.pitch = random.uniform(0.8, 1.2)
        self.player.volume = 0.3

    def on_collision_start(self, other: "GameObject"):
        if other.tag == "border":
            border = other.get_script(Border)
            if border:
                self.gameobject.velocity = self.gameobject.velocity.reflect(
                    border.normal()
                )
            self.play_bounce_sound()
        elif other.tag == "paddle":
            paddle = other.get_script(Paddle)
            paddle.update_npc_offset()
            ball_center = self.gameobject.get_center()
            paddle_center = other.get_center()
            paddle_height = other.shape.height
            offset = (ball_center.y - paddle_center.y) / (paddle_height / 2)
            offset = max(-1, min(1, offset))
            direction = -1 if self.gameobject.velocity.x > 0 else 1
            speed = self.gameobject.velocity.length() + random.uniform(
                INITIAL_BALL_SPEED * (SPEED_RATE / 3), INITIAL_BALL_SPEED * SPEED_RATE
            )
            max_bounce_angle = 60
            angle = offset * max_bounce_angle
            rad = math.radians(angle)
            new_vx = direction * abs(math.cos(rad)) * speed
            new_vy = math.sin(rad) * speed
            self.gameobject.velocity = Vector2D(new_vx, new_vy)
            self.play_bounce_sound()

    def reset(self, x, y):
        self.gameobject.shape.x = x - self.gameobject.shape.width / 2 - self.gameobject.shape.width / 2
        self.gameobject.shape.y = y - self.gameobject.shape.height / 2 - self.gameobject.shape.height / 2
        self.gameobject.velocity = Vector2D(0, 0)
        self.gameobject.out_of_bounds_ver = False
        self.gameobject.out_of_bounds_hor = False
