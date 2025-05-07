from src.script import Script

class Confetti(Script):
    def __init__(self, gameobject):
        super().__init__()
        self.gameobject = gameobject

    def update(self, delta_time):
        if self.gameobject.out_of_bounds_hor or self.gameobject.out_of_bounds_ver:
            self.gameobject.destroy()
