from DIPPID import SensorUDP
from config import INITIAL_BALL_SPEED
from src.ball import Ball
from src.paddle import Paddle
from util import Vector2D
import time

class Player(SensorUDP):
    last_signal: int = None
    def __init__(self, paddle: Paddle, ball: Ball):
        super().__init__(paddle.player_id)
        self.paddle = paddle
        self.ball = ball
        self.score = 0
        self.register_callback("gravity", self.on_input)

    def on_input(self, gravity):
        print(f"Gravity: {gravity}")
        if "z" in gravity:
            input = gravity["z"] / 9.81 * INITIAL_BALL_SPEED * 1.25
            self.paddle.set_velocity(Vector2D(0, input))
            self.last_signal = time.time()
                

    def is_ready(self):
        """Check if the player is ready to play. Returns True if the player as not connected due to NPC takeover."""
        return not self.is_connected() or self.get_value("button_1") == 1
                
    def update(self, delta_time):
        if self.is_connected():
            return

        # NPC Takeover
        delta = max(min(self.ball.get_center().y - self.paddle.get_center().y, 9.81), -9.81)
        desired_vertical_velocity = delta / 9.81 * INITIAL_BALL_SPEED * 0.8
        self.paddle.set_velocity(Vector2D(0, desired_vertical_velocity))
                
    def is_connected(self):
        signal_delta = time.time() - (self.last_signal or 0)
        timed_out = signal_delta > 2
        return not timed_out and self.has_capability("gravity") and "z" in self.get_value("gravity") and self.has_capability("button_1")
