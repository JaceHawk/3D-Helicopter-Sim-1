import random
from Engine.MatrixMath import Vector3


class Particle:
    def __init__(self, x, y, z, velocity):
        self.pos = Vector3(x, y, z)
        self.vel = velocity
        self.life = 1.0
        self.decay = random.uniform(0.01, 0.03)
        self.base_size = random.uniform(0.5, 1.5)
        self.growth_rate = 2.0

    def update(self, dt):
        self.pos.x += self.vel.x * dt
        self.pos.y += self.vel.y * dt
        self.pos.z += self.vel.z * dt

        self.vel = self.vel * 0.95  # Drag
        self.life -= self.decay
        self.base_size += self.growth_rate * dt

    def is_dead(self):
        return self.life <= 0.0
