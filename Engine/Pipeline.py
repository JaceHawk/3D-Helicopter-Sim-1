import math
from Engine.MatrixMath import Matrix4, Vector3


class Pipeline:
    def __init__(self, width, height, fov=90.0):
        self.width = width
        self.height = height
        self.aspect_ratio = height / width
        self.mat_proj = Matrix4.make_projection(
            fov, self.aspect_ratio, 0.1, 1000.0)

    def process_mesh(self, mesh, camera, world_matrix, base_color=None):
        triangles_to_draw = []
        mat_view = camera.get_view_matrix()

        for tri in mesh.triangles:
            tri_projected = [Vector3(), Vector3(), Vector3()]

            p0_trans = world_matrix.multiply_vector(tri.p[0])
            p1_trans = world_matrix.multiply_vector(tri.p[1])
            p2_trans = world_matrix.multiply_vector(tri.p[2])

            p0_view = mat_view.multiply_vector(p0_trans)
            p1_view = mat_view.multiply_vector(p1_trans)
            p2_view = mat_view.multiply_vector(p2_trans)

            # Backface Culling
            line1 = p1_view - p0_view
            line2 = p2_view - p0_view
            normal_view = line1.cross(line2).normalize()
            if normal_view.dot(p0_view.normalize()) > 0:
                continue

            # Near Plane Culling (Z check)
            if p0_view.z < 0.1 or p1_view.z < 0.1 or p2_view.z < 0.1:
                continue

            # Projection
            p0_proj = self.mat_proj.multiply_vector(p0_view)
            p1_proj = self.mat_proj.multiply_vector(p1_view)
            p2_proj = self.mat_proj.multiply_vector(p2_view)

            if p0_proj.w != 0:
                p0_proj = p0_proj / p0_proj.w
            if p1_proj.w != 0:
                p1_proj = p1_proj / p1_proj.w
            if p2_proj.w != 0:
                p2_proj = p2_proj / p2_proj.w

            # Screen Map
            p0_proj.x = (p0_proj.x + 1.0) * 0.5 * self.width
            p0_proj.y = (1.0 - p0_proj.y) * 0.5 * self.height
            p1_proj.x = (p1_proj.x + 1.0) * 0.5 * self.width
            p1_proj.y = (1.0 - p1_proj.y) * 0.5 * self.height
            p2_proj.x = (p2_proj.x + 1.0) * 0.5 * self.width
            p2_proj.y = (1.0 - p2_proj.y) * 0.5 * self.height

            tri_projected[0] = p0_proj
            tri_projected[1] = p1_proj
            tri_projected[2] = p2_proj

            # Lighting
            avg_depth = max(p0_view.z, p1_view.z, p2_view.z)
            color_to_use = base_color if base_color else tri.color

            line1_world = p1_trans - p0_trans
            line2_world = p2_trans - p0_trans
            normal_world = line1_world.cross(line2_world).normalize()
            brightness = max(0.2, normal_world.dot(Vector3(0, 0, -1)))

            final_color = (
                int(color_to_use[0] * brightness),
                int(color_to_use[1] * brightness),
                int(color_to_use[2] * brightness)
            )

            triangles_to_draw.append(
                (tri_projected, avg_depth, final_color, tri.edge_flags))

        triangles_to_draw.sort(key=lambda x: x[1], reverse=True)
        return triangles_to_draw

    def project_clipped_line(self, start_pos, end_pos, camera):
        mat_view = camera.get_view_matrix()
        v1 = mat_view.multiply_vector(start_pos)
        v2 = mat_view.multiply_vector(end_pos)
        near = 1.0

        if v1.z < near and v2.z < near:
            return None

        # Clipping
        if v1.z < near:
            t = (near - v1.z) / (v2.z - v1.z)
            v1 = v1 + ((v2 - v1) * t)
        elif v2.z < near:
            t = (near - v2.z) / (v1.z - v2.z)
            v2 = v2 + ((v1 - v2) * t)

        # Project
        p1_proj = self.mat_proj.multiply_vector(v1)
        if p1_proj.w != 0:
            p1_proj.x /= p1_proj.w
            p1_proj.y /= p1_proj.w

        s1_x = (p1_proj.x + 1.0) * 0.5 * self.width
        s1_y = (1.0 - p1_proj.y) * 0.5 * self.height

        p2_proj = self.mat_proj.multiply_vector(v2)
        if p2_proj.w != 0:
            p2_proj.x /= p2_proj.w
            p2_proj.y /= p2_proj.w

        s2_x = (p2_proj.x + 1.0) * 0.5 * self.width
        s2_y = (1.0 - p2_proj.y) * 0.5 * self.height

        return ((s1_x, s1_y), (s2_x, s2_y))
