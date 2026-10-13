import math

from pyglet.math import Mat4, Vec3, Quaternion


class TrackballCamera:
    # 23 mm full-frame-equivalent focal length, using the photo's 4:3 aspect.
    VERTICAL_FOV = 58.87617286

    def __init__(self):
        # Pose fitted to the reference photo's back-wall corners and ceiling hole.
        eye = Vec3(-0.11961226, 10.49493469, -16.62715585)
        direction = Vec3(0.00772557, -0.03588814, 0.99932595).normalize()
        up = Vec3(-0.01373324, 0.99925772, 0.03599186).normalize()
        self.distance = math.dist(eye, (0, 10.0, 7.5))
        self.target = eye + direction * self.distance
        self.reference_orientation = Mat4.look_at(Vec3(0, 0, 0), direction, up)
        self.rotation = (1.0, 0.0, 0.0, 0.0)
        self.tx = 0.0
        self.ty = 0.0

    def project(self, x, y):
        r = 0.6
        d = math.hypot(x, y)
        if d < r / math.sqrt(2):
            z = math.sqrt(r * r - d * d)
        else:
            z = (r * r / 2) / d
        return (x, y, z)

    def rotate(self, x, y, dx, dy, width, height):
        p1 = self.project(
            (width - 2 * (x - dx)) / width,
            (height - 2 * (y - dy)) / height,
        )
        p2 = self.project(
            (width - 2 * x) / width,
            (height - 2 * y) / height,
        )

        axis = (
            p2[1] * p1[2] - p2[2] * p1[1],
            p2[2] * p1[0] - p2[0] * p1[2],
            p2[0] * p1[1] - p2[1] * p1[0],
        )
        length = math.sqrt(sum(v * v for v in axis))

        if length < 1e-8:
            return

        d = math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))
        phi = -5.0 * math.asin(min(1.0, d / 1.2))

        s = math.sin(phi / 2) / length
        q = (
            math.cos(phi / 2),
            axis[0] * s,
            axis[1] * s,
            axis[2] * s,
        )

        a, b = self.rotation, q
        result = (
            a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3],
            a[0] * b[1] + a[1] * b[0] + a[2] * b[3] - a[3] * b[2],
            a[0] * b[2] - a[1] * b[3] + a[2] * b[0] + a[3] * b[1],
            a[0] * b[3] + a[1] * b[2] - a[2] * b[1] + a[3] * b[0],
        )
        norm = math.sqrt(sum(v * v for v in result))
        self.rotation = tuple(v / norm for v in result)

    def move(self, dx, dy):
        self.tx += dx * 0.03
        self.ty += dy * 0.03

    def zoom(self, dy):
        self.distance *= math.exp(-dy * 0.01)
        self.distance = max(5.0, min(150.0, self.distance))

    def view_matrix(self):
        q = Quaternion(*self.rotation)
        return (
            Mat4.from_translation(Vec3(self.tx, self.ty, -self.distance))
            @ self.reference_orientation
            @ Quaternion.to_mat4(q)
            @ Mat4.from_translation(-self.target)
        )
