import pyglet
from typing import TYPE_CHECKING, Optional, Tuple
from config import (
    PLAYER_1_PORT, PLAYER_2_PORT, FONT_SIZE, VERTICAL_LABEL_MARGIN
)
from util import GameState, ui_batch

if TYPE_CHECKING:
    from game import GameWindow
    from player import Player


class Text(pyglet.text.Label):
    def __init__(self, text: str, x: int, y: int, font_size: int, color: Optional[Tuple[int, int, int, int]] = (255, 255, 255, 255)) -> None:
        super().__init__(
            text=text,
            x=x, y=y,
            anchor_x="center", anchor_y="center",
            font_size=font_size,
            color=color,
            batch=ui_batch,
        )


class GameUI:
    game_state: pyglet.text.Label
    score_left: pyglet.text.Label
    score_right: pyglet.text.Label
    conn_info_left: pyglet.text.Label
    conn_info_right: pyglet.text.Label

    def __init__(self, window: "GameWindow", player_1: "Player", player_2: "Player") -> None:
        self.window = window
        self.player_left = player_1
        self.player_right = player_2
        self.setup_labels()

    def setup_labels(self) -> None:
        center_x: int = self.window.width // 2
        y_offset: int = self.window.height - VERTICAL_LABEL_MARGIN - FONT_SIZE // 2
        score_x_offset: int = 150

        # Center label
        self.game_state = Text(
            '', center_x, y_offset,
            FONT_SIZE, color=(255, 255, 255, 70)
        )

        # Score labels
        y: int = self.game_state.y - VERTICAL_LABEL_MARGIN - FONT_SIZE // 2
        self.score_left = Text(str(self.player_left.score),
                             center_x - score_x_offset, y, FONT_SIZE)
        self.score_right = Text(str(self.player_right.score),
                             center_x + score_x_offset, y, FONT_SIZE)

        # Port labels
        y: int = self.score_left.y - VERTICAL_LABEL_MARGIN // 2 - FONT_SIZE // 2
        self.conn_info_left = Text(
            f"Port: {PLAYER_1_PORT}", center_x - score_x_offset, y, FONT_SIZE // 1.5, color=(255, 255, 255, 70)
        )
        self.conn_info_right = Text(
            f"Port: {PLAYER_2_PORT}", center_x + score_x_offset, y, FONT_SIZE // 1.5, color=(255, 255, 255, 70)
        )

    def update(self, delta_time: float) -> None:
        self.score_left.text = str(self.player_left.score)
        self.score_right.text = str(self.player_right.score)
        self.conn_info_right.text = self.get_conn_info_text(self.player_right)
        self.conn_info_left.text = self.get_conn_info_text(self.player_left)
        self.game_state.text = self.get_status_text()
                
    def get_conn_info_text(self, player: "Player") -> str:
        if player.is_connected():
            return f"{player._port} (Connected)"
        else:
            return f"{player._port} (NPC)"
    
    def get_status_text(self) -> str:
        if not(self.player_left.is_connected() or self.player_right.is_connected()):
            self.game_state.color = (255, 220, 5, 200)
            return "Use the DIPPID app to connect to the ports below!"
        elif self.window.game_manager.state == GameState.INACTIVE or self.window.game_manager.state == GameState.WAITING:
            self.game_state.color = (100, 255, 100, 200)
            num_connected_players = len([p for p in [self.player_left, self.player_right] if p.is_connected()])
            num_ready_players = len([p for p in [self.player_left, self.player_right] if p.is_ready() and p.is_connected()])
            return f"Press button_1 to ready up! ({num_ready_players}/{num_connected_players})"
        elif self.window.game_manager.state == GameState.RESETTING:
            self.game_state.color = (100, 255, 100, 200)
            return f"{self.window.game_manager.last_scorer._port} scored!"
        else:
            self.game_state.color = (255, 255, 255, 120)
            return "Score"