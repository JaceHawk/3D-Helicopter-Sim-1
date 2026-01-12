import math


class Vector3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.w = 1.0

    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __truediv__(self, scalar):
        if scalar == 0:
            return Vector3()
        return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)

    def __repr__(self):
        return f"Vec3({self.x}, {self.y}, {self.z})"

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self):
        m = self.magnitude()
        if m == 0:
            return Vector3()
        return self / m

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def distance_to(self, other):
        return (self - other).magnitude()


class Matrix4:
    def __init__(self):
        self.m = [[0.0]*4 for _ in range(4)]
        self.m[0][0] = self.m[1][1] = self.m[2][2] = self.m[3][3] = 1.0

    def __matmul__(self, other):
        result = Matrix4()
        for i in range(4):
            for j in range(4):
                result.m[i][j] = sum(self.m[i][k] * other.m[k][j]
                                     for k in range(4))
        return result

    def multiply_vector(self, vec):
        x = vec.x * self.m[0][0] + vec.y * self.m[0][1] + \
            vec.z * self.m[0][2] + vec.w * self.m[0][3]
        y = vec.x * self.m[1][0] + vec.y * self.m[1][1] + \
            vec.z * self.m[1][2] + vec.w * self.m[1][3]
        z = vec.x * self.m[2][0] + vec.y * self.m[2][1] + \
            vec.z * self.m[2][2] + vec.w * self.m[2][3]
        w = vec.x * self.m[3][0] + vec.y * self.m[3][1] + \
            vec.z * self.m[3][2] + vec.w * self.m[3][3]
        result = Vector3(x, y, z)
        result.w = w
        return result

    @staticmethod
    def make_translation(x, y, z):
        mat = Matrix4()
        mat.m[0][3], mat.m[1][3], mat.m[2][3] = x, y, z
        return mat

    @staticmethod
    def make_rotation_z(angle_deg):
        mat = Matrix4()
        rad = math.radians(angle_deg)
        c, s = math.cos(rad), math.sin(rad)
        mat.m[0][0], mat.m[0][1] = c, -s
        mat.m[1][0], mat.m[1][1] = s, c
        return mat

    @staticmethod
    def make_rotation_x(angle_deg):
        mat = Matrix4()
        rad = math.radians(angle_deg)
        c, s = math.cos(rad), math.sin(rad)
        mat.m[1][1], mat.m[1][2] = c, -s
        mat.m[2][1], mat.m[2][2] = s, c
        return mat

    @staticmethod
    def make_rotation_y(angle_deg):
        mat = Matrix4()
        rad = math.radians(angle_deg)
        c, s = math.cos(rad), math.sin(rad)
        mat.m[0][0], mat.m[0][2] = c, s
        mat.m[2][0], mat.m[2][2] = -s, c
        return mat

    @staticmethod
    def make_projection(fov, aspect_ratio, near, far):
        mat = Matrix4()
        fov_rad = 1.0 / math.tan(math.radians(fov) / 2.0)
        mat.m[0][0] = aspect_ratio * fov_rad
        mat.m[1][1] = fov_rad
        mat.m[2][2] = far / (far - near)
        mat.m[2][3] = (-far * near) / (far - near)
        mat.m[3][2] = 1.0
        mat.m[3][3] = 0.0
        return mat

    @staticmethod
    def make_scaling(x, y, z):
        mat = Matrix4()
        mat.m[0][0], mat.m[1][1], mat.m[2][2] = x, y, z
        return mat
