from __future__ import annotations
import math
from typing import TYPE_CHECKING, List, Literal, Type, TypeVar
from src.gameobject import GameObject
from config import INITIAL_BALL_SIZE, INITIAL_BALL_SPEED,  PLAYER_1_PORT, PLAYER_2_PORT, WIN_CONDITION
from src.util import GameState, Vector2D
from pyglet import shapes
from src.scripts.ball import Ball
from src.scripts.paddle import Paddle
from src.scripts.border import Border
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
        
        # Init Ball
        ball_shape = shapes.RoundedRectangle(
            self.window.width / 2,
            self.window.height / 2,
            width=INITIAL_BALL_SIZE,
            height=INITIAL_BALL_SIZE,
            radius=INITIAL_BALL_SIZE / 2,
            color=(255, 255, 255),
            batch=gameobject_batch,
        )
        ball = GameObject.create(self, ball_shape, name="Ball", tag="ball", collision=True)
        ball.register_script(Ball(ball))
        
        # Init Paddles
        def init_paddle(side: Literal["left", "right"]) -> GameObject:
            width = 35
            height = 250     
            paddle_shape = shapes.RoundedRectangle(
                20 if side == "left" else self.window.width - 20 - width,
                self.window.height / 2 - height / 2,
                width=width,
                height=height,
                radius=math.pi,
                color=(255, 255, 255),
                batch=gameobject_batch,
            )
            
            paddle = GameObject.create(self, paddle_shape, name="Paddle Left" if side == "left" else "Paddle Right", tag="paddle", collision=True)
            paddle.register_script(Paddle(paddle, PLAYER_1_PORT if side == "left" else PLAYER_2_PORT))
            return paddle
        
        init_paddle("left")
        init_paddle("right")
        
        # Init Borders
        def init_border(side: Literal["top", "bottom"]) -> GameObject:
            width = self.window.width
            height = 10
            border_shape = shapes.RoundedRectangle(
                x=0,
                y=self.window.height - height if side == "top" else 0,
                width=width,
                height=height,
                radius=math.pi,
                color=(255, 255, 255, 150),
                batch=gameobject_batch,
            )
            border = GameObject.create(self, border_shape, name="Border Top" if side == "top" else "Border Bottom", tag="border", collision=True)
            border.register_script(Border(border, direction=1 if side == "top" else 2))
            return border
        
        init_border("top")
        init_border("bottom")

    def reset(self):
        ball = self.find("Ball")
        if not ball:
            raise ValueError("Ball not found in GameManager.")
        
        ball.set_position(self.window.width / 2, self.window.height / 2)
        ball.set_velocity(Vector2D(0, 0))
        ball.visible = False
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
        return [go for go in self.gameobjects if any(isinstance(script, script_type) for script in go.scripts)]
    
    def find(self, name: str) -> GameObject | None:
        """Find a GameObject by its name."""
        for go in self.gameobjects:
            if go.name == name:
                return go
        return None
        
    def register_go(self, gameobject: GameObject):
        """Register a GameObject with the GameManager."""
        self.gameobjects.append(gameobject)
        
    def unregister_go(self, gameobject: GameObject):
        """Unregister a GameObject from the GameManager."""
        if gameobject in self.gameobjects:
            self.gameobjects.remove(gameobject)

    def update(self, delta_time: float):
        # Forward update call
        for go in self.gameobjects:
            go.update(delta_time)

        ball = self.find("Ball").get_script(Ball) if self.find("Ball") else None
        paddles = self.find_by_script(Paddle)
        paddle_left = next((p.get_script(Paddle) for p in paddles if p.name == "Paddle Left"), None)
        paddle_right = next((p.get_script(Paddle) for p in paddles if p.name == "Paddle Right"), None)
        
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
                    (paddle_left.gameobject.get_center() - ball.gameobject.get_center()).normalize()
                    * INITIAL_BALL_SPEED
                )
                self.state = GameState.PLAYING

        elif self.state == GameState.PLAYING:
            # Check if ball is out of bounds and set score/state accordingly
            if not ball.gameobject.visible:
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
                    self.reset_timer = 1.0

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

    def exit(self):
        for paddle in [go.get_script(Paddle) for go in self.find_by_script(Paddle)]:
            paddle.disconnect()
