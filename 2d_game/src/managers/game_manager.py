from __future__ import annotations
import math
import os
import random
from typing import TYPE_CHECKING, List, Literal, Type, TypeVar
from src.gameobject import GameObject
from config import (
    INITIAL_BALL_SPEED,
    PADDLE_DIMENSIONS,
    PLAYER_1_PORT,
    PLAYER_2_PORT,
    RESET_DURATION,
    WIN_CONDITION,
)
from src.util import GameState, Vector2D
from pyglet import shapes, media
from src.scripts.ball import Ball
from src.scripts.paddle import Paddle
from src.scripts.border import Border
from src.scripts.confetti import Confetti
from src.util import gameobject_batch

if TYPE_CHECKING:
    from game import GameWindow
    from src.script import Script

T = TypeVar("T", bound="Script")


class GameManager:
    """GameManager is responsible for managing the game state and updating game objects."""

    state: GameState = GameState.INACTIVE
    reset_timer: float = 0
    last_scorer: GameObject | None = None
    gameobjects: List[GameObject] = []

    def __init__(self, window: "GameWindow"):
        self.window = window
        self.winner = None  # Track the winner for GAME_OVER state
        GameObject.gm = self  # Set static reference to this GameManager
        
        self.win_audio = media.load(
            os.path.abspath(os.path.dirname(__file__) + "/../../assets/pop.ogg"),
            streaming=False,
        )

        # Init Ball
        ball_size = 15
        ball_shape = shapes.RoundedRectangle(
            self.window.width / 2 - ball_size / 2,
            self.window.height / 2 - ball_size / 2,
            width=ball_size,
            height=ball_size,
            radius=ball_size / 2,
            color=(255, 255, 255),
            batch=gameobject_batch,
        )
        ball = GameObject.create(
            ball_shape, name="Ball", tag="ball", collision=True)
        ball.register_script(Ball(ball))

        # Init Paddles
        def init_paddle(side: Literal["left", "right"]) -> None:
            width = PADDLE_DIMENSIONS.x
            height = PADDLE_DIMENSIONS.y
            paddle_shape = shapes.RoundedRectangle(
                20 if side == "left" else self.window.width - 20 - width,
                self.window.height / 2 - height / 2,
                width=width,
                height=height,
                radius=math.pi,
                color=(255, 255, 255),
                batch=gameobject_batch,
            )

            paddle = GameObject.create(
                paddle_shape,
                name="Paddle Left" if side == "left" else "Paddle Right",
                tag="paddle",
                collision=True,
            )
            paddle.register_script(
                Paddle(paddle, PLAYER_1_PORT if side ==
                       "left" else PLAYER_2_PORT)
            )

        init_paddle("left")
        init_paddle("right")

        # Init Borders
        def init_border(side: Literal["top", "bottom"]) -> None:
            width = self.window.width
            height = self.window.height
            border_shape = shapes.RoundedRectangle(
                x=0,
                y=self.window.height if side == "top" else 0 - height,
                width=width,
                height=height,
                radius=math.pi,
                color=(255, 255, 255, 150),
                batch=gameobject_batch,
            )
            border = GameObject.create(
                border_shape,
                name="Border Top" if side == "top" else "Border Bottom",
                tag="border",
                collision=True,
            )
            border.register_script(
                Border(border, direction=1 if side == "top" else 2))

        init_border("top")
        init_border("bottom")
        
        # Init Separator
        def init_separator_segment(x: float, y: float) -> None:
            width = 4
            height = 4
            separator_shape = shapes.Rectangle(
                x=x - width / 2,
                y=y - height / 2,
                width=width,
                height=height,
                color=(255, 255, 255, 40),
                batch=gameobject_batch,
            )
            GameObject.create(
                separator_shape,
                name="Separator",
                tag="separator",
                collision=False,
            )
            
        for i in range(0, self.window.height, 10):
            init_separator_segment(
                self.window.width / 2, i + 10
            )

    def reset(self):
        ball = self.find("Ball")
        if not ball:
            raise ValueError("Ball not found in GameManager.")

        ball.set_position(self.window.width / 2, self.window.height / 2)
        ball.set_velocity(Vector2D(0, 0))
        ball.out_of_bounds_ver = False
        ball.out_of_bounds_hor = False
        self.state = GameState.WAITING
        self.reset_timer = 0

    def reset_scores(self):
        paddles = self.find_by_script(Paddle)
        for paddle in paddles:
            paddle.get_script(Paddle).score = 0

    def find_by_tag(self, tag: str) -> list[GameObject]:
        """Find all GameObjects with the specified tag."""
        return [go for go in self.gameobjects if go.tag == tag]

    def find_by_script(self, script_type: Type[T]) -> list[GameObject]:
        """Find all GameObjects with the specified script type."""
        return [
            go
            for go in self.gameobjects
            if any(isinstance(script, script_type) for script in go.scripts)
        ]

    def find(self, name: str) -> GameObject | None:
        """Find a GameObject by its name."""
        for go in self.gameobjects:
            if go.name == name:
                return go
        return None

    def register_obj(self, gameobject: GameObject):
        """Register a GameObject with the GameManager."""
        self.gameobjects.append(gameobject)

    def unregister_obj(self, gameobject: GameObject):
        """Unregister a GameObject from the GameManager."""
        if gameobject in self.gameobjects:
            self.gameobjects.remove(gameobject)

    def update(self, delta_time: float):
        # Forward update call
        for go in self.gameobjects:
            go.update(delta_time)

        # Calculate and set game state
        self._handle_state(delta_time)

    def exit(self):
        for paddle in [go.get_script(Paddle) for go in self.find_by_script(Paddle)]:
            paddle.disconnect()

    def _handle_state(self, delta_time: float):
        """Handle the state transitions of the game."""

        ball = self.find("Ball").get_script(
            Ball) if self.find("Ball") else None
        paddles = self.find_by_script(Paddle)
        paddle_left = next(
            (p.get_script(Paddle)
             for p in paddles if p.name == "Paddle Left"), None
        )
        paddle_right = next(
            (p.get_script(Paddle)
             for p in paddles if p.name == "Paddle Right"), None
        )

        if not ball or not paddle_left or not paddle_right:
            raise ValueError("GameManager is missing required game objects.")

        # Only update paddles if the game is in PLAYING state
        if self.state == GameState.PLAYING:
            for go in [go for go in self.gameobjects if go.tag == "paddle"]:
                go.update(delta_time)

        # State transitions
        if self.state == GameState.INACTIVE:
            if paddle_left.is_connected() or paddle_right.is_connected():
                self.state = GameState.WAITING

        elif self.state == GameState.WAITING:
            # Wait for button_1 from either player
            if paddle_left.is_ready() and paddle_right.is_ready():
                ball.gameobject.set_velocity(
                    (
                        paddle_left.gameobject.get_center()
                        - ball.gameobject.get_center()
                    ).normalize()
                    * INITIAL_BALL_SPEED
                )
                self.state = GameState.PLAYING

        elif self.state == GameState.PLAYING:
            # Check if ball is out of bounds on the x axis and set score/state accordingly
            if ball.gameobject.out_of_bounds_hor:
                # Spawn confetti for scored point at ball position in the opposite direction of its velocity
                self._spawn_confetti(ball)

                if ball.gameobject.shape.x < 0:
                    paddle_right.score += 1
                    self.last_scorer = paddle_right
                else:
                    paddle_left.score += 1
                    self.last_scorer = paddle_left

                # Check for win condition
                if paddle_left.score >= WIN_CONDITION:
                    self.winner = paddle_left
                    self.state = GameState.GAME_OVER
                elif paddle_right.score >= WIN_CONDITION:
                    self.winner = paddle_right
                    self.state = GameState.GAME_OVER
                else:
                    self.state = GameState.RESETTING
                    self.reset_timer = RESET_DURATION

        elif self.state == GameState.RESETTING:
            self.reset_timer -= delta_time
            paddle_left.gameobject.set_velocity(Vector2D(0, 0))
            paddle_right.gameobject.set_velocity(Vector2D(0, 0))
            if self.reset_timer <= 0:
                self.reset()

        elif self.state == GameState.GAME_OVER:
            # Wait for both players to press button_1, then reset scores and game
            if paddle_left.is_ready() and paddle_right.is_ready():
                self.reset_scores()
                self.winner = None
                self.last_scorer = None
                self.state = GameState.INACTIVE
                self.reset()

    def _spawn_confetti(self, ball: "Ball"):
        player = self.win_audio.play()
        player.volume = 0.3
        for i in range(15):
            confetti = GameObject.create(
                        shapes.Rectangle(
                            ball.gameobject.shape.x,
                            ball.gameobject.shape.y,
                            width=3,
                            height=3,
                            color=(random.randint(50, 255), random.randint(
                                50, 255), random.randint(50, 255), random.randint(150, 255)),
                            batch=gameobject_batch,
                        ),
                        name="Confetti",
                        tag="confetti",
                        collision=False,
                        gravity=True,
                    )
            dir = Vector2D(
                        -ball.gameobject.velocity.x,
                        0,
                    )

            confetti.set_velocity(
                        dir.rotate_angle(random.uniform(-15, 15)).normalize() * INITIAL_BALL_SPEED * random.uniform(0.8, 1.2)
                    )
            confetti.set_position(
                min(max(ball.gameobject.shape.x, confetti.shape.width / 2), self.window.width - confetti.shape.width / 2),
                ball.gameobject.shape.y,
            )
            confetti.register_script(Confetti(confetti))
