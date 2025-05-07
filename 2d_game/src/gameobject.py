from __future__ import annotations
from pyglet import shapes
from src.util import Vector2D
from typing import List, TYPE_CHECKING
from typing import Type, TypeVar, Optional

if TYPE_CHECKING:
    from src.script import Script
    from src.managers.game_manager import GameManager

T = TypeVar("T", bound="Script")


class GameObject:
    visible: bool = True

    def __init__(
        self,
        gm: "GameManager",
        shape: shapes.RoundedRectangle,
        name: str = "",
        tag: str = "",
        collision: bool = True,
    ):
        self.velocity = Vector2D(0, 0)
        self.gm = gm
        self.shape = shape
        self.name = name
        self.tag = tag
        self.collision = collision
        self.scripts: List["Script"] = []
        # Store previous position for collision sweeping
        self.prev_x = self.shape.x
        self.prev_y = self.shape.y
        gm.register_obj(self)

    @staticmethod
    def create(
        game_manager: "GameManager",
        shape,
        name: str = "",
        tag: str = "",
        collision: bool = True,
    ):
        obj = GameObject(game_manager, shape, name, tag, collision)
        return obj

    def get_script(self, script_type: Type[T]) -> Optional[T]:
        for script in self.scripts:
            if isinstance(script, script_type):
                return script
        return None

    def register_script(self, script: "Script"):
        self.scripts.append(script)
        script.gameobject = self

    def get_center(self) -> Vector2D:
        return Vector2D(
            self.shape.x + self.shape.width / 2, self.shape.y + self.shape.height / 2
        )

    def update(self, delta_time: float):
        # Store previous position before moving
        self.prev_x = self.shape.x
        self.prev_y = self.shape.y
        self.shape.position = (
            self.shape.x + self.velocity.x * delta_time,
            self.shape.y + self.velocity.y * delta_time,
        )
        for script in self.scripts:
            script.update(delta_time)

    def on_collision_start(self, other: "GameObject"):
        """Called when a collision starts with another GameObject"""
        for script in self.scripts:
            script.on_collision_start(other)

    def on_collision_end(self, other: "GameObject"):
        """Called when a collision ends with another GameObject"""
        for script in self.scripts:
            script.on_collision_end(other)

    def destroy(self):
        self.visible = False
        self.scripts.clear()
        self.gm.unregister_obj(self)

    def set_position(self, x: float, y: float):
        self.shape.x = x
        self.shape.y = y

    def set_velocity(self, velocity: Vector2D):
        self.velocity = velocity

    def __contains__(self, point: tuple[float, float]) -> bool:
        """Check if the point is inside the shape"""
        return point in self.shape
