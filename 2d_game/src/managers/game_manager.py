from __future__ import annotations
from typing import TYPE_CHECKING
from src.gameobjects.paddle import Paddle
from src.gameobjects.ball import Ball
from src.gameobjects.border import Border, BorderDirection
from src.managers.collision_manager import CollisionManager
from config import INITIAL_BALL_SPEED, PADDLE_DIMENSIONS, PLAYER_1_PORT, PLAYER_2_PORT
from src.util import GameState, Vector2D

if TYPE_CHECKING:
    from game import GameWindow


class GameManager():
    """GameManager is responsible for managing the game state and updating game objects."""

    def __init__(self, window: "GameWindow"):
        self.window = window

        # Init Ball
        self.ball = Ball(self.window.width / 2,
                         self.window.height / 2, 12, window)

        # Init Paddles
        self.paddle_left = Paddle(50, self.window.height / 2 - PADDLE_DIMENSIONS.y / 2,
                                  PLAYER_1_PORT, window, self.ball)
        self.paddle_right = Paddle(self.window.width - 50 - PADDLE_DIMENSIONS.x, self.window.height / 2 - PADDLE_DIMENSIONS.y / 2,
                                   PLAYER_2_PORT, window, self.ball)

        # Init Borders
        self.border_bottom = Border(
            0, -self.window.height, self.window.width, self.window.height, window, direction=BorderDirection.UP)
        self.border_top = Border(
            0, self.window.height, self.window.width, self.window.height, window, direction=BorderDirection.DOWN)

        # Init collision manager with all game objects
        self.collision_manager = CollisionManager(window)
        self.collision_manager.add(
            self.ball, self.paddle_left, self.paddle_right, self.border_top, self.border_bottom)

        self.state = GameState.INACTIVE
        self.reset_timer = 0
        self.last_scorer = None

    def reset(self):
        self.ball.reset(self.window.width / 2, self.window.height / 2)
        self.ball.visible = True
        self.state = GameState.WAITING
        self.reset_timer = 0

    def update(self, delta_time: float):
        was_ball_visible = self.ball.visible

        # Forward update call
        self.ball.update(delta_time)
        self.paddle_left.update(delta_time)
        self.paddle_right.update(delta_time)

        # Restricts npc movement during non-playing states
        if self.state == GameState.PLAYING:
            self.paddle_left.update(delta_time)
            self.paddle_right.update(delta_time)

        self.collision_manager.update(delta_time)

        # State transitions
        if self.state == GameState.INACTIVE:
            if self.paddle_left.is_connected() or self.paddle_right.is_connected():
                self.state = GameState.WAITING

        elif self.state == GameState.WAITING:
            # Wait for button_1 from either player
            if self.paddle_left.is_ready() and self.paddle_right.is_ready():
                self.ball.set_velocity((
                    self.paddle_left.get_center() - self.ball.get_center()
                ).normalize() * INITIAL_BALL_SPEED)
                self.state = GameState.PLAYING

        elif self.state == GameState.PLAYING:
            if not self.ball.visible and was_ball_visible:
                if self.ball.shape.x < 0:
                    self.paddle_right.score += 1
                    self.last_scorer = self.paddle_right
                else:
                    self.paddle_left.score += 1
                    self.last_scorer = self.paddle_left
                self.state = GameState.RESETTING
                self.reset_timer = 1.0

        elif self.state == GameState.RESETTING:
            self.reset_timer -= delta_time
            self.paddle_left.set_velocity(Vector2D(0, 0))
            self.paddle_right.set_velocity(Vector2D(0, 0))
            if self.reset_timer <= 0:
                self.reset()

    def exit(self):
        # Disconnect DIPPID sensors to stop them from keeping the process alive on exit
        self.paddle_left.disconnect()
        self.paddle_right.disconnect()
