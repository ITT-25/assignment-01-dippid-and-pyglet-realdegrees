from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.gameobject import GameObject


class Script:
    def __init__(self):
        self.gameobject: "GameObject" = (
            None  # Will be set when registered to a GameObject
        )

    @abstractmethod
    def update(self, delta_time: float):
        pass  # Override in subclasses for custom logic

    @abstractmethod
    def on_collision_start(self, other: "GameObject"):
        pass

    @abstractmethod
    def on_collision_end(self, other: "GameObject"):
        pass
