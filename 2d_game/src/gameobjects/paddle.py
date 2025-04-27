import math
import random
import time
from typing import TYPE_CHECKING
from DIPPID import SensorUDP
from pyglet import shapes
from src.util import gameobject_batch, Vector2D
from src.gameobjects.gameobject import GameObject
from config import INITIAL_BALL_SPEED, NPC_MAX_BASE_SPEED

if TYPE_CHECKING:
    from game import GameWindow
    from src.gameobjects.ball import Ball


class Paddle(GameObject, SensorUDP):
    last_signal: int = None

    def __init__(self, x, y, player_id: int, window: "GameWindow", ball: "Ball"):
        GameObject.__init__(
            self,
            shapes.RoundedRectangle(
                x,
                y,
                35,
                250,
                radius=math.pi,
                color=(255, 255, 255),
                batch=gameobject_batch,
            ),
            window,
        )
        SensorUDP.__init__(self, player_id)
        self.player_id = player_id
        self.window = window
        self.ball = ball
        self.score = 0
        self.npc_offset_y = 0
        self.set_velocity(Vector2D(0, 0))
        self.register_callback("gravity", self.on_input)

    def update_npc_offset(self):
        paddle_height = self.shape.height
        offset = random.uniform(-0.45, 0.45) * paddle_height
        self.npc_offset_y = offset

    def on_input(self, gravity):
        print(f"Gravity: {gravity}")
        if "z" in gravity:
            input = (
                math.copysign(abs(gravity["z"] / 9.81) ** 1.5, gravity["z"])
                * INITIAL_BALL_SPEED
                * 1.35
            )
            self.set_velocity(Vector2D(0, input))
            self.last_signal = time.time()

    def is_ready(self):
        return not self.is_connected() or self.get_value("button_1") == 1

    def update(self, delta_time):
        GameObject.update(self, delta_time)
        # Clamp paddle position to stay within window bounds
        if self.shape.x < 0:
            self.shape.x = 0
        elif self.shape.x + self.shape.width > self.window.width:
            self.shape.x = self.window.width - self.shape.width
        if self.shape.y < 0:
            self.shape.y = 0
        elif self.shape.y + self.shape.height > self.window.height:
            self.shape.y = self.window.height - self.shape.height

        if not self.is_connected():
            self.npc_takeover()

    def is_connected(self):
        signal_delta = time.time() - (self.last_signal or 0)
        timed_out = signal_delta > 2
        return (
            not timed_out
            and self.has_capability("gravity")
            and "z" in self.get_value("gravity")
            and self.has_capability("button_1")
        )

    def npc_takeover(self):
        ball_center = self.ball.get_center()
        paddle_center = self.get_center()
        target_y = paddle_center.y + getattr(self, "npc_offset_y", 0)
        is_moving_towards_paddle = (
            self.ball.velocity.x < 0 and ball_center.x > paddle_center.x
        ) or (self.ball.velocity.x > 0 and ball_center.x < paddle_center.x)
        distance_x = abs(ball_center.x - paddle_center.x)
        speed_factor = (
            (NPC_MAX_BASE_SPEED + (1 - distance_x / self.window.width))
            if is_moving_towards_paddle
            else NPC_MAX_BASE_SPEED / 2
        )
        delta_y = max(min(ball_center.y - target_y, 9.81), -9.81)
        desired_vertical_velocity = delta_y / 9.81 * INITIAL_BALL_SPEED * speed_factor
        self.set_velocity(Vector2D(0, desired_vertical_velocity))
