import pygame
from Engine.MatrixMath import Vector3, Matrix4
from Engine.ObjectLoader import ObjectLoader
from Engine.Mesh import Mesh


class Helicopter:
    def __init__(self, x=0, y=0, z=0):
        # State
        self.pos = Vector3(x, y, z)
        self.vel = Vector3(0, 0, 0)
        self.yaw = 0.0
        self.pitch = 0.0
        self.roll = 0.0
        self.throttle = 0.0

        # Physics Constants
        self.mass = 1000.0
        self.drag_factor = 0.05
        self.gravity = 9.81
        self.max_thrust = 16000.0

        try:
            self.mesh = ObjectLoader.load_obj(
                "9 - 3D Rotorcraft/Assets/helicopter288.obj")
        except:
            self.mesh = Mesh.make_cube()

    def update(self, dt, terrain):
        keys = pygame.key.get_pressed()

        # Throttle Control
        if keys[pygame.K_SPACE]:
            self.throttle += 80.0 * dt
        else:
            self.throttle -= 50.0 * dt
        self.throttle = max(0.0, min(100.0, self.throttle))

        # Cyclic Control
        tilt_speed = 60.0 * dt
        if keys[pygame.K_w]:
            self.pitch += tilt_speed
        if keys[pygame.K_s]:
            self.pitch -= tilt_speed
        if keys[pygame.K_a]:
            self.roll += tilt_speed
        if keys[pygame.K_d]:
            self.roll -= tilt_speed
        if keys[pygame.K_q]:
            self.yaw -= tilt_speed
        if keys[pygame.K_e]:
            self.yaw += tilt_speed

        # Auto-stabilization
        self.pitch *= 0.98
        self.roll *= 0.98

        # Forces
        gravity_force = Vector3(0, -self.gravity * self.mass, 0)

        # Lift & Orientation
        mat_orient = Matrix4.make_rotation_y(self.yaw) @ \
            (Matrix4.make_rotation_x(self.pitch)
             @ Matrix4.make_rotation_z(self.roll))

        world_lift_dir = mat_orient.multiply_vector(
            Vector3(0, 1, 0)).normalize()
        base_lift = (self.throttle / 100.0) * self.max_thrust

        # Ground Effect
        ground_h = terrain.get_height(self.pos.x, self.pos.z)
        altitude = self.pos.y - ground_h
        lift_multiplier = 1.0

        if 0 < altitude < 15.0:
            factor = (15.0 - altitude) / 15.0
            lift_multiplier = 1.0 + (0.4 * factor * factor)

        lift_force = world_lift_dir * (base_lift * lift_multiplier)
        drag_force = self.vel * -1.0 * self.drag_factor * self.mass

        # Integration
        total_force = gravity_force + lift_force + drag_force
        self.vel = self.vel + ((total_force / self.mass) * dt)
        self.pos = self.pos + (self.vel * dt)

        # Ground Collision
        if self.pos.y < ground_h + 1.0:
            self.pos.y = ground_h + 1.0
            self.vel.y = -self.vel.y * 0.3 if self.vel.y < -5.0 else 0

            # Ground Friction
            self.vel.x *= 0.92
            self.vel.z *= 0.92
            if abs(self.vel.x) < 0.05:
                self.vel.x = 0
            if abs(self.vel.z) < 0.05:
                self.vel.z = 0

    def get_world_matrix(self):
        scale = 2.0
        mat_scale = Matrix4.make_scaling(scale, scale, scale)
        mat_correction = Matrix4.make_rotation_y(-90.0)

        mat_rot = Matrix4.make_rotation_y(self.yaw) @ \
            (Matrix4.make_rotation_x(self.pitch)
             @ Matrix4.make_rotation_z(self.roll))

        mat_trans = Matrix4.make_translation(
            self.pos.x, self.pos.y, self.pos.z)
        return mat_trans @ (mat_rot @ (mat_correction @ mat_scale))
