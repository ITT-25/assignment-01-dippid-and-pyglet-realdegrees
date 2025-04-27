import math
from typing import TYPE_CHECKING
from DIPPID import SensorUDP
from config import INITIAL_BALL_SPEED, NPC_MAX_BASE_SPEED

from src.util import Vector2D
import time

if TYPE_CHECKING:
    from game import GameWindow
    from src.gameobjects.ball import Ball
    from src.gameobjects.paddle import Paddle


class Player(SensorUDP):
    last_signal: int = None

    def __init__(self, paddle: "Paddle", ball: "Ball", window: "GameWindow"):
        super().__init__(paddle.player_id)
        self.paddle = paddle
        self.ball = ball
        self.window = window
        self.score = 0
        self.register_callback("gravity", self.on_input)

    def on_input(self, gravity):
        print(f"Gravity: {gravity}")
        if "z" in gravity:
            input = math.copysign(abs(gravity["z"] / 9.81) ** 1.5, gravity["z"]) * INITIAL_BALL_SPEED * 1.35
            self.paddle.set_velocity(Vector2D(0, input))
            self.last_signal = time.time()

    def is_ready(self):
        """Check if the player is ready to play. Returns True if the player as not connected due to NPC takeover."""
        return not self.is_connected() or self.get_value("button_1") == 1

    def update(self, delta_time):
        if self.is_connected():
            return
        else:
            self.npc_takeover()

    def is_connected(self):
        signal_delta = time.time() - (self.last_signal or 0)
        timed_out = signal_delta > 2
        return (
            not timed_out and
            self.has_capability("gravity") and
            "z" in self.get_value("gravity") and
            self.has_capability("button_1")
        )

    def npc_takeover(self):
        # Determine if ball is moving towards or away from the paddle
        ball_center = self.ball.get_center()
        paddle_center = self.paddle.get_center()

        is_moving_towards_paddle = (
            (self.ball.velocity.x < 0 and ball_center.x > paddle_center.x) or
            (self.ball.velocity.x > 0 and ball_center.x < paddle_center.x)
        )
        distance_x = abs(ball_center.x - paddle_center.x)
        
        
        

        # Adjust speed multiplier based on ball direction relative to paddle
        speed_factor = (NPC_MAX_BASE_SPEED + (1 - distance_x / self.window.width))if is_moving_towards_paddle else NPC_MAX_BASE_SPEED / 2

        # Calculate and apply final velocity to paddle
        delta_y = max(min(ball_center.y - paddle_center.y, 9.81), -9.81)
        desired_vertical_velocity = delta_y / 9.81 * \
            INITIAL_BALL_SPEED * speed_factor
        self.paddle.set_velocity(Vector2D(0, desired_vertical_velocity))
