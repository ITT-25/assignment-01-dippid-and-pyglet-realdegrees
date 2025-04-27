from __future__ import annotations
from pyglet.graphics import Batch
from enum import Enum, auto


class GameState(Enum):
    INACTIVE = auto()
    WAITING = auto()
    PLAYING = auto()
    RESETTING = auto()


gameobject_batch = Batch()
ui_batch = Batch()


class Vector2D:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def length(self) -> float:
        """Calculate the length of the vector."""
        return (self.x**2 + self.y**2) ** 0.5

    def normalize(self) -> Vector2D:
        """Normalize the vector to a length of 1."""
        length = self.length()
        if length == 0:
            return Vector2D(0, 0)
        return self / length

    def reflect(self, normal: Vector2D) -> Vector2D:
        """Reflect the vector on a normal vector."""
        dot_product = self.x * normal.x + self.y * normal.y
        return Vector2D(
            self.x - 2 * dot_product * normal.x, self.y - 2 * dot_product * normal.y
        )

    @staticmethod
    def lerp(a: Vector2D, b: Vector2D, t: float) -> Vector2D:
        """Linearly interpolate between two vectors."""
        return Vector2D(a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t)

    def __add__(self, other: Vector2D):
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2D):
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float | Vector2D):
        if isinstance(scalar, Vector2D):
            return Vector2D(self.x * scalar.x, self.y * scalar.y)
        return Vector2D(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float):
        return Vector2D(self.x / scalar, self.y / scalar)

    def __neg__(self):
        """Return the negation of the vector."""
        return Vector2D(-self.x, -self.y)
