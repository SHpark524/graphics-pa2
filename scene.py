
from dataclasses import dataclass

from pyglet.math import Mat4, Vec3


BOX_WIDTH = 20.0
BOX_HEIGHT = 25.0
BOX_DEPTH = 15.0

WALL_THICKNESS = 0.2

WHITE = (1.0, 1.0, 1.0)
RED = (1.0, 0.0, 0.0)
GREEN = (0.0, 1.0, 0.0)


@dataclass
class Part:
    center: tuple[float, float, float]
    size: tuple[float, float, float]
    color: tuple[float, float, float]

    def model(self) -> Mat4:
        translation = Mat4.from_translation(
            Vec3(*self.center)
        )
        scaling = Mat4.from_scale(
            Vec3(*self.size)
        )
        return translation @ scaling


def build_scene() -> list[Part]:
    w = BOX_WIDTH
    h = BOX_HEIGHT
    d = BOX_DEPTH
    t = WALL_THICKNESS

    return [
        # Floor
        Part(
            center=(0, -t / 2, d / 2),
            size=(w, t, d),
            color=WHITE,
        ),

        # Back wall
        Part(
            center=(0, h / 2, d + t / 2),
            size=(w, h, t),
            color=WHITE,
        ),

        # Right wall
        Part(
            center=(-w / 2 - t / 2, h / 2, d / 2),
            size=(t, h, d),
            color=GREEN,
        ),

        # Left wall
        Part(
            center=(w / 2 + t / 2, h / 2, d / 2),
            size=(t, h, d),
            color=RED,
        ),

        # Ceiling
        Part(
            center=(0, h + t / 2, d / 2),
            size=(w, t, d),
            color=WHITE,
        ),
    ]
