import math

from pyglet import gl
from pyglet.math import Vec4


class Mesh:
    def __init__(self, program, positions, shades, indices):
        self.positions = positions
        self.shades = shades
        self.indices = indices
        self.vertices = program.vertex_list_indexed(
            len(shades),
            gl.GL_TRIANGLES,
            indices,
            position=("f", positions),
            shade=("f", shades),
        )

    def draw(self):
        self.vertices.draw(gl.GL_TRIANGLES)


def bake_static_parts(program, meshes, parts):
    groups = {}
    for part in parts:
        positions, shades, indices = groups.setdefault(part.color, ([], [], []))
        source = meshes[part.mesh]
        offset = len(shades)
        model = part.model()
        for index in range(0, len(source.positions), 3):
            point = model @ Vec4(*source.positions[index : index + 3], 1.0)
            positions.extend(point[:3])
        shades.extend(source.shades)
        indices.extend(offset + index for index in source.indices)
    return tuple((color, Mesh(program, *data)) for color, data in groups.items())


def append_quad(positions, shades, indices, corners, shade):
    start = len(shades)
    for corner in corners:
        positions.extend(corner)
        shades.append(shade)
    indices.extend((start, start + 1, start + 2, start, start + 2, start + 3))


class CubeMesh(Mesh):
    def __init__(self, program):
        faces = (
            (
                (-0.5, -0.5, 0.5),
                (0.5, -0.5, 0.5),
                (0.5, 0.5, 0.5),
                (-0.5, 0.5, 0.5),
                1.0,
            ),
            (
                (0.5, -0.5, -0.5),
                (-0.5, -0.5, -0.5),
                (-0.5, 0.5, -0.5),
                (0.5, 0.5, -0.5),
                0.63,
            ),
            (
                (-0.5, 0.5, 0.5),
                (0.5, 0.5, 0.5),
                (0.5, 0.5, -0.5),
                (-0.5, 0.5, -0.5),
                0.86,
            ),
            (
                (-0.5, -0.5, -0.5),
                (0.5, -0.5, -0.5),
                (0.5, -0.5, 0.5),
                (-0.5, -0.5, 0.5),
                0.48,
            ),
            (
                (0.5, -0.5, 0.5),
                (0.5, -0.5, -0.5),
                (0.5, 0.5, -0.5),
                (0.5, 0.5, 0.5),
                0.78,
            ),
            (
                (-0.5, -0.5, -0.5),
                (-0.5, -0.5, 0.5),
                (-0.5, 0.5, 0.5),
                (-0.5, 0.5, -0.5),
                0.72,
            ),
        )
        positions, shades, indices = [], [], []
        for face in faces:
            append_quad(positions, shades, indices, face[:4], face[4])
        super().__init__(program, positions, shades, indices)


class RoundedBoxMesh(Mesh):

    def __init__(self, program, dimensions=(5.0, 2.78, 5.02), radius=1.3, segments=20):
        positions, shades, indices = [], [], []
        half = tuple(dimension / 2 for dimension in dimensions)
        core = tuple(value - radius for value in half)
        light = (0.3, 0.75, 0.55)
        light_length = math.sqrt(sum(value * value for value in light))
        light = tuple(value / light_length for value in light)

        faces = (
            (0, -1, 1, 2),
            (0, 1, 1, 2),
            (1, -1, 0, 2),
            (1, 1, 0, 2),
            (2, -1, 0, 1),
            (2, 1, 0, 1),
        )

        def rounded_point(point):
            physical = tuple(point[axis] * dimensions[axis] for axis in range(3))
            closest = tuple(
                max(-core[axis], min(core[axis], physical[axis])) for axis in range(3)
            )
            delta = tuple(physical[axis] - closest[axis] for axis in range(3))
            length = math.sqrt(sum(value * value for value in delta))
            if length > 1e-8:
                normal = tuple(value / length for value in delta)
                physical = tuple(
                    closest[axis] + radius * normal[axis] for axis in range(3)
                )
            else:
                normal = tuple(
                    1.0 if abs(point[axis]) > 0.499 else 0.0 for axis in range(3)
                )
            normalized = tuple(physical[axis] / dimensions[axis] for axis in range(3))
            shade = 0.58 + 0.38 * max(
                0.0, sum(normal[axis] * light[axis] for axis in range(3))
            )
            return normalized, shade

        for axis, sign, u_axis, v_axis in faces:
            for row in range(segments):
                v0 = -0.5 + row / segments
                v1 = -0.5 + (row + 1) / segments
                for column in range(segments):
                    u0 = -0.5 + column / segments
                    u1 = -0.5 + (column + 1) / segments
                    corners = []
                    for u, v in ((u0, v0), (u1, v0), (u1, v1), (u0, v1)):
                        point = [0.0, 0.0, 0.0]
                        point[axis] = sign * 0.5
                        point[u_axis] = u
                        point[v_axis] = v
                        corners.append(rounded_point(point))

                    start = len(shades)
                    for point, shade in corners:
                        positions.extend(point)
                        shades.append(shade)
                    indices.extend(
                        (start, start + 1, start + 2, start, start + 2, start + 3)
                    )

        super().__init__(program, positions, shades, indices)


class RoundedBoxSeamMesh(Mesh):
    """A thin strip following the middle perimeter of a rounded box."""

    def __init__(
        self,
        program,
        dimensions=(5.0, 2.78, 5.02),
        radius=1.3,
        seam_width=0.055,
        seam_height=0.15,
        segments=40,
        surface_offset=0.006,
    ):
        positions, shades, indices = [], [], []
        half = tuple(dimension / 2 for dimension in dimensions)
        core = tuple(value - radius for value in half)

        def surface_point(point, side_axis, side_sign):
            physical = tuple(point[axis] * dimensions[axis] for axis in range(3))
            closest = tuple(
                max(-core[axis], min(core[axis], physical[axis])) for axis in range(3)
            )
            delta = tuple(physical[axis] - closest[axis] for axis in range(3))
            length = math.sqrt(sum(value * value for value in delta))
            if length > 1e-8:
                normal = tuple(value / length for value in delta)
                physical = tuple(
                    closest[axis] + radius * normal[axis] for axis in range(3)
                )
            else:
                normal = tuple(
                    side_sign if axis == side_axis else 0.0 for axis in range(3)
                )

            physical = tuple(
                physical[axis] + surface_offset * normal[axis] for axis in range(3)
            )
            return tuple(physical[axis] / dimensions[axis] for axis in range(3))

        for side_axis in (0, 2):
            along_axis = 2 if side_axis == 0 else 0
            low_y = (seam_height - seam_width / 2) / dimensions[1]
            high_y = (seam_height + seam_width / 2) / dimensions[1]
            for side_sign in (-1, 1):
                for step in range(segments):
                    along0 = -0.5 + step / segments
                    along1 = -0.5 + (step + 1) / segments
                    corners = []
                    for along, y in (
                        (along0, low_y),
                        (along0, high_y),
                        (along1, high_y),
                        (along1, low_y),
                    ):
                        point = [0.0, 0.0, 0.0]
                        point[side_axis] = side_sign * 0.5
                        point[along_axis] = along
                        point[1] = y
                        corners.append(surface_point(point, side_axis, side_sign))

                    start = len(shades)
                    for point in corners:
                        positions.extend(point)
                        shades.append(0.95)
                    indices.extend(
                        (start, start + 1, start + 2, start, start + 2, start + 3)
                    )

        super().__init__(program, positions, shades, indices)


class CylinderMesh(Mesh):

    def __init__(self, program, sides=12):
        positions, shades, indices = [], [], []
        for index in range(sides):
            a = 2.0 * math.pi * index / sides
            b = 2.0 * math.pi * (index + 1) / sides
            x0, z0 = 0.5 * math.cos(a), 0.5 * math.sin(a)
            x1, z1 = 0.5 * math.cos(b), 0.5 * math.sin(b)
            light = 0.5 * math.cos((a + b) / 2) + 0.7 * math.sin((a + b) / 2)
            shade = 0.67 + 0.22 * light
            append_quad(
                positions,
                shades,
                indices,
                ((x0, -0.5, z0), (x1, -0.5, z1), (x1, 0.5, z1), (x0, 0.5, z0)),
                shade,
            )
            for y, cap_shade in ((0.5, 0.95), (-0.5, 0.49)):
                start = len(shades)
                for vertex in ((0.0, y, 0.0), (x0, y, z0), (x1, y, z1)):
                    positions.extend(vertex)
                    shades.append(cap_shade)
                indices.extend((start, start + 1, start + 2))
        super().__init__(program, positions, shades, indices)
