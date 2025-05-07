from typing import TYPE_CHECKING, List
from src.gameobject import GameObject

if TYPE_CHECKING:
    from game import GameWindow
    from src.managers.game_manager import GameManager


class CollisionManager:
    def __init__(self, window: "GameWindow", game_manager: "GameManager"):
        self.collisions: List[tuple[GameObject, GameObject]] = []
        self.window = window
        self.game_manager = game_manager

    def update(self, delta_time: float):
        objects = self.game_manager.gameobjects
        for i in range(len(objects)):
            if not objects[i].collision:
                continue

            out_of_bounds = self.check_out_of_bounds(objects[i])
            objects[i].visible = not out_of_bounds

            for j in range(i + 1, len(objects)):
                obj1 = objects[i]
                obj2 = objects[j]
                is_colliding = self.check_collision(obj1, obj2)
                was_colliding = self.collisions.count((obj1, obj2)) > 0
                if is_colliding and not was_colliding:
                    obj1.on_collision_start(obj2)
                    obj2.on_collision_start(obj1)
                    self.collisions.append((obj1, obj2))
                elif not is_colliding and was_colliding:
                    obj1.on_collision_end(obj2)
                    obj2.on_collision_end(obj1)
                    self.collisions.remove((obj1, obj2))

    def check_collision(self, obj1: GameObject, obj2: GameObject) -> bool:
        """
        Checks for collision between two game objects using continuous collision detection (CCD).
        It interpolates the movement of each corner of the first object (obj1) from its previous
        position to its current position and checks if any of these interpolated points
        are inside the second object (obj2).
        """
        COLLISION_ACCURACY = 10
        corners_prev = [
            (obj1.prev_x, obj1.prev_y),
            (obj1.prev_x + obj1.shape.width, obj1.prev_y),
            (obj1.prev_x, obj1.prev_y + obj1.shape.height),
            (obj1.prev_x + obj1.shape.width, obj1.prev_y + obj1.shape.height),
        ]
        corners_curr = [
            (obj1.shape.x, obj1.shape.y),
            (obj1.shape.x + obj1.shape.width, obj1.shape.y),
            (obj1.shape.x, obj1.shape.y + obj1.shape.height),
            (obj1.shape.x + obj1.shape.width, obj1.shape.y + obj1.shape.height),
        ]
        for corner_index in range(4):
            prev_corner_x, prev_corner_y = corners_prev[corner_index]
            curr_corner_x, curr_corner_y = corners_curr[corner_index]
            for step in range(COLLISION_ACCURACY + 1):
                interpolation_factor = step / COLLISION_ACCURACY
                interpolated_x = (
                    prev_corner_x
                    + (curr_corner_x - prev_corner_x) * interpolation_factor
                )
                interpolated_y = (
                    prev_corner_y
                    + (curr_corner_y - prev_corner_y) * interpolation_factor
                )
                if (interpolated_x, interpolated_y) in obj2:
                    return True
        return False

    def check_out_of_bounds(self, obj: GameObject) -> bool:
        return (
            obj.shape.x + obj.shape.width < 0
            or obj.shape.x > self.game_manager.window.width
            or obj.shape.y + obj.shape.height < 0
            or obj.shape.y > self.game_manager.window.height
        )
