import random
from Engine.MatrixMath import Vector3


class Cloud:
    def __init__(self, x, y, z):
        self.pos = Vector3(x, y, z)
        self.velocity = Vector3(random.uniform(
            0.5, 2.0), 0, random.uniform(0.1, 0.5))
        self.puffs = []

        base_size = random.uniform(8.0, 15.0)
        for _ in range(random.randint(3, 6)):
            ox = random.uniform(-10, 10)
            oy = random.uniform(-5, 5)
            oz = random.uniform(-10, 10)
            size = base_size * random.uniform(0.8, 1.2)
            self.puffs.append((Vector3(ox, oy, oz), size))

    def update(self, dt, world_size):
        # Drift
        self.pos.x += self.velocity.x * dt
        self.pos.z += self.velocity.z * dt

        # Wrap
        half_world = (world_size * 10.0) / 2.0
        if self.pos.x > half_world:
            self.pos.x -= half_world * 2
        if self.pos.x < -half_world:
            self.pos.x += half_world * 2
        if self.pos.z > half_world:
            self.pos.z -= half_world * 2
        if self.pos.z < -half_world:
            self.pos.z += half_world * 2
