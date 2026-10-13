import math

from pyglet import gl
from pyglet.math import Vec4


class Mesh:
    def __init__(self, program, positions, shades, indices):
        self.positions = positions
        self.shades = shades
        self.indices = indices
        self.vertices = program.vertex_list_indexed(
            len(shades), gl.GL_TRIANGLES, indices,
            position=("f", positions), shade=("f", shades),
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
            point = model @ Vec4(*source.positions[index:index + 3], 1.0)
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
            ((-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5), 1.0),
            ((0.5, -0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5), (0.5, 0.5, -0.5), 0.63),
            ((-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5), 0.86),
            ((-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, -0.5, 0.5), (-0.5, -0.5, 0.5), 0.48),
            ((0.5, -0.5, 0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, 0.5, 0.5), 0.78),
            ((-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, 0.5, -0.5), 0.72),
        )
        positions, shades, indices = [], [], []
        for face in faces:
            append_quad(positions, shades, indices, face[:4], face[4])
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
                positions, shades, indices,
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


class SphereMesh(Mesh):

    def __init__(self, program, sides=12, stacks=6):
        positions, shades, indices = [], [], []

        def point(latitude, longitude):
            radius = 0.5 * math.cos(latitude)
            return (
                radius * math.cos(longitude),
                0.5 * math.sin(latitude),
                radius * math.sin(longitude),
            )

        for stack in range(stacks):
            low = -math.pi / 2 + math.pi * stack / stacks
            high = -math.pi / 2 + math.pi * (stack + 1) / stacks
            for side in range(sides):
                left = 2 * math.pi * side / sides
                right = 2 * math.pi * (side + 1) / sides
                a, b = point(low, left), point(low, right)
                c, d = point(high, right), point(high, left)
                for triangle in ((a, b, c), (a, c, d)):
                    if stack == 0 and triangle == (a, b, c):
                        continue
                    if stack == stacks - 1 and triangle == (a, c, d):
                        continue
                    center = tuple(sum(vertex[axis] for vertex in triangle) / 3 for axis in range(3))
                    length = math.sqrt(sum(value * value for value in center))
                    light = (0.35 * center[0] + 0.75 * center[1] + 0.55 * center[2]) / length
                    shade = 0.55 + 0.38 * max(0.0, light)
                    start = len(shades)
                    for vertex in triangle:
                        positions.extend(vertex)
                        shades.append(shade)
                    indices.extend((start, start + 1, start + 2))
        super().__init__(program, positions, shades, indices)
