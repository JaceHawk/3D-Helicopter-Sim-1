import math
from Engine.MatrixMath import Vector3
from Engine.Mesh import Mesh, Triangle


class Terrain:
    def __init__(self, width=40, depth=40, scale=20.0):
        self.width = width
        self.depth = depth
        self.scale = scale
        self.mesh = self.generate_mesh()

    def get_height(self, x, z):
        # Base Terrain
        h1 = math.sin(x * 0.04) * math.cos(z * 0.04) * 40.0
        h2 = math.sin((x + 15.2) * 0.1) * math.cos((z - 20.1) * 0.1) * 10.0
        h3 = math.sin(x * 0.25) * math.cos(z * 0.23) * 0.8
        raw_height = h1 + h2 + h3

        # Landing Pad Flattening
        dist = math.sqrt(x*x + z*z)
        flat_radius = 16.0
        blend_radius = 75.0

        if dist < flat_radius + 10.0:
            return 0.0
        elif dist < blend_radius:
            factor = (dist - flat_radius) / (blend_radius - flat_radius)
            # Smoothstep
            smooth_factor = 3 * factor * factor - 2 * factor * factor * factor
            return raw_height * smooth_factor
        return raw_height

    def generate_mesh(self):
        mesh = Mesh()
        verts = []
        start_x = -(self.width * self.scale) / 2.0
        start_z = -(self.depth * self.scale) / 2.0

        # Vertices
        for z in range(self.depth + 1):
            for x in range(self.width + 1):
                wx = start_x + (x * self.scale)
                wz = start_z + (z * self.scale)
                wy = self.get_height(wx, wz)
                verts.append(Vector3(wx, wy, wz))

        # Triangles
        for z in range(self.depth):
            for x in range(self.width):
                row_len = self.width + 1
                p1_idx = z * row_len + x
                p2_idx = z * row_len + (x + 1)
                p3_idx = (z + 1) * row_len + x
                p4_idx = (z + 1) * row_len + (x + 1)

                v1, v2 = verts[p1_idx], verts[p2_idx]
                v3, v4 = verts[p3_idx], verts[p4_idx]

                # Altitude Color
                avg_h = (v1.y + v2.y + v3.y + v4.y) / 4.0
                if avg_h > 31.0:
                    col = (200, 200, 200)  # Snow
                elif avg_h > 5.0:
                    col = (34, 139, 34)   # Forest
                else:
                    col = (0, 100, 0)                 # Valley

                if math.sqrt(v1.x**2 + v1.z**2) < 15.0:
                    col = (50, 50, 50)  # Pad

                t1, t2 = Triangle(v1, v3, v2), Triangle(v2, v3, v4)
                t1.color = t2.color = col
                mesh.triangles.extend([t1, t2])

        return mesh
