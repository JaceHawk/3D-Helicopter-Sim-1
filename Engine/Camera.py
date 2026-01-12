from Engine.MatrixMath import Vector3, Matrix4
import math
import pygame


class Camera:
    def __init__(self):
        self.mode = 'chase'
        self.pos = Vector3(0, -100, 0)
        self.yaw = 0.0
        self.pitch = 0.0
        self.follow_distance = 15.0

    def get_view_matrix(self):
        mat_trans = Matrix4.make_translation(
            -self.pos.x, -self.pos.y, -self.pos.z)
        mat_rot_y = Matrix4.make_rotation_y(-self.yaw)
        mat_rot_x = Matrix4.make_rotation_x(-self.pitch)
        return mat_rot_x @ mat_rot_y @ mat_trans

    def chase(self, target):
        self.yaw = target.yaw
        dist = self.follow_distance

        rad_yaw = math.radians(self.yaw)
        rad_pitch = math.radians(self.pitch)

        fx = math.sin(rad_yaw) * math.cos(rad_pitch)
        fy = -math.sin(rad_pitch)
        fz = math.cos(rad_yaw) * math.cos(rad_pitch)

        self.pos.x = target.pos.x - (fx * dist)
        self.pos.y = target.pos.y - (fy * dist)
        self.pos.z = target.pos.z - (fz * dist)

    def update(self, keys, mouse_delta):
        dx, dy = mouse_delta
        sensitivity = 0.2
        self.yaw += dx * sensitivity
        self.pitch -= dy * sensitivity
        self.pitch = max(-89.0, min(89.0, self.pitch))

        base_speed = 6.0
        if keys[pygame.K_LSHIFT]:
            speed = base_speed * 10.0
        elif keys[pygame.K_LCTRL]:
            speed = base_speed * 1/3
        else:
            speed = base_speed

        rad_yaw = math.radians(self.yaw)
        if keys[pygame.K_w]:
            self.pos.x += math.sin(rad_yaw) * speed
            self.pos.z += math.cos(rad_yaw) * speed
        if keys[pygame.K_s]:
            self.pos.x -= math.sin(rad_yaw) * speed
            self.pos.z -= math.cos(rad_yaw) * speed
        if keys[pygame.K_a]:
            self.pos.x -= math.cos(rad_yaw) * speed
            self.pos.z += math.sin(rad_yaw) * speed
        if keys[pygame.K_d]:
            self.pos.x += math.cos(rad_yaw) * speed
            self.pos.z -= math.sin(rad_yaw) * speed
        if keys[pygame.K_e]:
            self.pos.y -= speed
        if keys[pygame.K_q]:
            self.pos.y += speed

    def follow(self, target, mouse_delta):
        dx, dy = mouse_delta
        sensitivity = 0.2
        self.yaw += dx * sensitivity
        self.pitch -= dy * sensitivity
        self.pitch = max(-89.0, min(89.0, self.pitch))

        dist = self.follow_distance
        rad_yaw = math.radians(self.yaw)
        rad_pitch = math.radians(self.pitch)

        fx = math.sin(rad_yaw) * math.cos(rad_pitch)
        fy = -math.sin(rad_pitch)
        fz = math.cos(rad_yaw) * math.cos(rad_pitch)

        self.pos.x = target.pos.x - (fx * dist)
        self.pos.y = target.pos.y - (fy * dist)
        self.pos.z = target.pos.z - (fz * dist)
