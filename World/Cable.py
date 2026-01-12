import math
from Engine.MatrixMath import Vector3


class Cable:
    def __init__(self, num_segments=10, total_length=15.0):
        self.num_segments = num_segments
        self.total_length = total_length
        self.segment_length = total_length / num_segments

        self.nodes = [Vector3(0, 0, 0) for _ in range(num_segments + 1)]
        self.old_nodes = [Vector3(0, 0, 0) for _ in range(num_segments + 1)]

    def update(self, dt, start_pos, end_pos):
        gravity = Vector3(0, -9.81, 0)

        # 1. Verlet Integration
        for i in range(1, self.num_segments):
            vel_x = (self.nodes[i].x - self.old_nodes[i].x) * 0.99
            vel_y = (self.nodes[i].y - self.old_nodes[i].y) * 0.99
            vel_z = (self.nodes[i].z - self.old_nodes[i].z) * 0.99

            self.old_nodes[i].x = self.nodes[i].x
            self.old_nodes[i].y = self.nodes[i].y
            self.old_nodes[i].z = self.nodes[i].z

            self.nodes[i].x += vel_x + (gravity.x * dt * dt)
            self.nodes[i].y += vel_y + (gravity.y * dt * dt)
            self.nodes[i].z += vel_z + (gravity.z * dt * dt)

        # 2. Constraint Solving
        for _ in range(5):
            self.apply_constraints(start_pos, end_pos)

    def apply_constraints(self, start_pos, end_pos):
        self.nodes[0] = start_pos
        self.nodes[-1] = end_pos

        for i in range(self.num_segments):
            node1 = self.nodes[i]
            node2 = self.nodes[i+1]

            dx, dy, dz = node2.x - node1.x, node2.y - node1.y, node2.z - node1.z
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            if dist == 0:
                continue

            diff = dist - self.segment_length
            percent = (diff / dist) * 0.5

            offset_x, offset_y, offset_z = dx * percent, dy * percent, dz * percent

            if i != 0:
                self.nodes[i].x += offset_x
                self.nodes[i].y += offset_y
                self.nodes[i].z += offset_z

            if i + 1 != self.num_segments:
                self.nodes[i+1].x -= offset_x
                self.nodes[i+1].y -= offset_y
                self.nodes[i+1].z -= offset_z
