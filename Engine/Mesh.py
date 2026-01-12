from Engine.MatrixMath import Vector3


class Triangle:
    def __init__(self, p1, p2, p3, flags=None):
        self.p = [p1, p2, p3]
        self.normal = Vector3()
        self.color = (255, 255, 255)
        self.edge_flags = flags if flags is not None else [True, True, True]


class Mesh:
    def __init__(self):
        self.triangles = []

    @staticmethod
    def make_cube():
        mesh = Mesh()
        verts = [
            Vector3(-0.5, -0.5, -0.5), Vector3(-0.5, 0.5, -0.5),
            Vector3(0.5, 0.5, -0.5),   Vector3(0.5, -0.5, -0.5),
            Vector3(-0.5, -0.5, 0.5),  Vector3(-0.5, 0.5, 0.5),
            Vector3(0.5, 0.5, 0.5),    Vector3(0.5, -0.5, 0.5)
        ]
        indices = [
            0, 1, 2, 0, 2, 3, 3, 2, 6, 3, 6, 7,
            7, 6, 5, 7, 5, 4, 4, 5, 1, 4, 1, 0,
            1, 5, 6, 1, 6, 2, 4, 0, 3, 4, 3, 7
        ]
        for i in range(0, len(indices), 3):
            mesh.triangles.append(
                Triangle(verts[indices[i]], verts[indices[i+1]], verts[indices[i+2]]))
        return mesh

    @staticmethod
    def make_flat_quad(size=1.0):
        mesh = Mesh()
        s = size / 2.0
        p1, p2 = Vector3(-s, 0, -s), Vector3(s, 0, -s)
        p3, p4 = Vector3(s, 0, s), Vector3(-s, 0, s)

        t1 = Triangle(p1, p3, p2)
        t1.color = (50, 50, 50)
        t2 = Triangle(p1, p4, p3)
        t2.color = (50, 50, 50)

        mesh.triangles.append(t1)
        mesh.triangles.append(t2)
        return mesh
