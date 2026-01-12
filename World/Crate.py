from Engine.MatrixMath import Vector3, Matrix4
from Engine.Mesh import Mesh


class Crate:
    def __init__(self, x=0, y=0, z=0):
        self.pos = Vector3(x, y, z)
        self.vel = Vector3(0, 0, 0)
        self.mass = 300.0
        self.gravity = 9.81
        self.mesh = Mesh.make_cube()

    def update(self, dt, terrain):
        gravity_accel = Vector3(0, -self.gravity, 0)

        # Drag
        drag_force = self.vel * -0.5
        drag_accel = drag_force * (1.0 / self.mass)

        # Integration
        self.vel = self.vel + ((gravity_accel + drag_accel) * dt)
        self.pos = self.pos + (self.vel * dt)

        # Ground Collision
        ground_h = terrain.get_height(self.pos.x, self.pos.z)
        if self.pos.y < ground_h + 0.5:
            self.pos.y = ground_h + 0.5
            self.vel.y = -self.vel.y * 0.2 if self.vel.y < -2.0 else 0

            # Friction
            self.vel.x *= 0.80
            self.vel.z *= 0.80

    def get_world_matrix(self):
        mat_scale = Matrix4.make_scaling(1.0, 1.0, 1.0)
        mat_trans = Matrix4.make_translation(
            self.pos.x, self.pos.y, self.pos.z)
        return mat_trans @ mat_scale
