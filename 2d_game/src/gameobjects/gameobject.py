from __future__ import annotations
from abc import abstractmethod
from pyglet import shapes
from src.util import Vector2D


class GameObject:
    visible: bool = True

    def __init__(self, shape: shapes.RoundedRectangle, window):
        self.velocity = Vector2D(0, 0)
        self.shape = shape
        self.window = window
        # Store previous position for collision sweeping
        self.prev_x = self.shape.x
        self.prev_y = self.shape.y

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

    @abstractmethod
    def destroy(self):
        pass

    @abstractmethod
    def on_collision_start(self, other: "GameObject"):
        pass

    @abstractmethod
    def on_collision_end(self, other: "GameObject"):
        pass

    def set_position(self, x: float, y: float):
        self.shape.x = x
        self.shape.y = y

    def set_velocity(self, velocity: Vector2D):
        self.velocity = velocity

    def __contains__(self, point: tuple[float, float]) -> bool:
        """Check if the point is inside the shape"""
        return point in self.shape
