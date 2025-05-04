from typing import TYPE_CHECKING
from src.script import Script
from src.util import Vector2D
from config import INITIAL_BALL_SPEED, NPC_MAX_BASE_SPEED
import random
import math
import time
from DIPPID import SensorUDP

if TYPE_CHECKING:
    from src.gameobject import GameObject


class Paddle(Script):
    def __init__(self, gameobject: "GameObject", player_id):
        super().__init__()
        self.gameobject = gameobject
        self.player_id: int = player_id
        self.score: int = 0
        self.npc_offset_y: int = 0
        self.last_signal: float = None
        self.sensor = SensorUDP(player_id)
        self.sensor.register_callback("gravity", self.on_input)
        self.window = gameobject.gm.window

    def update_npc_offset(self):
        paddle_height = self.gameobject.shape.height
        offset = random.uniform(-0.45, 0.45) * paddle_height
        self.npc_offset_y = offset

    def on_input(self, gravity: dict):
        if "z" in gravity:
            input: float = (
                math.copysign(abs(gravity["z"] / 9.81) ** 1.5, gravity["z"])
                * INITIAL_BALL_SPEED
                * 1.35
            )
            self.gameobject.set_velocity(Vector2D(0, input))
            self.last_signal = time.time()

    def is_ready(self) -> bool:
        return not self.is_connected() or self.sensor.get_value("button_1") == 1

    def update(self, delta_time):
        if self.gameobject.shape.x < 0:
            self.gameobject.shape.x = 0
        elif self.gameobject.shape.x + self.gameobject.shape.width > self.window.width:
            self.gameobject.shape.x = self.window.width - self.gameobject.shape.width
        if self.gameobject.shape.y < 0:
            self.gameobject.shape.y = 0
        elif self.gameobject.shape.y + self.gameobject.shape.height > self.window.height:
            self.gameobject.shape.y = self.window.height - self.gameobject.shape.height
        if not self.is_connected():
            self.npc_takeover()

    def is_connected(self):
        signal_delta = time.time() - (self.last_signal or 0)
        timed_out = signal_delta > 2
        return (
            not timed_out
            and self.sensor.has_capability("gravity")
            and "z" in self.sensor.get_value("gravity")
            and self.sensor.has_capability("button_1")
        )

    def npc_takeover(self):
        ball = self.gameobject.gm.find("Ball") if self.gameobject.gm.find("Ball") else None
        if not ball:
            return
        
        ball_center = ball.get_center()
        paddle_center = self.gameobject.get_center()
        target_y = paddle_center.y + self.npc_offset_y
        is_moving_towards_paddle = (
            ball.velocity.x < 0 and ball_center.x > paddle_center.x
        ) or (ball.velocity.x > 0 and ball_center.x < paddle_center.x)
        distance_x = abs(ball_center.x - paddle_center.x)
        speed_factor = (
            (NPC_MAX_BASE_SPEED + (0.5 - min(0.5, (distance_x) / self.window.width)))
            if is_moving_towards_paddle
            else NPC_MAX_BASE_SPEED / 2
        )
        delta_y = max(min(ball_center.y - target_y, 9.81), -9.81)
        desired_vertical_velocity = delta_y / 9.81 * INITIAL_BALL_SPEED * speed_factor
        self.gameobject.set_velocity(Vector2D(0, desired_vertical_velocity))

    def disconnect(self):
        self.sensor.disconnect()
