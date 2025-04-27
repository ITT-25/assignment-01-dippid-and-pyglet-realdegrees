from typing import TYPE_CHECKING, List
from src.gameobjects.gameobject import GameObject

if TYPE_CHECKING:
    from game import GameWindow


class CollisionManager:
    def __init__(self, window: "GameWindow"):
        self.window = window
        self.objects: List[GameObject] = []
        self.collisions: List[tuple[GameObject, GameObject]] = []

    def add(self, *objs: GameObject):
        self.objects.extend(objs)

    def update(self, delta_time: float):
        for i in range(len(self.objects)):
            out_of_bounds = self.check_out_of_bounds(self.objects[i])
            self.objects[i].visible = not out_of_bounds

            for j in range(i + 1, len(self.objects)):
                obj1 = self.objects[i]
                obj2 = self.objects[j]
                is_colliding = self.check_collision(obj1, obj2)
                was_colliding = self.collisions.count((obj1, obj2)) > 0
                if is_colliding and not was_colliding:
                    print(
                        f"Collision detected between {obj1.__class__.__name__} and {obj2.__class__.__name__}"
                    )
                    obj1.on_collision_start(obj2)
                    obj2.on_collision_start(obj1)
                    self.collisions.append((obj1, obj2))
                elif not is_colliding and was_colliding:
                    print(
                        f"Collision ended between {obj1.__class__.__name__} and {obj2.__class__.__name__}"
                    )
                    obj1.on_collision_end(obj2)
                    obj2.on_collision_end(obj1)
                    self.collisions.remove((obj1, obj2))

    def check_collision(self, obj1: GameObject, obj2: GameObject) -> bool:
        COLLISION_ACCURACY = 50
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
            or obj.shape.x > self.window.width
            or obj.shape.y + obj.shape.height < 0
            or obj.shape.y > self.window.height
        )
